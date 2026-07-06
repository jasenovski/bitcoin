from utils.merkle import gerar_raiz_merkle
from models.sha_bitcoin import sha_256_btc
from glob import glob
from json import load as jload, dump as jdump
from shutil import move
from os import sep, path
from pickle import load as pload, dump as pdump
from datetime import datetime
from utils.constants import padding1
from utils.shasha import shashasha

def checar_hash_final(versao: int, 
                      hash_anterior: str, 
                      root_merkle: str, 
                      timestamp: int, 
                      target: int, 
                      nonce: int, 
                      hash_final: str):
    
    """
    Função que checa se o hash final do bloco é válido.

    Args:
        versao (int): Versão do bloco.
        hash_anterior (str): Hash do bloco anterior.
        root_merkle (str): Hash da raiz Merkle.
        timestamp (int): Timestamp do bloco.
        target (int): Target do bloco.
        nonce (int): Nonce do bloco.
        hash_final (str): Hash final do bloco.

    Returns:
        bool: True se o hash final for válido, False caso contrário.
    """

    versao = f"{versao:032b}"
    hash_anterior = f"{int(hash_anterior, 16):0256b}"
    root_merkle = f"{int(root_merkle, 16):0256b}"
    timestamp = f"{timestamp:032b}"
    target = f"{target:032b}"
    nonce = f"{nonce:032b}"

    header = versao + hash_anterior + root_merkle + timestamp + target + nonce + padding1
    sha2 = shashasha(header)

    return sha2 == hash_final

def checar_hash_merkle(transacoes: list[dict], 
                       hash_merkle: str) -> bool:
    
    """
    Função que checa se o hash da raiz Merkle é válido.

    Args:
        transacoes (list): Lista de transações do bloco.
        hash_merkle (str): Hash da raiz Merkle.

    Returns:
        bool: True se o hash da raiz Merkle for válido, False caso contrário.
    """

    return gerar_raiz_merkle(transacoes) == hash_merkle

def checar_transacoes(transacoes_checar: list[dict]) -> bool:

    """
    Função que checa se as transações do bloco são válidas.

    Args:
        transacoes_checar (list): Lista de transações do bloco.
    """

    transacoes_checar_copy = transacoes_checar.copy()

    del transacoes_checar_copy[-1]
    del transacoes_checar_copy[-1]
    del transacoes_checar_copy[-1]

    arquivos_transacoes = glob("transacoes_minerar/*.json")
    for arquivo_transacoes in arquivos_transacoes:
        with open(arquivo_transacoes, "r") as file:
            transacoes = jload(file)

        if transacoes == transacoes_checar_copy:
            return True

    return False

def checagem(bloco: dict) -> bool:

    """
    Função que realiza a checagem do bloco.

    Args:
        bloco (dict): Dicionário contendo as informações do bloco.

    Returns:
        bool: True se o bloco for válido, False caso contrário.
    """

    checagem_merkle = checar_hash_merkle(bloco["transacoes"], bloco["hash_raiz_merkle"])
    checagem_hash = checar_hash_final(bloco["versao"], bloco["hash_bloco_anterior"], bloco["hash_raiz_merkle"], bloco["timestamp"], bloco["target"], bloco["nonce"], bloco["hash_final"])
    checagem_transacoes = checar_transacoes(bloco["transacoes"])

    return checagem_hash and checagem_merkle and checagem_transacoes

def escrever_bloco(bloco: dict) -> None:

    """
    Função que escreve o bloco no ledger.

    Args:
        bloco (dict): Dicionário contendo as informações do bloco.
    """

    with open("ledger/ledger.json", "r") as file:
        ledger: list[dict] = jload(file)

    bloco = {
        "versao": bloco["versao"],
        "dificuldade": bloco["dificuldade"],
        "target": bloco["target"],
        "nonce": bloco["nonce"],
        "timestamp": bloco["timestamp"],
        "hash_bloco_anterior": bloco["hash_bloco_anterior"],
        "hash_raiz_merkle": bloco["hash_raiz_merkle"],
        "transacoes": bloco["transacoes"],
        "hash_final": bloco["hash_final"]
    }

    ledger.append(bloco)

    with open("ledger/ledger.json", "w") as file:
        jdump(ledger, file, indent=4)

def mover_transacoes(transacoes_checar: list[dict]) -> None:

    """
    Função que move as transações do bloco para a pasta de transações mineradas.

    Args:
        transacoes_checar (list): Lista de transações do bloco.
    """

    transacoes_checar_copy = transacoes_checar.copy()
    del transacoes_checar_copy[-1]
    del transacoes_checar_copy[-1]
    del transacoes_checar_copy[-1]

    arquivos_transacoes = glob("transacoes_minerar/*.json")
    for arquivo_transacoes in arquivos_transacoes:
        with open(arquivo_transacoes, "r") as file:
            transacoes = jload(file)

        if transacoes == transacoes_checar_copy:
            move(arquivo_transacoes, path.join("transacoes_mineradas", f"{arquivo_transacoes.split(sep)[-1]}"))

def adicionar_transacao(transacao: dict) -> None:
    """
    Função que adiciona uma transação ao arquivo de transações.
    Args:
        transacao (dict): Dicionário contendo as informações da transação.
    """

    with open('transacoes.pkl', 'rb') as f:
        transacoes: list = pload(f)

    transacoes.append(transacao)

    with open('transacoes.pkl', 'wb') as f:
        pdump(transacoes, f)

def fechar_transacoes(transacoes: list[dict]) -> None:
    """
    Função que fecha as transações do bloco, salvando-as em um arquivo JSON e 
    limpando o arquivo de transações.
    Args:
        transacoes (list): Lista de transações do bloco.
    """

    date_hour = datetime.now().strftime("%d-%m-%Y %H%M%S")

    with open(path.join("transacoes_minerar", f"transacoes_{date_hour}.json"), 'w') as file:
        jdump(transacoes, file, indent=4)

    
    with open('transacoes.pkl', 'wb') as f:
        pdump([], f)
