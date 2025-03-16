#!/usr/bin/env python3

# This script is used to fetch historical price data from the chainlink oracle.

import bz2
import json

from chainlink_config import DIR_THIS, DATE_TS_END, DATE_TS_START
from chainlink_utils  import get_assets, get_feed, dt2ts


# ChainLink returns the following schema:
def _map_data(d):
    return {
             'round_id': d[0],
               'answer': d[1],
           'started_at': d[2],
           'updated_at': d[3],
    'answered_in_round': d[4]
     }


def get_latest_round(feed):
    return _map_data(feed.functions.latestRoundData().call())


def get_round_data(feed, round_id):
    return _map_data(feed.functions.getRoundData(round_id).call())


def fetch_data_by_timestamp_range(feed, ts_start, ts_end):

    def find_valid_lower_bound_round_id():
        """Finds the first valid lower bound using binary search."""
        lower_bound = 1
        upper_bound = get_latest_round(feed)['round_id']

        while lower_bound < upper_bound:
            mid_round = (lower_bound + upper_bound) // 2
            try:
                round_data = get_round_data(feed, mid_round)
                if round_data and round_data['updated_at'] != 0:
                    # Valid round found, narrow the search lower.
                    upper_bound = mid_round
                else:
                    # Invalid data, narrow the search upper
                    lower_bound = mid_round + 1
            except Exception as _:
                # Narrow the search upper.
                print(f"Updating lower_bound: {lower_bound} -> {mid_round+1}")
                lower_bound = mid_round + 1

        # Validate the found lower bound.
        try:
            round_data = get_round_data(feed, lower_bound)
            if round_data and round_data['updated_at'] != 0:
                return lower_bound
        except:
            pass

        return None

    def find_round_by_timestamp(target_timestamp, direction, initial_lower_bound):
        """Finds the closest round for a given timestamp using binary search."""
        lower_bound = initial_lower_bound
        upper_bound = get_latest_round(feed)['round_id']
        target_round = None

        while lower_bound <= upper_bound:
            mid_round = (lower_bound + upper_bound) // 2
            try:
                round_data = get_round_data(feed, mid_round)
            except Exception as e:
                # print(f"Exception encountered for round {mid_round}: {e}")
                print(f"Updating lower_bound: {lower_bound} -> {mid_round + 1}")
                lower_bound = mid_round + 1
                continue

            if round_data is None or round_data['updated_at'] == 0:
                # Handle non-existent or uninitialized rounds.
                upper_bound = mid_round - 1
                continue

            updated_at = round_data['updated_at']

            if direction == 'start':
                if updated_at >= target_timestamp:
                    target_round = mid_round
                    # Narrow to earlier rounds.
                    upper_bound = mid_round - 1
                else:
                    lower_bound = mid_round + 1
            elif direction == 'end':
                if updated_at <= target_timestamp:
                    target_round = mid_round
                    # Narrow to later rounds.
                    lower_bound = mid_round + 1
                else:
                    upper_bound = mid_round - 1

        return target_round

    # Find the initial valid lower bound.
    valid_lower_bound = find_valid_lower_bound_round_id()
    if valid_lower_bound is None:
        print("No valid data found in the feed.")
        return []

    # Find the starting and ending round_ids using binary search.
    start_round_id = find_round_by_timestamp(ts_start, 'start', valid_lower_bound)
    end_round_id = find_round_by_timestamp(ts_end, 'end', valid_lower_bound)

    if start_round_id is None or end_round_id is None:
        return []

    # Fetch all rounds between the start and end round_ids.
    result = []
    for round_id in range(start_round_id, end_round_id + 1):
        round_data = get_round_data(feed, round_id)
        if round_data and ts_start <= round_data['updated_at'] <= ts_end:
            print(round_data)
            result.append(round_data)

    return result


def gen_dataset():
    ts_start = dt2ts(DATE_TS_START)
    ts_end = dt2ts(DATE_TS_END)

    for asset in get_assets():
        print(f"Fetching data for {asset} from {ts_start} to {ts_end}.")
        feed = get_feed(asset)
        data = fetch_data_by_timestamp_range(feed, ts_start, ts_end)
        print(data)
        fnf = f"{DIR_THIS}/data/{asset}.json.bz2"
        with bz2.open(fnf, "wt") as f:
            json.dump(data, f)
        print(f"Saved data to json at: {fnf}")
        print("\n\n\n\n\n")


if __name__ == "__main__":
    gen_dataset()
