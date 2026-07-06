import streamlit as st
from json import load
from pgs.pg_ledger import page_ledger
from pgs.pg_transacoes import page_transacoes
from pgs.pg_gerar_transacoes import page_gerar_transacoes

pages = {
    "Ledger": page_ledger,
    "Transações": page_transacoes,
    "Gerar Transações": page_gerar_transacoes
    }

def main():
    st.sidebar.title("Menu")
    menu = st.sidebar.radio(label="Selecione uma opção", 
                            options=list(pages.keys()), 
                            index=0)

    with open('ledger/ledger.json') as json_file:
        ledger = load(json_file)
    
    st.session_state["ledger"] = ledger
    pages[menu]()

if __name__ == "__main__":
    main()