# Introdução

Projeto final da disciplina de COGNITIVE ENVIRONMENTS da turma 5DTSR.

Esse projeto possuí duas aplicações:
- [app-liveness.py](app-liveness.py) - App de Liveness Detection utilizando AWS e OpenAI para validação de vivacidade.
- [app-topic-modeling.py](app-topic-modeling.py) - App de Topic Modeling utilizando a OpenAI para classificação dos chamados

Mesmo sendo apenas um dos modelos propostos obrigatório, optamos por fazer ambos acima.

# Como rodar o projeto

1) Instalar as dependências do **[requirements.txt](requirements.txt)**
2) Duplicar o arquivo **[.streamlit/secrets-sample.toml](.streamlit/secrets-sample.toml)**
para **.stremlit/secrets.toml** e substituir o conteúdo pelos seus tokens na AWS e OpenAI
3) Executar a aplicação desejada com os comandos abaixo.

```
streamlit run app-liveness.py
```

ou

```
streamlit run app-topic-modeling.py
```

# Versão do Python utilizada

Foi utilizada durante o desenvolvimento a versão 3.12.4 do Python.