import sys
from pathlib import Path

path_add = str(Path(__file__).parent.parent)
if path_add not in sys.path:
    sys.path.append(path_add)

import numpy as np
from utils.constants import letters, primos
from utils.operations import mens_transf_bits, gerar_words, ch_function, maj_function, somatorio_zero_function, somatorio_um_function, addition_2_32

def sha_256(mensagem_funcao: str) -> str:

    """
    Função que implementa o algoritmo SHA-256.

    Args:
        mensagem_funcao (str): Mensagem de entrada para a função SHA-256.

    Returns:
        str: Hash (hexadecimal) final gerado pelo algoritmo SHA-256.
    """

    valores_funcoes = {"ch": [], "maj": [], "s0": [], "s1": [], "T1": [], "T2": []}
    valores_constantes = {"a": [], "b": [], "c": [], "d": [], "e": [], "f": [], "g": [], "h": []}
    valores_hash_parciais = {"h0": [], "h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": [], "h7": []}

    num_blocos = int(np.ceil((len(mensagem_funcao) - 55) / 64) + 1)

    mensagem_bits = mens_transf_bits(mensagem_funcao, num_blocos)

    words = gerar_words(mensagem_bits, num_blocos)

    hashes = [int((np.sqrt(primo) - int(np.sqrt(primo))) * 2 ** 32) for primo in primos if primos.index(primo) < 8]

    ks = [int((np.cbrt(primo) - int(np.cbrt(primo))) * 2 ** 32) for primo in primos if primos.index(primo) < 64]

    for i in range(num_blocos):

        a = hashes[0]
        b = hashes[1]
        c = hashes[2]
        d = hashes[3]
        e = hashes[4]
        f = hashes[5]
        g = hashes[6]
        h = hashes[7]

        for j in range(64):

            ch = ch_function(e, f, g)
            valores_funcoes["ch"].append('{0:08x}'.format(ch))

            maj = maj_function(a, b, c)
            valores_funcoes["maj"].append('{0:08x}'.format(maj))

            somatorio_zero = somatorio_zero_function(a)
            valores_funcoes["s0"].append('{0:08x}'.format(somatorio_zero))

            somatorio_um = somatorio_um_function(e)
            valores_funcoes["s1"].append('{0:08x}'.format(somatorio_um))

            t1 = addition_2_32(h, somatorio_um, ch, ks[j], words[i][j])
            valores_funcoes["T1"].append('{0:08x}'.format(t1))

            t2 = addition_2_32(somatorio_zero, maj)
            valores_funcoes["T2"].append('{0:08x}'.format(t2))

            h = g
            g = f
            f = e
            e = addition_2_32(d, t1)
            d = c
            c = b
            b = a
            a = addition_2_32(t1, t2)

            for k, v in enumerate(valores_hash_parciais.values()):
                # letters['all'][k] -> variáveis a, b, c, d, e, f, g, h
                exec(f"global x; x = addition_2_32({letters['all'][k]}, {hashes[k]})")
                v.append(f"{x:08x}")
                
            for k, v in enumerate(valores_constantes.values()):
                exec(f"global x; x = {letters['all'][k]}")
                v.append(f"{x:08x}")

        for k in range(8):
            exec(f"hashes[{k}] = addition_2_32({letters['all'][k]}, {hashes[k]})")

    hash_final = ""
    for hf in hashes:
        hash_final += f"{hf:08x}"
    
    return hash_final

if __name__ == "__main__":
    sha = sha_256("abc")
    print(sha)
