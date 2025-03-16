#!/usr/bin/env python3

import bz2
import pandas as pd

from mpt_config import FNF_DATA_CSV_BZ2

from chainlink_utils import get_price_ts, get_assets


def rdata_to_csv(assets=get_assets(), fnf=FNF_DATA_CSV_BZ2):
    # Load data.
    data = {}
    for asset in assets:
        ts, data[asset] = get_price_ts(asset)

    # Find what is the length of the shortest timeseries.
    ts_shortest = min([len(data[asset]) for asset in assets])

    # Generate CSV Header.
    str_data = 'ts,' + ','.join(assets) + '\n'
    for i in range(ts_shortest):
        str_data += f"{ts+i},"
        try:
            for asset in assets:
                price = data[asset][i]
                if asset != assets[-1]:
                    str_data += f"{price},"
                else:
                    str_data += f"{price}\n"
        except:
            print(f"error: {asset} {i}")

    # Write CSV with data ready for pandas.
    print(f"Writing CSV data to: {FNF_DATA_CSV_BZ2}")
    with bz2.open(fnf, "wt") as f:
        f.write(str_data)


def data_load(fnf=FNF_DATA_CSV_BZ2):
    with bz2.open(fnf) as fd:
        return pd.read_csv(fd)


if __name__ == "__main__":
    pass
    # Generate CSV file from raw data:
    # rdata_to_csv()
    #
    # # Preview CSV data using pandas:
    # pd = data_load()
    # print(pd)

