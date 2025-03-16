#!/usr/bin/env python3

# Shared configuration.

import os
import eth_account
from web3 import Web3


DIR_THIS = os.path.abspath(os.path.dirname(__file__))

CONTRACT="XRPMPT"

# Target Chain RPC (using Ganache for testing).
# WEB3_PROVIDER = 'HTTP://127.0.0.1:7545'
WEB3_PROVIDER = 'https://rpc.sepolia.org'
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))


# Contract's ABI and BIN.
CONTRACT_BIN  = f"{DIR_THIS}/src/output/{CONTRACT}.bin"
CONTRACT_ABI  = f"{DIR_THIS}/src/output/{CONTRACT}.abi"

# Contract's address after it has been deployed:
CONTRACT_ADDR = f"0x284dae20099c497B97CC1992f2c484922686Cf53"

# Load private key (stored in .pkey).
try:
    PKEY = open(f"{DIR_THIS}/.pkey").read()
except Exception as _:
    print(f"Add private key to {DIR_THIS}/.pkey")
    exit(-1)

# Wallet address derived from the private key.
account = eth_account.Account.from_key(PKEY)
user_address = account.address

# # For POA
# from web3.middleware import geth_poa_middleware
# w3.middleware_onion.inject(geth_poa_middleware, layer=0)

if os.path.exists(CONTRACT_ABI):
    # Contract's ABI.
    contract_abi = open(CONTRACT_ABI, 'r').read()

    # Initialize the contract.
    contract = w3.eth.contract(address=CONTRACT_ADDR, abi=contract_abi)


# RLUSD Contract definitions:
IERC20_BIN  = f"{DIR_THIS}/src/output/IERC20.bin"
IERC20_ABI  = f"{DIR_THIS}/src/output/IERC20.abi"
WETH_ADDR   = f"0x7b79995e5f793A07Bc00c21412e50Ecae098E7f9"
RLUSD_ADDR  = f"0xe101FB315a64cDa9944E570a7bFfaFE60b994b1D"

if os.path.exists(IERC20_BIN):
    # IERC20 ABI.
    ierc20_contract_abi = open(IERC20_ABI, 'r').read()

    # Initialize the token's contracts.
    weth_contract = w3.eth.contract(address=WETH_ADDR, abi=ierc20_contract_abi)
    rlusd_contract = w3.eth.contract(address=RLUSD_ADDR, abi=ierc20_contract_abi)
