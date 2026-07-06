from models.sha_256 import sha_256
from models.sha_bitcoin import sha_256_btc

def gerar_novo_nivel(pares):
    novo_nivel = []
    for hash1, hash2 in pares:
        hash1_bin = f"{int(hash1, 16):0256b}"
        hash2_bin = f"{int(hash2, 16):0256b}"
        novo_nivel.append(sha_256_btc(hash1_bin + hash2_bin))
    
    return novo_nivel

def gerar_pares(transacoes, nivel=0):
    pares = []
    for i in range(0, len(transacoes), 2):
        par = transacoes[i:i+2]

        if len(par) == 2:
            pares.append([par[0], par[1]])
        else:
            pares.append([par[0], par[0]])
    
    if nivel == 0:
        for i, par in enumerate(pares):
            hash1 = sha_256(str(par[0]))
            hash2 = sha_256(str(par[1]))
            pares[i] = [hash1, hash2]

    return pares

def gerar_raiz_merkle(transacoes):

    nivel = 0
    pares = gerar_pares(transacoes=transacoes, nivel=nivel)
    transacoes = gerar_novo_nivel(pares)
    while len(transacoes) > 1:
        pares = gerar_pares(transacoes=transacoes, nivel=nivel)
        transacoes = gerar_novo_nivel(pares)
        nivel += 1
    
    return transacoes[0]