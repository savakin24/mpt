#!/usr/bin/env python3

# Auxiliary functions to help visualize and understand the data.

import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch

from mpt_config import DIR_THIS
from mpt_data import data_load
from chainlink_utils import get_assets

def price_corr():
    df = data_load()

    # Set timestamp column as index.
    df['ts'] = pd.to_datetime(df['ts'], unit='s')
    df.set_index('ts', inplace=True)

    # Derive the correlation matrix between various assets.
    corr_matrix = df.corr()

    # Using the upper triangle matrix as mask (without the diagonal).
    m = corr_matrix.shape[0]
    r = np.arange(m)
    mask = r[:, None] < r

    # Define custom colormap.
    cmap = LinearSegmentedColormap.from_list('rg', ["r", "w", "g"], N=256)

    # Define asset names (not actually showing up!).
    names = [n.upper() for n in get_assets()]

    # Plot the heatmap.
    sns.heatmap(
        data=corr_matrix,
        cmap=cmap, mask=mask,
        cbar=True, annot=True,
        xticklabels=names,
        yticklabels=names
    )

    # Add custom legend box.
    box_x, box_y = 0.8, 0.6  # Position relative to the heatmap.
    box_width, box_height = 0.2, 0.4  # Dimensions of the box.

    # Create the legend box.
    box = FancyBboxPatch(
        (box_x, box_y), box_width, box_height,
        boxstyle="square,pad=0.0",
        linewidth=0, edgecolor="white", facecolor="white",
        transform=plt.gca().transAxes  # Axes-relative positioning.
    )
    plt.gca().add_patch(box)

    # Add asset names to the box.
    for i, name in enumerate(names):
        plt.text(
            box_x + 0.02,  # Slightly offset inside the box.
            box_y + box_height - 0.05 - i * 0.05,  # Vertical spacing.
            f"{i+1}. {name}", fontsize=13, color="black",
            verticalalignment="top", horizontalalignment="left",
            transform=plt.gca().transAxes
        )

    # Add title and labels.
    plt.title("Correlation Matrix - Assets")
    plt.tight_layout()

    # Save output image to figs.
    fnf_image = f"{DIR_THIS}/figs/correlations.png"
    plt.savefig(fnf_image)
    print(f"Saved correlation image to: {fnf_image}.")
    plt.show()


if __name__ == '__main__':
    # pass
    price_corr()