import sys
from pathlib import Path

path_add = str(Path(__file__).parent.parent)
if path_add not in sys.path:
    sys.path.append(path_add)

import numpy as np
from utils.constants import letters, primos
from utils.operations import gerar_words, ch_function, maj_function, somatorio_zero_function, somatorio_um_function, addition_2_32

def sha_256_btc(binario_str: str, 
                hash_anterior: str = "6a09e667bb67ae853c6ef372a54ff53a510e527f9b05688c1f83d9ab5be0cd19", 
                ks: list[int]=None):

    """
    Função que implementa o algoritmo SHA-256 do Bitcoin.

    Args:
        binario_str (str): String binária com 512 bits de entrada para a função SHA-256.
        hash_anterior (str): Hash anterior em formato hexadecimal. Padrão é o hash
        inicial do SHA-256.
        ks (list[int]): Lista de constantes K em formato decimal. Padrão é None

    Returns:
        str: Hash (hexadecimal) final gerado pelo algoritmo SHA-256 do Bitcoin.
    """

    words = gerar_words(binario_str, num_blocos=1)

    hashes = [int(hash_anterior[i * 8:(i + 1) * 8:1], 16) for i in range(8)]

    if ks is None:
        ks = [int((np.cbrt(primo) - int(np.cbrt(primo))) * 2 ** 32) 
              for primo in primos if primos.index(primo) < 64]

    a, b, c, d, e, f, g, h = hashes
    for j in range(64):

        ch = ch_function(e, f, g)
        maj = maj_function(a, b, c)
        somatorio_zero = somatorio_zero_function(a)
        somatorio_um = somatorio_um_function(e)
        t1 = addition_2_32(h, somatorio_um, ch, ks[j], words[0][j])
        t2 = addition_2_32(somatorio_zero, maj)

        h = g
        g = f
        f = e
        e = addition_2_32(d, t1)
        d = c
        c = b
        b = a
        a = addition_2_32(t1, t2)

    for k in range(8):
        exec(f"hashes[{k}] = addition_2_32({letters['all'][k]}, {hashes[k]})")

    hash_final = ""
    for i in range(8):
        hash_final += "{0:08x}".format(hashes[i])
    
    return hash_final