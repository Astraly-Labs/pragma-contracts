import json
import os
from enum import Enum
from pathlib import Path

import requests
from dotenv import load_dotenv
from starknet_py.net.full_node_client import FullNodeClient
from empiric.core import Currency, Pair

load_dotenv()

ETH_TOKEN_ADDRESS = 0x49D36570D4E46F48E99674BD3FCC84644DDD6B96F7C741B1562B82F9E004DC7


NETWORKS = {
    "sharingan": {
        "name": "sharingan",
        "explorer_url": "",
        "rpc_url": "https://sharingan.madara.zone",
    },
    "madara": {
        "name": "madara",
        "explorer_url": "",
        "rpc_url": "http://127.0.0.1:9944",
    },
    "katana": {
        "name": "katana",
        "explorer_url": "",
        "rpc_url": "http://127.0.0.1:5050",
    },
    "devnet": {
        "name": "devnet",
        "explorer_url": "",
        "rpc_url": "http://127.0.0.1:5050/rpc",
    },
    "pragma_testnet": {
      "name": "pragma_testnet",
      "explorer_url": "https://testnet.pragmaoracle.com/explorer",
      "rpc_url": "https://testnet.pragmaoracle.com/rpc"
    }
}

NETWORK = NETWORKS[os.getenv("STARKNET_NETWORK", "pragma_testnet")]
NETWORK["account_address"] = os.environ.get(
    f"{NETWORK['name'].upper()}_ACCOUNT_ADDRESS"
) or os.environ.get("ACCOUNT_ADDRESS")
NETWORK["private_key"] = os.environ.get(
    f"{NETWORK['name'].upper()}_PRIVATE_KEY"
) or os.environ.get("PRIVATE_KEY")


RPC_CLIENT = FullNodeClient(node_url=NETWORK["rpc_url"])
try:
    response = requests.post(
        RPC_CLIENT.url,
        json={
            "jsonrpc": "2.0",
            "method": f"starknet_chainId",
            "params": [],
            "id": 0,
        },
    )
    payload = json.loads(response.text)

    class ChainId(Enum):
        chain_id = int(payload["result"], 16)

    NETWORK["chain_id"] = ChainId.chain_id
except:
    pass

SOURCE_DIR = Path("src")
CONTRACTS = {p.stem: p for p in list(SOURCE_DIR.glob("**/*.cairo"))}
BUILD_DIR = Path("build")
BUILD_DIR.mkdir(exist_ok=True, parents=True)
DEPLOYMENTS_DIR = Path("deployments") / NETWORK["name"]
DEPLOYMENTS_DIR.mkdir(exist_ok=True, parents=True)

COMPILED_CONTRACTS = [
    {"contract_name": "Admin", "is_account_contract": False},
    {"contract_name": "Oracle", "is_account_contract": False},
    {"contract_name": "Proxy", "is_account_contract": False},
    {"contract_name": "PublisherRegistry", "is_account_contract": False},
    {"contract_name": "SummaryStats", "is_account_contract": False},
    {"contract_name": "YieldCurve", "is_account_contract": False},
    {"contract_name": "ERC20", "is_account_contract": False},
    {"contract_name": "OpenzeppelinAccount", "is_account_contract": True},
]

CURRENCIES = [
    Currency("USD", 8, 1, 0, 0),
    Currency(
        "BTC",
        18,
        0,
        0x03FE2B97C1FD336E750087D68B9B867997FD64A2661FF3CA5A7C771641E8E7AC,
        0x2260FAC5E5542A773AA44FBCFEDF7C193BC2C599,
    ),
    Currency(
        "ETH",
        18,
        0,
        0x049D36570D4E46F48E99674BD3FCC84644DDD6B96F7C741B1562B82F9E004DC7,
        0x0000000000000000000000000000000000000000,
    ),
    Currency(
        "USDC",
        6,
        0,
        0x053C91253BC9682C04929CA02ED00B3E423F6710D2EE7E0D5EBB06F3ECF368A8,
        0xA0B86991C6218B36C1D19D4A2E9EB0CE3606EB48,
    ),
    Currency(
        "USDT",
        6,
        0,
        0x068F5C6A61780768455DE69077E07E89787839BF8166DECFBF92B645209C0FB8,
        0xDAC17F958D2EE523A2206206994597C13D831EC7,
    ),
    Currency(
        "DAI",
        18,
        0,
        0x001108CDBE5D82737B9057590ADAF97D34E74B5452F0628161D237746B6FE69E,
        0x6B175474E89094C44DA98B954EEDEAC495271D0F,
    ),
]
PAIRS = [
    Pair("ETH/USD", "ETH", "USD"),
    Pair("BTC/USD", "BTC", "USD"),
    Pair("USDC/USD", "USDC", "USD"),
    Pair("USDT/USD", "USDT", "USD"),
    Pair("DAI/USD", "DAI", "USD"),
]