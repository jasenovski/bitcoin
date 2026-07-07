import requests
from models.minerar import minerar
from platform import node
from socket import gethostbyname, gethostname
from datetime import datetime
from json import load, dump

def check_ledger_exists():
    try:
        with open('ledger/ledger.json') as json_file:
            ledger = load(json_file)
    except FileNotFoundError:
        ledger = requests.get(f"{PEER}/get_ledger").json()
        with open("ledger/ledger.json", "w") as file:
            dump(ledger, file, indent=4)

check_ledger_exists()

start_time = datetime.now()

try:
    localhost = gethostbyname(gethostname())
except:
    localhost = ""

ip_peer = input(f"Digite o IP do peer [{localhost}]: ")
if ip_peer == "":
    ip_peer = localhost

port_peer = input("Digite a porta do peer [5000]: ")
if port_peer == "":
    port_peer = 5000

PEER = f"http://{ip_peer}:{port_peer}"
MINERADOR = node()

configs: dict = requests.get(f"{PEER}/get_configs").json()[0]
transacoes: list[dict] = requests.get(f"{PEER}/get_transacoes").json()
ultimo_bloco: dict = requests.get(f"{PEER}/get_ledger").json()[-1]

with open('configs/configuracoes.json') as json_file:
    versao_atual = load(json_file)[0]["versao"]

if versao_atual != configs["versao"]:
    print(f"Versão do peer diferente da versão local. Versão do peer: {configs['versao']} | Versão local: {versao_atual}")
    print("Atualize a versão local para continuar minerando usando 'git pull'")
    exit()

if not transacoes[0].get("code", None) is None:
    print("Não há transações para minerar")
    exit()
else:
    transacoes.append({"de": "rede", "para": MINERADOR, "valor": float(configs["recompensa"])})
    transacoes.append({"voltas_nonce": 0})
    transacoes.append({"minerador": MINERADOR})


versao = configs["versao"]
hash_bloco_anterior = ultimo_bloco["hash_final"]
target = configs["target"]
dificuldade = configs["dificuldade"]

sha2, header = minerar(PEER, versao, hash_bloco_anterior, transacoes, target, dificuldade)

nonce = int(header[32 + 256 + 256 + 32 + 32:32 + 256 + 256 + 32 + 32 + 32], 2)
timestamp = int(header[32 + 256 + 256:32 + 256 + 256 + 32], 2)
merkle_root = f"{int(header[32 + 256:32 + 256 + 256], 2):064x}"

bloco = \
{
    "versao": versao,
    "dificuldade": dificuldade,
    "target": target,
    "nonce": nonce,
    "timestamp": timestamp,
    "hash_bloco_anterior": hash_bloco_anterior,
    "hash_raiz_merkle": merkle_root,
    "hash_final": sha2,
    "transacoes": transacoes,
}

mining_time = datetime.now() - datetime.fromtimestamp(bloco["timestamp"])
print(f"Tempo de mineração: {mining_time.total_seconds() / 60:.2f} minutos")

response = requests.put(f"{PEER}/check_mining", json=bloco)

print(response.json())

if response.json()["code"] == 200:
    from utils.utils import escrever_bloco
    escrever_bloco(bloco)
