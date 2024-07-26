import streamlit as st
import cv2
import time
import boto3
import os
import uuid

# Obter credenciais da AWS das variáveis de ambiente
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_session_token = os.getenv('AWS_SESSION_TOKEN')  # se estiver usando credenciais temporárias

# Configurar clientes S3 e Rekognition
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token
)

rekognition = boto3.client(
    'rekognition',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token
)

st.title("Captura de Vídeo")

# Configurar captura de vídeo
video_capture = cv2.VideoCapture(0)
frame_width = int(video_capture.get(3))
frame_height = int(video_capture.get(4))
fps = 15  # Taxa de quadros mínima
duracao = 5  # Duração mínima em segundos
frame_count = fps * duracao

# Configurar vídeo writer
unique_filename = str(uuid.uuid4()) + '.mp4'
video_writer = cv2.VideoWriter(unique_filename, cv2.VideoWriter_fourcc(*'MP4V'), fps, (frame_width, frame_height))

frame_placeholder = st.empty()

# Capturar vídeo por 5 segundos
frames_capturados = 0

while frames_capturados < frame_count:
    ret, frame = video_capture.read()
    if not ret:
        st.error("Não foi possível capturar o vídeo.")
        break

    frame_placeholder.image(frame, channels="BGR")
    video_writer.write(frame)
    frames_capturados += 1

    if st.button("Parar Captura"):
        break

video_capture.release()
video_writer.release()
cv2.destroyAllWindows()

st.success("Vídeo capturado com sucesso!")

# Carregar o vídeo salvo para o S3
bucket_name = 'seu-bucket'
s3.upload_file(unique_filename, bucket_name, unique_filename)

# Chamar o serviço de detecção de objetos do Rekognition para verificar presença de celulares e mãos
response = rekognition.detect_labels(
    Image={'S3Object': {'Bucket': bucket_name, 'Name': unique_filename}},
    MaxLabels=10,
    MinConfidence=80
)

# Verificar se há celulares ou mãos na imagem
fraude_detectada = False
objetos_detectados = []

for label in response['Labels']:
    if label['Name'].lower() in ['cell phone', 'hand']:
        fraude_detectada = True
        objetos_detectados.append(label['Name'])

if fraude_detectada:
    st.error(f"Fraude detectada: {', '.join(objetos_detectados)} presentes na imagem.")
else:
    # Chamar o serviço Face Liveness do Rekognition
    response = rekognition.start_face_liveness_session(
        Video={'S3Object': {'Bucket': bucket_name, 'Name': unique_filename}},
        ClientRequestToken='token-unico'
    )

    session_id = response['SessionId']

    # Obter o resultado da verificação
    while True:
        result = rekognition.get_face_liveness_session_results(SessionId=session_id)
        if result['Status'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(5)

    if result['Status'] == 'COMPLETED':
        if result['Confidence'] >= 90:  # Defina o limiar de confiança
            st.success("Verificação de liveness bem-sucedida!")
        else:
            st.error("Verificação de liveness falhou.")
    else:
        st.error("Verificação de liveness falhou.")

# Excluir o arquivo de vídeo local após o processamento
if os.path.exists(unique_filename):
    os.remove(unique_filename)

# Excluir o arquivo de vídeo do S3 após o processamento
try:
    s3.delete_object(Bucket=bucket_name, Key=unique_filename)
    st.success("Arquivo de vídeo excluído do S3 com sucesso.")
except Exception as e:
    st.error(f"Erro ao excluir arquivo do S3: {e}")
