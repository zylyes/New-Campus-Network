from cryptography.fernet import Fernet
import os
import logging

class SecurityManager:
    def __init__(self):
        self.key, self.cipher = self._init_crypto()

    def _init_crypto(self):
        key_file = "encryption.key"
        try:
            if os.path.exists(key_file):
                with open(key_file, "rb") as f:
                    key = f.read()
                    return key, Fernet(key)
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key, Fernet(key)
        except Exception as e:
            logging.error(f"Crypto initialization failed: {str(e)}")
            raise

    def encrypt(self, plaintext: str) -> bytes:
        return self.cipher.encrypt(plaintext.encode())

    def decrypt(self, ciphertext: bytes) -> str:
        return self.cipher.decrypt(ciphertext).decode()