import hashlib
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class APKCrypto:
    def __init__(self, seed_key: str):
        """
        Initialize the cipher. Modify this to match the APK's logic.
        Example: MD5 hash of a seed key for AES-128.
        """
        self.raw_key = hashlib.md5(seed_key.encode('utf-8')).digest()

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext to Hex/Base64. Modify MODE and Padding as needed.
        """
        cipher = AES.new(self.raw_key, AES.MODE_ECB)
        padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        
        # Adjust based on APK encoding (Hex vs Base64)
        return binascii.hexlify(ciphertext).decode('utf-8')

    def decrypt(self, encoded_ciphertext: str) -> str:
        """
        Decrypt Hex/Base64 ciphertext back to plaintext.
        """
        cipher = AES.new(self.raw_key, AES.MODE_ECB)
        
        # Adjust based on APK encoding (Hex vs Base64)
        ciphertext = binascii.unhexlify(encoded_ciphertext)
        
        decrypted_padded = cipher.decrypt(ciphertext)
        plaintext = unpad(decrypted_padded, AES.block_size)
        return plaintext.decode('utf-8')
