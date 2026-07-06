import streamlit as st
from datetime import datetime
from utils.constants import padding1
from utils.shasha import shashasha
from utils.merkle import gerar_raiz_merkle

def page_ledger() -> None:

    """
    Displays the ledger in a Streamlit app.
    Returns:
        None: This function does not return any value. It directly renders the ledger 
        in the Streamlit app.
    """

    ledger: list[dict] = st.session_state["ledger"]

    st.title("Ledger")

    tabs = st.tabs([f"Bloco {i}" for i, _ in enumerate(ledger)])
    for i, (tab, bloco) in enumerate(zip(tabs, ledger)):
        with tab:
            st.subheader("Version")
            st.write(f"{bloco['versao']}")

            st.divider()

            st.subheader("Difficulty")
            st.write(f"{bloco['dificuldade']}")

            st.divider()

            st.subheader("Hash of previous block")
            if i == 0:
                hash_anterior = bloco['hash_bloco_anterior']
            st.write(f"{hash_anterior}")

            st.divider()

            st.subheader("Hash of merkle root")
            hash_raiz_merkle = gerar_raiz_merkle(bloco['transacoes'])
            st.write(f"{hash_raiz_merkle}")

            st.divider()

            st.subheader("Timestamp")
            st.write(f"{bloco['timestamp']} ({datetime.fromtimestamp(bloco['timestamp']).strftime('%Y-%m-%d %H:%M:%S')})")

            st.divider()

            st.subheader("Nonce")
            st.write(f"{bloco['nonce']}")

            st.divider()

            st.subheader("Target")
            st.write(f"{bloco['target']}")

            st.divider()

            if not bloco['transacoes'][-1].get("minerador") is None:
                st.subheader("Miner")
                st.write(f"{bloco['transacoes'][-1]['minerador']}")            

                st.divider()

            st.subheader("Hash of current block")
            header = f"{bloco['versao']:032b}" \
                     f"{int(hash_anterior, 16):0256b}" \
                     f"{int(hash_raiz_merkle, 16):0256b}" \
                     f"{bloco['timestamp']:032b}" \
                     f"{bloco['target']:032b}" \
                     f"{bloco['nonce']:032b}" \
                     f"{padding1}"

            hash_final = shashasha(header)
            if hash_final[:bloco["dificuldade"]] == "0" * bloco["dificuldade"]:
                st.success(f"{hash_final}")
            else:
                st.error(f"{hash_final}")
            
            hash_anterior = hash_final

