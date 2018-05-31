import os
import binascii


def generate_key_generator():
    return binascii.hexlify(os.urandom(16)).decode()