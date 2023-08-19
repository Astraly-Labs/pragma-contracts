# %% Imports
import logging
from asyncio import run
from math import ceil, log

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
)


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# %% Main
async def main():
    # %% Declarations
    logger.info(
        f"ℹ️  Connected to CHAIN_ID {NETWORK['chain_id'].value.to_bytes(ceil(log(NETWORK['chain_id'].value, 256)), 'big')} "
        f"with RPC {RPC_CLIENT.url}"
    )
    account = await get_starknet_account()
    if NETWORK["name"] in ["madara", "madara_tsukuyomi", "sharingan", "pragma-testnet"] and account.address == 1:
        await deploy_starknet_account(amount=100)
    account = await get_starknet_account()
    logger.info(f"ℹ️  Using account {hex(account.address)} as deployer")

    class_hash = {
        contract["contract_name"]: await declare(contract["contract_name"])
        for contract in COMPILED_CONTRACTS
    }
    dump_declarations(class_hash)

    salt = 1 if NETWORK["name"] in ["madara_tsukuyomi"] else None
    # %% Deploy
    deployments = {}
    deployments["PublisherRegistry"] = await deploy(
        "PublisherRegistry",
        account.address,
        salt=salt
    )
    selector = ContractFunction.get_selector("initializer")
    calldata = [account.address, deployments["PublisherRegistry"]["address"], len(CURRENCIES)]
    for currency in CURRENCIES:
        calldata.extend(currency.serialize())
    calldata.append(len(PAIRS))
    for pair in PAIRS:
        calldata.extend(pair.serialize())
    constructor_args = [class_hash["Oracle"], selector, calldata]
    deployments["Proxy"] = await deploy(
        "Proxy",
        *constructor_args,
        salt=salt
    )
    deployments["SummaryStats"] = await deploy(
        "SummaryStats",
        deployments["Proxy"]["address"],
        salt=salt
    )
    dump_deployments(deployments)

    


# %% Run
if __name__ == "__main__":
    run(main())