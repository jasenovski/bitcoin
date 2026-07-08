from utils.merkle import gerar_raiz_merkle
import requests
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
    checagem_hash = checar_hash_final(bloco["versao"], bloco["hash_bloco_anterior"], 
                                      bloco["hash_raiz_merkle"], bloco["timestamp"], 
                                      bloco["target"], bloco["nonce"], bloco["hash_final"])
    checagem_transacoes = checar_transacoes(bloco["transacoes"])

    return checagem_hash, checagem_merkle, checagem_transacoes

def escrever_bloco(bloco: dict, ledger: list[dict]) -> None:

    """
    Função que escreve o bloco no ledger.

    Args:
        bloco (dict): Dicionário contendo as informações do bloco.
        ledger (list): Lista de blocos do ledger.
    """

    ledger.append(bloco)

    with open("ledger/ledger.json", "w") as file:
        jdump(ledger, file, indent=4)
    
    return ledger

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

def checar_maior_ledger():
    """
    Função que checa qual é o maior ledger entre os peers, e salva a maior ledger no 
    arquivo ledger.json.
    """

    todas_configs = []
    for caminho_configs in glob("configs/configuracoes*.json"):
        with open(caminho_configs, "r", encoding="utf-8") as arquivo:
            configs = jload(arquivo)[0]
        
        todas_configs.append(configs)

    todas_ledgers = {}
    for caminho_ledger in glob("ledgers/ledger*.json"):
        with open(caminho_ledger, "r", encoding="utf-8") as arquivo:
            ledger = jload(arquivo)
        
        peer = caminho_ledger.split("\\")[-1].split(".")[0].split("_")[-1]
        todas_ledgers[peer] = ledger

    maiores_ledgers = {}
    for peer, ledger in todas_ledgers.items():
        tamanho = 1
        for bloco in ledger[1:]:
            response = requests.put(f"http://localhost:5000/check_mining", json=bloco)
            if response.json()["code"] == 400 and \
                response.json()["checagem_hash"] == False and \
                    response.json()["checagem_merkle"] == False:
                break
            else:
                versao: int = bloco["versao"]
                hash_final: str = bloco["hash_final"]
                ganho = bloco["transacoes"][-3]["valor"]

                configs = [config for config in todas_configs if config["versao"] == versao][0]
                dificuldade = configs["dificuldade"]
                target = configs["target"]
                recompensa = configs["recompensa"]

                if hash_final.startswith("0" * dificuldade) and \
                    int(hash_final[48:56], 16) <= target and \
                        ganho == recompensa:
                    tamanho += 1
        
        maiores_ledgers[peer] = tamanho

    peer_vencedor = max(maiores_ledgers, key=maiores_ledgers.get)
    ledger_vencedor = todas_ledgers[peer_vencedor]

    with open(f"ledger/ledger.json", "w", encoding="utf-8") as arquivo:
        jdump(ledger_vencedor, arquivo, indent=4, ensure_ascii=False)
    
    return peer_vencedor
