import streamlit as st
import boto3
from PIL import Image
import base64
import io
import os
import openai

# Configurações da AWS
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION_NAME = os.getenv('AWS_REGION', 'us-east-2')

# Configuração da OpenAI
openai.api_key = os.getenv('OPENAI_TOKEN')

# Função para detectar faces e objetos na imagem usando Amazon Rekognition
def detectar_faces_e_objetos(image_bytes):
    cliente = boto3.client('rekognition',
                           aws_access_key_id=AWS_ACCESS_KEY,
                           aws_secret_access_key=AWS_SECRET_KEY,
                           region_name=REGION_NAME)

    resposta = cliente.detect_labels(Image={'Bytes': image_bytes}, MaxLabels=10, MinConfidence=75)
    resposta_face = cliente.detect_faces(Image={'Bytes': image_bytes}, Attributes=['ALL'])

    etiquetas = resposta['Labels']
    detalhes_face = resposta_face['FaceDetails']

    return etiquetas, detalhes_face

# Função para verificar se a imagem é válida
def imagem_valida(etiquetas, detalhes_face):
    quantidade_faces = len(detalhes_face)

    # Verificar se há exatamente um rosto
    if quantidade_faces > 1:
        return False, 'Mais de um rosto detectado.'

    if quantidade_faces < 1:
        return False, 'Nenhum rosto detectado.'

    # Verificar se há dispositivos ou partes do corpo (mãos, dedos)
    for etiqueta in etiquetas:
        if etiqueta['Name'] in ['Hand', 'Finger']:
            return False, 'Partes do corpo detectados.'

        if etiqueta['Name'] in ['Cell Phone', 'Tablet', 'Mobile Phone']:
            return False, 'Dispositivos detectados.'

        if etiqueta['Name'] in ['Paper', 'Letter', 'Photograph']:
            return False, 'Papéis ou fotos detectados.'

    return True, None

# Função para enviar a imagem para a OpenAI e obter uma descrição
def obter_descricao_openai(image_base64):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Responda exatamente com apenas 'sim' ou 'não' em minúsculo e sem pontuação \
                                se a imagem é uma foto de uma foto ou foto de um dispositivo móvel ou \
                                qualquer outra tentativa de burlar o sistema da câmera. \
                                Fique atento à reflexos, riscos, listras de tela, iluminação, sombras, \
                                baixa qualidade da imagem ou bordas dos elementos."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}",
                            "detail": "high"
                        },
                    },
                ],
            }
        ],
        max_tokens=10,
    )
    return response.choices[0].message.content

# Interface do Streamlit
st.title('Verificação de segurança')

st.header('Instruções:')
st.write('1. Fique em um local iluminado e sem outras pessoas presentes na imagem.')
st.write('2. Deixe somente sua face aparecendo na imagem. Evite mãos, dedos, ou outros elementos.')

# Captura de imagem com camera_input
captura = st.camera_input("Capture uma imagem")

if captura is not None:
    # Converter a imagem capturada em bytes
    imagem = Image.open(captura)
    st.image(imagem, caption='Imagem capturada.', use_column_width=True)

    img_byte_arr = io.BytesIO()
    imagem.save(img_byte_arr, format='PNG')
    image_bytes = img_byte_arr.getvalue()

     # Converter a imagem para Base64
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

     # Obter descrição da OpenAI
    descricao = obter_descricao_openai(image_base64)
    if descricao == 'sim':
        st.error('A imagem é uma foto de uma foto ou de um dispositivo móvel. \
                 Por favor, tire outra foto.')
        st.stop()

    # Detecção de faces e objetos
    etiquetas, detalhes_face = detectar_faces_e_objetos(image_bytes)

    # Verificação da validade da imagem
    resultado, motivo = imagem_valida(etiquetas, detalhes_face)
    if resultado:
        st.success('A imagem é válida: apenas um rosto detectado e nenhum dispositivo \
                   ou parte do corpo encontrado.')
    else:
        st.error(f'A imagem não é válida: {motivo}.')
