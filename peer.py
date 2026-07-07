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
        print("Ledger local encontrado.")
    except FileNotFoundError:
        print("Ledger não encontrado...")
        with open("ledger/ledger.json", "w") as file:
            dump(ledger, file, indent=4)
        print("Ledger obtido e salvo localmente.")
    
def check_configs():
    try:
        from glob import glob
        arquivos_configs = glob("configs/configuracoes*.json")
        if not arquivos_configs:
            raise FileNotFoundError("Nenhum arquivo de configuração encontrado.")

        def versao_do_arquivo(caminho):
            with open(caminho, encoding="utf-8") as json_file:
                dados = load(json_file)
            config = dados[-1] if isinstance(dados, list) else dados
            return config["versao"]

        ultimo_arquivo = max(arquivos_configs, key=versao_do_arquivo)
        with open(ultimo_arquivo, encoding="utf-8") as json_file:
            configs_local = load(json_file)

        print("Configurações locais encontradas.")

        if configs_local[0]["versao"] != configs["versao"]:
            import os
            print(f"Executando 'git pull' para atualizar a versão local do peer. "
                  f"Versão do peer: {configs['versao']} | Versão local: {configs_local[0]['versao']}")
            os.system("git pull")

            with open("configs/configuracoes.json", "w") as file:
                dump(configs, file, indent=4)
            
            print("Versão atualizada. Por favor, reinicie o minerador para continuar.")
            exit()

    except FileNotFoundError:
        print("Configurações não encontradas...")
        with open("configs/configuracoes.json", "w") as file:
            dump(configs, file, indent=4)
        print("Configurações obtidas e salvas localmente.")

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
ledger: list[dict] = requests.get(f"{PEER}/get_ledger").json()
ultimo_bloco: dict = ledger[-1]

check_ledger_exists()
check_configs()

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

mining_time = datetime.fromtimestamp(bloco["timestamp"]) - start_time
print(f"Tempo de mineração: {mining_time.total_seconds() / 60:.2f} minutos")

response = requests.put(f"{PEER}/check_mining", json=bloco)

print(response.json())

if response.json()["code"] == 200:
    from utils.utils import escrever_bloco
    ledger = escrever_bloco(bloco, ledger)
    
    response = \
        requests.post(url=f"{PEER}/receber_ledger", 
                      json={"minerador": f"{MINERADOR}", 
                            "ledger": ledger})
    print("-" * 100)
    print(response.json())
