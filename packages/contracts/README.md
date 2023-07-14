# Pragma Contracts

Deploy Pragma on Madara.

## Installation

The project uses poetry. Just use:

```bash
poetry install
```

## Deploy

First copy the [.env.example](./.env.example) into a `.env` file. Default
account addresses for katana, madara and starknet-devnet are set.

Then use the `STARKNET_NETWORK` env variable to target madara, katana or the
devnet. For example:

```bash
STARKNET_NETWORK=pragma_testnet python ./scripts/compile_all.py
STARKNET_NETWORK=pragma_testnet python ./scripts/deploy_pragma.py
```
