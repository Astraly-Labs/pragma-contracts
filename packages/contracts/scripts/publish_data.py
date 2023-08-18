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

from empiric.publisher.client import EmpiricPublisherClient
from empiric.publisher.fetchers import (
    BitstampFetcher,
    CexFetcher,
    CoinbaseFetcher,
    AscendexFetcher,
    DefillamaFetcher
)
from empiric.publisher.assets import get_spot_asset_spec_for_pair_id
from empiric.core.entry import SpotEntry
from empiric.core.utils import currency_pair_to_pair_id


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ASSETS = "BTC/USD,ETH/USD,SOL/USD,DOGE/USD,BTC/EUR,USDC/USD,USDT/USD"


# %% Main
async def main():
    # %% Setup
    logger.info(
        f"ℹ️  Connected to CHAIN_ID {NETWORK['chain_id'].value.to_bytes(ceil(log(NETWORK['chain_id'].value, 256)), 'big')} "
        f"with RPC {RPC_CLIENT.url}"
    )
    account = await get_starknet_account()
    
    current_publishers = await call("PublisherRegistry", "get_all_publishers")
    if len(current_publishers.publishers) > 0 and 88314212732225 in current_publishers.publishers:
        logger.info(
            f"ℹ️  Publisher 'PRAGMA' already added"
        )
    else:
        # %% Add publisher
        await invoke("PublisherRegistry", "add_publisher", "PRAGMA", account.address)
        logger.info(
            f"ℹ️  Publisher 'PRAGMA' added"
        )
        await invoke("PublisherRegistry", "add_source_for_publisher", "PRAGMA", "BITSTAMP")
        await invoke("PublisherRegistry", "add_source_for_publisher", "PRAGMA", "CEX")
        await invoke("PublisherRegistry", "add_source_for_publisher", "PRAGMA", "COINBASE")
        await invoke("PublisherRegistry", "add_source_for_publisher", "PRAGMA", "ASCENDEX")
        await invoke("PublisherRegistry", "add_source_for_publisher", "PRAGMA", "DEFILLAMA")
        logger.info(
            f"ℹ️  Sources added for publisher 'PRAGMA' "
        )
    


    # %% Publish data
    assets = [get_spot_asset_spec_for_pair_id(asset) for asset in ASSETS.split(",")]
    publisher_client = EmpiricPublisherClient()
    publisher_client.add_fetchers(
        [
            fetcher(assets, "PRAGMA")
            for fetcher in (
                BitstampFetcher,
                CexFetcher,
                CoinbaseFetcher,
                AscendexFetcher,
                DefillamaFetcher
            )
        ]
    )
    

    pairs = [
        currency_pair_to_pair_id(*p["pair"]) for p in assets if p["type"] == "SPOT"
    ]

    abi = json.load(open(get_artifact("Oracle")))["abi"]
    abi_summary = json.load(open(get_artifact("SummaryStats")))["abi"]
    while True:
        _entries = await publisher_client.fetch()
        serialized_spot_entries = SpotEntry.serialize_entries(_entries)
        await invoke("Proxy", "publish_spot_entries", serialized_spot_entries, abi=abi)
        # await invoke("Proxy", "set_checkpoints", pairs, 84959893733710, abi=abi)
        # await invoke("SummaryStats", "save_volatilities", pairs, 1, 1, abi=abi_summary)
        # time.sleep(1)
    


# %% Run
if __name__ == "__main__":
    run(main())