from datetime import datetime
from utils.merkle import gerar_raiz_merkle
from models.sha_bitcoin import sha_256_btc
from utils.constants import padding1, padding2
import requests

def minerar(
            PEER: str,
            versao: int, 
            hash_bloco_anterior: str, 
            transacoes: list[dict], 
            target: int, 
            dificuldade: int = 2) -> tuple[str, str]:
    
    """
    Função que realiza a mineração de um bloco.

    Args:
        PEER (str): Endereço do peer para verificar o ledger.
        versao (int): Versão do bloco.
        hash_bloco_anterior (str): Hash hexadecimal do bloco anterior.
        transacoes (list[dict]): Lista de transações a serem incluídas no bloco.
        target (int): Valor do target para a mineração.
        dificuldade (int, optional): Número de zeros à esquerda que o hash final deve ter. Defaults to 2.
    
    Returns:
        tuple: Retorna uma tupla contendo o hash (hexadecimal) final do bloco e o header (binário) do bloco
    """

    print("Iniciando mineração...")
    versao = f"{versao:032b}"
    target = f"{target:032b}"
    hash_raiz_merkle = gerar_raiz_merkle(transacoes)
    hash_raiz_merkle_bin = f"{int(hash_raiz_merkle, 16):0256b}"
    hash_bloco_anterior = f"{int(hash_bloco_anterior, 16):0256b}"
    qtd_hashes = 0
    datetime_inicio = datetime.now()
    voltas_nonce = 0
    flag = False

    while True:
        for i, nonce in enumerate(range(2 ** 32 - 1)):

            if i % 1_000 == 0:
                ledger: list[dict] = requests.get(f"{PEER}/get_ledger").json()
                ultimas_transacoes = ledger[-1]["transacoes"]
                if ultimas_transacoes[:-3] == transacoes[:-3]:
                    print("Transações já foram mineradas por outro peer")
                    exit()

            nonce_bin = f"{nonce:032b}"
            timestamp = f"{int(datetime.now().timestamp()):032b}"
            header1 = versao + hash_bloco_anterior + hash_raiz_merkle_bin + timestamp + target + nonce_bin + padding1

            if nonce == 0:
                sha0 = sha_256_btc(header1[:512])

            sha1 = sha_256_btc(header1[512:], hash_anterior=sha0)
            header2 = f"{int(sha1, 16):0256b}" + padding2
            sha2 = sha_256_btc(header2)

            qtd_hashes += 1

            try:
                hash_rate = qtd_hashes / (datetime.now() - datetime_inicio).total_seconds()
            except ZeroDivisionError:
                hash_rate = 0

            print(f"Nonce: {nonce:06d}  |  Hash rate: {hash_rate:.2f} H/s", end="\r")

            if sha2[:dificuldade] == "0" * dificuldade and int(sha2[48:48 + 8], 16) < int(target, 2):
                flag = True
                break
        
        if flag is True:
            break

        voltas_nonce += 1
        transacoes[-2]["voltas_nonce"] = voltas_nonce
        hash_raiz_merkle = gerar_raiz_merkle(transacoes)
        hash_raiz_merkle_bin = f"{int(hash_raiz_merkle, 16):0256b}"

    print(f"Mineração finalizada! Nonce Final: {nonce} |  Hash rate: {hash_rate:.2f} H/s")

    return sha2, header1
