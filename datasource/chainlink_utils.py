import bz2
import json
import time
import datetime

from chainlink_config import (
    DIR_THIS,
    w3,
    abi,
    chainlink_addrs
)


# Return available assets.
def get_assets():
    return list(chainlink_addrs.keys())


# Get decimals for asset.
def get_chainlink_decimals(asset):
    if asset == 'pepe': return 18
    return 8


# Miscellaneous functions that can be shared.
def get_feed(asset, use_ens=False):
    if use_ens:
        ens = chainlink_addrs[asset][0]
        addr = w3.ens.address(ens)
    else:
        # Using Arbitrum Addr by default:
        addr = chainlink_addrs[asset][1]
    return w3.eth.contract(address=addr, abi=abi)


def get_price_ts(asset):
    fnf = f"{DIR_THIS}/data/{asset}.json.bz2"
    print(f"Loading data for {asset} from {fnf}")

    with bz2.open(fnf) as fd:
        rdata = json.load(fd)
    decimals = get_chainlink_decimals(asset)

    t_start = rdata[0]['updated_at']
    t_end = rdata[-1]['updated_at']
    ts_prices = []
    for i, e in enumerate(rdata):
        price = e['answer'] / 10 ** decimals
        ts_prices.append(price)
        t_this = rdata[i]['updated_at']
        try:
            t_next = rdata[i + 1]['updated_at']
        except:
            break
        if t_next != t_end:
            for _ in range(t_next - t_this):
                ts_prices.append(price)

    return t_start, ts_prices


# From date time to time stamp.
def dt2ts(dt):
    return int(time.mktime(
        datetime.datetime.strptime(dt, "%d/%m/%Y %H:%M:%S").timetuple()
    ))


# From time stamp to string time.
def ts2st(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')


