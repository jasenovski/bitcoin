import numpy as np
from utils.constants import letters, valores_sigmas, valores_words

def bitwise_and(*valores):
    r = valores[0]
    for valor in valores[1:]:
        r &= valor
    
    return r

def bitwise_or(*valores):
    r = valores[0]
    for valor in valores[1:]:
        r |= valor
    
    return r


def bitwise_not(valor):
    return ~valor

def bitwise_xor(*valores):
    r = valores[0]
    for valor in valores[1:]:
        r ^= valor
    
    return r

def right_shift(val, num_desloc):
    return val >> num_desloc


def right_rotation(val, num_rot):
    return val >> num_rot | val << (32 - num_rot)


def addition_2_32(*valores):
    soma = np.sum(valores)
    return soma % (2 ** 32)


def ch_function(*valores):

    # valores = [e, f, g]

    for i, charactere in enumerate(letters["ch"]):
        exec(f"global {charactere}; {charactere} = valores[{i}]")

    return bitwise_xor(bitwise_and(e, f), bitwise_and(bitwise_not(e), g))

def maj_function(*valores):

    # valores = [a, b, c]

    for i, charactere in enumerate(letters["maj"]):
        exec(f"global {charactere}; {charactere} = valores[{i}]")

    return bitwise_xor(bitwise_and(a, b), bitwise_and(a, c), bitwise_and(b, c))


def somatorio_zero_function(valor):
    rr2 = right_rotation(valor, 2)
    rr13 = right_rotation(valor, 13)
    rr22 = right_rotation(valor, 22)
    return bitwise_xor(rr2, rr13, rr22)


def somatorio_um_function(valor):
    rr6 = right_rotation(valor, 6)
    rr11 = right_rotation(valor, 11)
    rr25 = right_rotation(valor, 25)
    return bitwise_xor(rr6, rr11, rr25)


def mens_transf_bits(mensagem_funcao, num_blocos):

    num_caracts_mens = len(mensagem_funcao)
    num_bits_mens = 8 * num_caracts_mens
    num_bits_mens_bin = ('{:64b}'.format(num_bits_mens)).replace(" ", "0")

    mens_transf = ""
    for i in range(num_caracts_mens):
        mens_transf += '{:08b}'.format(ord(mensagem_funcao[i]))

    mens_transf += "1"

    qtd_zeros = (512 * num_blocos) - num_bits_mens - 1 - 64
    mens_transf += "0" * qtd_zeros

    mens_transf += num_bits_mens_bin

    return mens_transf


def sigma_zero(valor):
    rr7 = right_rotation(valor, 7)
    rr18 = right_rotation(valor, 18)
    rs3 = right_shift(valor, 3)
    return bitwise_xor(rr7, rr18, rs3)


def sigma_um(valor):
    rr17 = right_rotation(valor, 17)
    rr19 = right_rotation(valor, 19)
    rs10 = right_shift(valor, 10)
    return bitwise_xor(rr17, rr19, rs10)


def gerar_words(mens, num_blocos):
    words = np.zeros((num_blocos, 64), dtype=object)

    for i in range(num_blocos):
        for j in range(16):
            words[i][j] = int(mens[512 * i + j * 32:512 * i + (j + 1) * 32], 2)

    for i in range(num_blocos):
        for j in range(16, 64, 1):
            sig1 = sigma_um(words[i][j - 2])
            sig0 = sigma_zero(words[i][j - 15])
            valores_sigmas["sig0"].append(f"{sig0:08x}")
            valores_sigmas["sig1"].append(f"{sig1:08x}")
            words[i][j] = addition_2_32(sig1, words[i][j - 7], sig0, words[i][j - 16])
    
    for i in range(num_blocos):
        for j in range(64):
            valores_words["words"].append(f"{words[i][j]:08x}")

    return words