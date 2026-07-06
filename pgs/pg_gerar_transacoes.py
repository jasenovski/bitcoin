import streamlit as st
from pickle import load
from time import sleep
from utils.utils import adicionar_transacao
from utils.fechar_transacoes import fechar_pool

def page_gerar_transacoes():

    with open('transacoes.pkl', 'rb') as f:
        transacoes = load(f)
    
    placeholder = st.empty()

    with placeholder.form(key='form', clear_on_submit=True):
    
        st.subheader('Gerar transação')
        de = st.text_input('De', placeholder='Digite o nome do remetente')
        para = st.text_input('Para', placeholder='Digite o nome do destinatário')
        valor = st.number_input('Valor', min_value=10, value=50, step=5, format='%d', help='Valor mínimo de 10')

        botao = st.form_submit_button('Inserir transação')
        if botao:
            
            if de == "":
                st.error('O campo "De" não pode ser vazio!')
                return
            
            if para == "":
                st.error('O campo "Para" não pode ser vazio!')
                return            
            
            transacao = {
                'de': de,
                'para': para,
                'valor': float(valor)
            }
            
            adicionar_transacao(transacao)
            
            st.success('Transação em espera para mineração!')
            sleep(1)
            st.rerun()
            placeholder.empty()

    qtd_transacoes = len(transacoes)
    forma = 'transação aberta' if qtd_transacoes == 1 else 'transações abertas'
    st.sidebar.subheader(f'Liberar {qtd_transacoes} {forma} para mineração')
    st.sidebar.button('Fechar transações', on_click=fechar_pool)
