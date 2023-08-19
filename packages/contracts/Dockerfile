FROM python:3.9.16

FROM python:3.9.13

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$PATH:/root/.local/bin"
RUN poetry config virtualenvs.create false

# install deps
WORKDIR /app/pragma/packages/contracts
COPY poetry.lock .
COPY pyproject.toml .
COPY scripts ./scripts
COPY README.md .
RUN poetry install
# split install in two steps to leverage docker cache
COPY . .
RUN poetry install

# Build contracts
# RUN python scripts/compile_all.py

ENV STARKNET_NETWORK=madara_tsukuyomi \
    MADARA_ACCOUNT_ADDRESS=0x2 \
    MADARA_PRIVATE_KEY=0x00c1cf1490de1352865301bb8705143f3ef938f97fdf892f1090dcb5ac7bcd1d
# Make the script executable
RUN chmod +x ./entrypoint.sh
CMD [ "./entrypoint.sh" ]