from flask import Flask
from flask_restful import Api, Resource
from flask_restful.reqparse import RequestParser
from json import load
from glob import glob
from utils.utils import checagem, escrever_bloco, mover_transacoes

app = Flask(__name__)
api = Api(app)

block_put_args = RequestParser()
block_put_args.add_argument("versao", type=int, help="Versao do bloco", required=True)
block_put_args.add_argument("dificuldade", type=int, help="Dificuldade", required=True)
block_put_args.add_argument("target", type=int, help="Target", required=True)
block_put_args.add_argument("nonce", type=int, help="Nonce de mineração", required=True)
block_put_args.add_argument("timestamp", type=int, help="Timestamp", required=True)
block_put_args.add_argument("hash_bloco_anterior", type=str, help="Hash do bloco anterior", required=True)
block_put_args.add_argument("hash_raiz_merkle", type=str, help="Hash da raiz de merkle", required=True)
block_put_args.add_argument("transacoes", type=dict, action="append", help="Transações", required=True)
block_put_args.add_argument("hash_final", type=str, help="Hash final do bloco", required=True)

class GetConfigs(Resource):
    def get(self):
        with open('configs/configuracoes.json') as json_file:
            configs = load(json_file)
        return configs

class GetLedger(Resource):
    def get(self):
        with open('ledger/ledger.json') as json_file:
            ledger = load(json_file)
        return ledger

class GetTransacoes(Resource):
    def get(self):
        arquivos_transacoes = glob("transacoes_minerar/*.json")
        if len(arquivos_transacoes) > 0:
            with open(arquivos_transacoes[0], "r") as file:
                transacoes = load(file)
            return transacoes
        else:
            return [
                        {
                            "message": "Sem Transacoes", 
                            "code": 400
                        }
                   ]

class CheckMinerar(Resource):
    def put(self):
        bloco = block_put_args.parse_args()
        if checagem(bloco=bloco):
            mover_transacoes(bloco["transacoes"])
            escrever_bloco(bloco)
            return {"message": "OK", "code": 200}
        else:
            return {"message": "NOK", "code": 400}

if __name__ == "__main__":
    api.add_resource(GetConfigs, "/get_configs")
    api.add_resource(GetLedger, "/get_ledger")
    api.add_resource(CheckMinerar, "/check_mining")
    api.add_resource(GetTransacoes, "/get_transacoes")
    
    app.run(host='0.0.0.0', port=5000)