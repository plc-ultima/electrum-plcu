#!/usr/bin/env python3
import sys
import json
import hashlib

from .crypto import aes_encrypt_mode_ecb, aes_decrypt_mode_ecb

if str != bytes:
    # Python 3.x
    def ord(c):
        return c

    def chr(n):
        return bytes((n, ))

class Base24():
    def __init__(self):
        self.__b24chars = '3479ACDEFHJKLMNPQRTUVWXY'
        self.__b24base = len(self.__b24chars)
        self.b24chars = self.__b24chars

    def b24encode(self, v):
        """ encode v, which is a string of bytes, to base24.
        """
        long_value = 0
        for (i, c) in enumerate(v[::-1]):
            long_value += (256**i) * ord(c)

        result = ''
        while long_value >= self.__b24base:
            div, mod = divmod(long_value, self.__b24base)
            result = self.__b24chars[mod] + result
            long_value = div
        result = self.__b24chars[long_value] + result

        # Bitcoin does a little leading-zero-compression:
        # leading 0-bytes in the input become leading-1s
        nPad = 0
        for c in v:
            if c == '\0':
                nPad += 1
            else:
                break

        return (self.__b24chars[0] * nPad) + result

    def b24decode(self, v, length=None):
        """ decode v into a string of len bytes
        """
        long_value = 0
        for (i, c) in enumerate(v[::-1]):
            c_index = self.__b24chars.find(c)
            if c_index == -1:
                print(f'b24decode: symbol {c} is not found in alphabet')
                return b''
            long_value += c_index * (self.__b24base**i)

        result = bytes()
        while long_value >= 256:
            div, mod = divmod(long_value, 256)
            result = chr(mod) + result
            long_value = div
        result = chr(long_value) + result

        nPad = 0
        for c in v:
            if c == self.__b24chars[0]:
                nPad += 1
            else:
                break

        result = chr(0) * nPad + result
        if length is not None and len(result) != length:
            return None

        return result


def multiply_by_16(b):
    if b[0] & 0xF0:
        return None
    lenght = len(b)
    value = int.from_bytes(b, byteorder='big')
    value = value * 16
    return value.to_bytes(lenght, byteorder='big')


def divide_by_16(b):
    lenght = len(b)
    value = int.from_bytes(b, byteorder='big')
    value = value >> 4
    return value.to_bytes(lenght, byteorder='big')


class PlcKeys():

    def __init__(self, network=None, constants_addrtype_p2pkh=None):
        assert (network == 'mainnet' or network == 'testnet' or constants_addrtype_p2pkh)
        if network:
            self.netid = 0x128 if network == 'mainnet' else 0x124
        else:
            self.netid = constants_addrtype_p2pkh & 0x000001FF

    def decrypt(self, key, pin, numkeys=1, keyindex=0):

        nkeys = numkeys - 1
        prefix = ((self.netid & 0x3ff) << 6) | ((
            (nkeys & 0x07) << 3) & 0x38) | (keyindex & 0x07)

        key_bin = Base24().b24decode(key.replace('-', ''))
        if not key_bin:
            print('Invalid base24 key format')
            return b''
        bignum = multiply_by_16(key_bin)

        if nkeys == 0:
            if int.from_bytes(bignum[:2], "big") != prefix:
                print(f"Invalid prefix: {prefix}")
                return b''

            keyhash = (bignum[34] << 12) | (bignum[35] << 4) | (
                (bignum[36] & 0xF0) >> 4)
        else:
            keyhash = (bignum[37] << 12) | (bignum[38] << 4) | (
                (bignum[39] & 0xF0) >> 4)

            bignum = multiply_by_16(bignum)[:-3]
            if int.from_bytes(bignum[:2], "big") != prefix:
                print(f"Invalid prefix: {prefix}")
                return b''

        salt = (keyhash | ((keyhash << 20) & 0xFFFFFFFFFFFFFFFF))
        bsalt = salt.to_bytes(5, "big")
        data = hashlib.scrypt(pin.encode(), salt=bsalt, n=8192, r=8, p=1)
        sha512 = hashlib.sha512(data).digest()

        key1 = aes_decrypt_mode_ecb(sha512[:32], bignum[2:-3])[:16]
        key2 = aes_decrypt_mode_ecb(sha512[32:], bignum[18:-3])[:16]
        key = key1 + key2

        hhh = hashlib.sha256(hashlib.sha256(prefix.to_bytes(length=2, byteorder='big') + key).digest()).digest()
        keyhash2 = (hhh[0] << 12) | (hhh[1] << 4) | ((hhh[2] & 0xF0) >> 4)
        if keyhash != keyhash2:
            print('Invalid transport PIN')
            return b''

        return key

    def encrypt(self, key, pin):

        numkeys = 1
        keyindex = 0

        nkeys = numkeys - 1
        prefix = ((self.netid & 0x3ff) << 6) | (
            ((nkeys & 0x07) << 3) & 0x38) | (keyindex & 0x07)

        if(len(key) != 32):
            raise Exception(f"Invalid key length: {len(key)}")

        data = prefix.to_bytes(2, byteorder='big') + key
        h = hashlib.sha256(data).digest()
        h = hashlib.sha256(h).digest()

        keyhash = (h[0] << 12) | (h[1] << 4) | ((h[2] & 0xF0) >> 4)

        salt = (keyhash | ((keyhash << 20) & 0xFFFFFFFFFFFFFFFF))
        bsalt = salt.to_bytes(5, "big")
        data = hashlib.scrypt(pin.encode(), salt=bsalt, n=8192, r=8, p=1)
        sha512 = hashlib.sha512(data).digest()

        prefix = prefix.to_bytes(2, 'big')

        bignum = bytearray(2)
        bignum[0] = prefix[0]
        bignum[1] = prefix[1]

        ekey1 = aes_encrypt_mode_ecb(sha512[:32], key[:16])
        ekey2 = aes_encrypt_mode_ecb(sha512[32:], key[16:])

        bignum.extend(ekey1+ekey2)

        bignum.append(h[0])
        bignum.append(h[1])
        bignum.append(h[2] & 0xF0)

        key_bin = divide_by_16(bytes(bignum))
        key24 = Base24().b24encode(key_bin)
        return key24

    def compile_keys(self, keys):
        key = bytearray(32)
        for ki in range(len(keys)):
            for bi in range(len(keys[ki])):
                key[bi] ^= keys[ki][bi]
        return key

    def decrypt_multikey(self, multikeys):
        key_index = 0
        keys = []
        numkeys = len(multikeys)
        for k in multikeys:
            kx = self.decrypt(
                k["key"].replace('-', ''),
                k["pin"],
                numkeys,
                key_index)
            key_index += 1
            keys.append(kx)
        if numkeys == 1:
            return keys[0]
        return self.compile_keys(keys)

def with_dashes(str):
    res = ''
    while str:
        res += str[0:4]
        str = str[4:]
        if str:
            res += '-'
    return res
