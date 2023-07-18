# %% Imports
import logging
from asyncio import run
from math import ceil, log
import time
import json

from scripts.constants import COMPILED_CONTRACTS, ETH_TOKEN_ADDRESS, NETWORK, RPC_CLIENT, PAIRS, CURRENCIES
from starknet_py.contract import ContractFunction
from scripts.utils import (
    call,
    declare,
    deploy,
    deploy_starknet_account,
    dump_declarations,
    dump_deployments,
    get_starknet_account,
    invoke,
    get_artifact
)


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# %% Main
async def main():
    # %% Setup
    logger.info(
        f"ℹ️  Connected to CHAIN_ID {NETWORK['chain_id'].value.to_bytes(ceil(log(NETWORK['chain_id'].value, 256)), 'big')} "
        f"with RPC {RPC_CLIENT.url}"
    )
    account = await get_starknet_account()
    
    # %% Add publisher
    # await invoke("PublisherRegistry", "add_publisher", "PRAGMA", account.address)
    # logger.info(
    #     f"ℹ️  Publisher 'PRAGMA' added"
    # )
    # await invoke("PublisherRegistry", "add_source_for_publisher", "PRAGMA", "PRAGMA")
    # logger.info(
    #     f"ℹ️  Source 'PRAGMA' added for publisher 'PRAGMA' "
    # )


    # %% Publish data
    abi = json.load(open(get_artifact("Oracle")))["abi"]
    mock_spot_entry = {
                "pair_id": "ETH/USD",
                "price": 1900,
                "volume": 0,
                "base" : {"timestamp": int(time.time()),
                "source": "PRAGMA",
                "publisher": "PRAGMA",}
            }
    await invoke("Proxy", "publish_spot_entry", mock_spot_entry, abi=abi)
    


# %% Run
if __name__ == "__main__":
    run(main())