from models.sha_bitcoin import sha_256_btc
from utils.constants import padding2

def shashasha(header1: str) -> str:

    """
    Função que realiza o duplo hash SHA-256 do cabeçalho do bloco.

    Args:
        header1 (str): Cabeçalho do bloco em binário com 512 bits.

    Returns:
        str: Hash final do bloco em hexadecimal.
    """

    sha0 = sha_256_btc(header1[:512])
    sha1 = sha_256_btc(header1[512:], hash_anterior=sha0)
    header2 = f"{int(sha1, 16):0256b}" + padding2
    sha2 = sha_256_btc(header2)
    return sha2