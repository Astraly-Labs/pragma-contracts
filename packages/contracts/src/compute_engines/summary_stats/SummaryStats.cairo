%lang starknet

from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.cairo_builtins import HashBuiltin, BitwiseBuiltin
from starkware.cairo.common.math import unsigned_div_rem
from starkware.starknet.common.syscalls import get_block_number

from time_series.prelude import TickElem
from time_series.stats.metrics import extract_values
from oracle.IOracle import IOracle, EmpiricAggregationModes
from compute_engines.summary_stats.library import SummaryStats

@storage_var
func SummaryStats__oracle_address() -> (res: felt) {
}

@storage_var
func SummaryStats__volatility(key: felt, interval: felt) -> (res: felt) {
}

@event
func VolatilitySaved(key: felt, interval: felt, value: felt) {
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    oracle_address: felt
) {
    SummaryStats__oracle_address.write(oracle_address);
    return ();
}

@view
func calculate_mean{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    key: felt, start: felt, stop: felt
) -> (mean_: felt) {
    let (oracle_address) = SummaryStats__oracle_address.read();
    let _mean = SummaryStats.calculate_mean(oracle_address, key, start, stop);
    return (_mean,);
}

@view
func calculate_volatility{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    key: felt, start: felt, stop: felt, num_samples: felt
) -> (volatility_: felt) {
    let (oracle_address) = SummaryStats__oracle_address.read();
    let _volatility = SummaryStats.calculate_volatility(
        oracle_address, key, start, stop, num_samples
    );
    // Reporting in percentage
    let percentage_ = _volatility * 100;
    return (percentage_,);
}

@external
func save_volatilities{
        bitwise_ptr: BitwiseBuiltin*,
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr,
    }(
    pair_ids_len, pair_ids: felt*, interval: felt, num_samples: felt
) {
    if (pair_ids_len == 0) {
        return ();
    }

    save_volatility([pair_ids], interval, num_samples);

    return save_volatilities(pair_ids_len - 1, pair_ids + 1, interval, num_samples);
}

func save_volatility{
        bitwise_ptr: BitwiseBuiltin*,
        syscall_ptr: felt*,
        pedersen_ptr: HashBuiltin*,
        range_check_ptr,
}(pair_id, interval, num_samples) {
    let (block_number) = get_block_number();
    let start = block_number - interval;

    let (volatility) = calculate_volatility(pair_id, start, block_number, num_samples);

    SummaryStats__volatility.write(pair_id, interval, volatility);
    VolatilitySaved.emit(pair_id, interval, volatility);
    return ();
}
