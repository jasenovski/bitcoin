from utils.utils import fechar_transacoes
from pickle import load

def fechar_pool():
    with open('transacoes.pkl', 'rb') as f:
        transacoes = load(f)

    qtd_transacoes = len(transacoes)

    if qtd_transacoes > 0:
        print(f'Fechando {qtd_transacoes} transações...')
        print(f"Transações fechadas para mineração: {transacoes}")

        fechar_transacoes(transacoes)
    
    else:
        print('Não há transações para fechar...')
