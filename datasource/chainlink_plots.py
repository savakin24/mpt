#!/usr/bin/env python3

import seaborn as sns
sns.set_style("dark")
import matplotlib.pyplot as plt
from datetime import datetime


from chainlink_utils import DIR_THIS, get_assets, get_price_ts


def plot_price_time_series(t_start, ts_prices, name=''):

    # Asset description.
    desc = (' ' + name if name else '').upper()

    # Extract timestamps and prices from the data.
    timestamps = [datetime.fromtimestamp(i+t_start) for i in range(len(ts_prices))]

    # Create the plot
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, ts_prices, label='Price'+desc)

    # Add labels, title, and legend.
    plt.xlabel('Timestamp')
    plt.ylabel('Price'+desc)
    plt.title('Price Time Series'+desc)
    plt.legend()
    plt.grid(True)

    # Format x-axis for better readability.
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save output image to figs.
    fnf_image = f"{DIR_THIS}/figs/plot_{name.lower()}.png"
    plt.savefig(fnf_image)
    print(f"Saved correlation image to: {fnf_image}.")
    plt.show()

    # Show the plot.
    plt.show()


def main():
    for asset in get_assets():
        t_start, ts_prices = get_price_ts(asset)
        plot_price_time_series(t_start, ts_prices, asset.capitalize())


if __name__ == '__main__':
    main()
