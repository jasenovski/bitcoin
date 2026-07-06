import streamlit as st

def page_transacoes() -> None:
    """
    Displays the transactions in a Streamlit app.
    Returns:
        None: This function does not return any value. It directly renders the transactions
        in the Streamlit app.
    """

    ledger: list[dict] = st.session_state["ledger"]

    st.title("Transações")

    tabs = st.tabs([f"Bloco {i}" for i, _ in enumerate(ledger)])
    for tab, bloco in zip(tabs, ledger):
        with tab:
            for transacao in bloco["transacoes"]:
                
                st.divider()
                st.write(transacao)