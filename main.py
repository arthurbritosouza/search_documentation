import streamlit as st
from check import main

st.header('🤖 Documentations', anchor="top", help="Interaja com o chatbot!")

if 'mensagens' not in st.session_state:
    st.session_state.mensagens = []
if 'documentacao' not in st.session_state:
    st.session_state.documentacao = ""
if 'chat_ativo' not in st.session_state:
    st.session_state.chat_ativo = False

def exibir_chat():
    for mensagem in st.session_state.mensagens:
        chat = st.chat_message(mensagem['role'])
        chat.markdown(mensagem['content'])

documentacao_input = st.text_input("Insira o link da documentação:", value=st.session_state.documentacao)

if documentacao_input != st.session_state.documentacao:
    st.session_state.documentacao = documentacao_input

exibir_chat()

prompt = st.chat_input("Say something")
if prompt:
    st.session_state.chat_ativo = True

if st.session_state.chat_ativo and prompt:
    response = main(st.session_state.documentacao, prompt)

    st.session_state.mensagens.append({'role': 'user', 'content': prompt})

    st.session_state.mensagens.append({'role': 'assistant', 'content': f"Chatbot respondeu: {response}"})

    exibir_chat()
