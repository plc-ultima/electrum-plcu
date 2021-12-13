# -*- coding: utf-8 -*-
#
# Electrum - lightweight Bitcoin client
# Copyright (C) 2018 The Electrum developers
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import json

from .util import inv_dict, all_subclasses
from . import bitcoin


def read_json(filename, default):
    path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(path, 'r') as f:
            r = json.loads(f.read())
    except:
        r = default
    return r


GIT_REPO_URL = "https://github.com/plc-ultima/electrum-plcu"
GIT_REPO_ISSUES_URL = "https://github.com/plc-ultima/electrum-plcu/issues"
BIP39_WALLET_FORMATS = read_json('bip39_wallet_formats.json', [])


class AbstractNet:

    NET_NAME: str
    TESTNET: bool
    WIF_PREFIX: int
    ADDRTYPE_P2PKH: int
    ADDRTYPE_P2SH: int
    SEGWIT_HRP: str
    BOLT11_HRP: str
    GENESIS: str
    BLOCK_HEIGHT_FIRST_LIGHTNING_CHANNELS: int = 0
    BIP44_COIN_TYPE: int
    LN_REALM_BYTE: int

    MONEYBOX_ADDRESS: str
    GRAVEBOX_ADDRESS: str
    TAXBOX_PUBKEY: str

    @classmethod
    def max_checkpoint(cls) -> int:
        return max(0, len(cls.CHECKPOINTS) * 2016 - 1)

    @classmethod
    def rev_genesis_bytes(cls) -> bytes:
        return bytes.fromhex(bitcoin.rev_hex(cls.GENESIS))


class PlcultimaMainnet(AbstractNet):

    NET_NAME = "mainnet"
    TESTNET = False
    WIF_PREFIX = 0xC804AA
    ADDRTYPE_P2PKH = 0xC80528
    ADDRTYPE_P2SH = 0xC80529

    MONEYBOX_ADDRESS = ""
    TAXBOX_PUBKEY   = "036f433065070d0b473b6ba5cc7c506dcecdbdb9333c244d4649dc7e6e5a7dc66b"

    SEGWIT_HRP = "plcu"
    BOLT11_HRP = SEGWIT_HRP
    GENESIS = "f596cf825f5833b7e30243d12c6164bd26db5fba05af08c498c886ff843158dd"
    DEFAULT_PORTS = {'t': '50001', 's': '50002'}
    DEFAULT_SERVERS = read_json('servers.json', {})
    CHECKPOINTS = read_json('checkpoints.json', [])
    # BLOCK_HEIGHT_FIRST_LIGHTNING_CHANNELS = 497000

    XPRV_HEADERS = {
        'standard':    0x0488ade4,  # xprv
        # 'p2wpkh-p2sh': 0x049d7878,  # yprv
        # 'p2wsh-p2sh':  0x0295b005,  # Yprv
        # 'p2wpkh':      0x04b2430c,  # zprv
        # 'p2wsh':       0x02aa7a99,  # Zprv
    }
    XPRV_HEADERS_INV = inv_dict(XPRV_HEADERS)
    XPUB_HEADERS = {
        'standard':    0x0488b21e,  # xpub
        # 'p2wpkh-p2sh': 0x049d7cb2,  # ypub
        # 'p2wsh-p2sh':  0x0295b43f,  # Ypub
        # 'p2wpkh':      0x04b24746,  # zpub
        # 'p2wsh':       0x02aa7ed3,  # Zpub
    }
    XPUB_HEADERS_INV = inv_dict(XPUB_HEADERS)
    BIP44_COIN_TYPE = 2
    LN_REALM_BYTE = 0
    # LN_DNS_SEEDS = [
    #     'nodes.lightning.directory.',
    #     'lseed.bitcoinstats.com.',
    #     'lseed.darosior.ninja',
    # ]


class PlcultimaTestnet(AbstractNet):

    NET_NAME = "testnet"
    TESTNET = True
    WIF_PREFIX = 0xC805DE
    ADDRTYPE_P2PKH = 0xC80524
    ADDRTYPE_P2SH = 0xC80525

    MONEYBOX_ADDRESS = ""
    TAXBOX_PUBKEY   = "0372e1234a73c83625e153d3ed47b631f9cfc2e112d1c4172b4cfc5d4b76994022"

    SEGWIT_HRP = "tplcu"
    BOLT11_HRP = SEGWIT_HRP
    GENESIS = "83b43792fc6255e24d471ce91e4d2a31de74280990ce8ff220c04227864d5377"
    DEFAULT_PORTS = {'t': '51001', 's': '51002'}
    DEFAULT_SERVERS = read_json('servers_testnet.json', {})
    CHECKPOINTS = read_json('checkpoints_testnet.json', [])

    XPRV_HEADERS = {
        'standard':    0x04358394,  # tprv
        # 'p2wpkh-p2sh': 0x044a4e28,  # uprv
        # 'p2wsh-p2sh':  0x024285b5,  # Uprv
        # 'p2wpkh':      0x045f18bc,  # vprv
        # 'p2wsh':       0x02575048,  # Vprv
    }
    XPRV_HEADERS_INV = inv_dict(XPRV_HEADERS)
    XPUB_HEADERS = {
        'standard':    0x043587cf,  # tpub
        # 'p2wpkh-p2sh': 0x044a5262,  # upub
        # 'p2wsh-p2sh':  0x024289ef,  # Upub
        # 'p2wpkh':      0x045f1cf6,  # vpub
        # 'p2wsh':       0x02575483,  # Vpub
    }
    XPUB_HEADERS_INV = inv_dict(XPUB_HEADERS)
    BIP44_COIN_TYPE = 1
    LN_REALM_BYTE = 1
    # LN_DNS_SEEDS = [  # TODO investigate this again
    #     #'test.nodes.lightning.directory.',  # times out.
    #     #'lseed.bitcoinstats.com.',  # ignores REALM byte and returns mainnet peers...
    # ]



NETS_LIST = tuple(all_subclasses(AbstractNet))

# don't import net directly, import the module instead (so that net is singleton)
net = PlcultimaMainnet


def set_mainnet():
    global net
    net = PlcultimaMainnet

def set_testnet():
    global net
    net = PlcultimaTestnet
