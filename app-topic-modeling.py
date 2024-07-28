import streamlit as st

import os
import json

from openai import OpenAI

OPENAI_API_KEY = os.getenv('OPENAI_TOKEN')

client = OpenAI(api_key=OPENAI_API_KEY)

def classificar_texto_openai(texto):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Você é um modelo de classificação de texto no contexto de reclamações \
                            de um setor financeiro, gostaria que classificasse o texto abaixo entre \
                            as categorias: \
                                'Serviços de conta bancária', \
                                'Cartão de crédito / Cartão pré-pago', \
                                'Roubo / Relatório de disputa', \
                                'Hipotecas / Empréstimos' e \
                                'Outros'. \
                            O resultado gostaria que seguisse o template de output:\
                                {"'"texto"'": <'texto original do imput'>, "'"categoria"'": <'categoria classificada pelo chatgpt'>}."
            },
            {
                "role": "user",
                "content": "Texto: '" + texto + "'"
            }
        ]
    )

    retorno = response.choices[0].message.content
    json_resposta =  json.loads(retorno)
    return json_resposta['categoria']

# Aplicação streamlit com um campo de texto e um botão de validar
st.title("Classificação de texto com OpenAI")
st.write("Possíveis categorias:")
st.write('- Serviços de conta bancária')
st.write('- Cartão de crédito / Cartão pré-pago')
st.write('- Roubo / Relatório de disputa')
st.write('- Hipotecas / Empréstimos')
st.write('- Outros')

texto = st.text_area("Digite o texto que deseja classificar:")
botao = st.button("Classificar")

if botao:
    categoria = classificar_texto_openai(texto)
    st.write(f"O texto foi classificado na categoria: {categoria}")
