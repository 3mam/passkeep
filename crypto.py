from Crypto.Cipher import AES
from Crypto.Random.random import randint
from Crypto.Random import get_random_bytes
import hashlib


def generate_salt():
    return get_random_bytes(AES.block_size)


class Key:
    def __init__(self, password: bytearray, salt: bytearray):
        self._salt = salt
        self._private_key = hashlib.scrypt(
            password, salt=salt, n=2**14, r=8, p=1, dklen=32)

    def encrypt(self, text):
        cipher = AES.new(self._private_key, AES.MODE_GCM, nonce=self._salt)
        return cipher.encrypt(bytes(text, 'utf-8'))

    def decrypt(self, encrypt_text):
        cipher = AES.new(self._private_key, AES.MODE_GCM, nonce=self._salt)
        return cipher.decrypt(encrypt_text)


def generate_password():
    chars = [
        'q', 'w', 'r', 't', 'y', 'u', 'i', 'o', 'p',
        'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',
        'z', 'x', 'c', 'v', 'b', 'n', 'm',
        'Q', 'W', 'R', 'T', 'Y', 'U', 'I', 'O', 'P',
        'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L',
        'Z', 'X', 'C', 'V', 'B', 'N', 'M',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        '@', '#', '$', '%', '&', '!', '?', '='
    ]
    new_password = [
        chars[randint(0, len(chars)-1)]
        for i in range(20)
    ]
    return ''.join(new_password)
