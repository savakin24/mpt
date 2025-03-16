#!/usr/bin/env python

# Import necessary dependencies.
import bz2
import numpy as np
import pandas as pd
import scipy.optimize as sco
import matplotlib.pyplot as plt

from mpt_config import DIR_THIS, FNF_DATA_CSV_BZ2, risk_free_rate


def get_mpt(fnf=FNF_DATA_CSV_BZ2):
    with bz2.open(fnf) as fd:
        df = pd.read_csv(fd)

    # Convert timestamps to a usable time index (optional).
    df['ts'] = pd.to_datetime(df['ts'], unit='s')
    df.set_index('ts', inplace=True)
    
    # Calculate log returns.
    log_returns = np.log(df / df.shift(1)).dropna()
    
    # Calculate annualized returns and covariance matrix.
    trading_seconds_per_year = 365 * 24 * 60 * 60  # Seconds in a year.
    annualized_returns = log_returns.mean() * trading_seconds_per_year
    annualised_covar = log_returns.cov() * trading_seconds_per_year
    
    # Number of assets.
    num_assets = len(annualized_returns)
    
    print('=== Show CoVariance Matrix ===')
    print(annualised_covar, end="\n\n\n")

    # Define optimization constraints.
    # note: here is where we can define leverage, or allow shorting.
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))

    # Define useful functions:
    def get_returns(weights):
        return np.sum(annualized_returns * weights)

    def get_volatility(weights):
        return np.sqrt(np.dot(weights.T, np.dot(annualised_covar, weights)))
    
    def get_opt_params(weights):
        # Package Relevant fields for optimization.
        weights = np.array(weights)
        rets = get_returns(weights)
        vols = get_volatility(weights)
        return np.array([rets, vols, (rets - risk_free_rate) / vols])

    def summarize(weights, annualized_returns, volatilty):
        return_perc = sum(weights * annualized_returns)
        sharpe_ratio = (return_perc - risk_free_rate) / volatilty
        allocations = {}
        for i, name in enumerate(df.columns.values):
            allocations[name] = weights[i]
        return {
            'return_perc': return_perc,
            'allocations': allocations,
            'sharpe_ratio': sharpe_ratio,
            'volatilty': volatilty
        }

    def show_portfolio(summary):
        print(' Portfolio allocations:')
        for k, v in summary['allocations'].items():
            if v > 0.0001:
                print(f"{k:>21s} : {v*100:5.2f}%")
        print(f" Expected return      : {110 * summary['return_perc']:5.2f}%")
        print(f" Sharpe ratio         : {summary['sharpe_ratio']:5.2f}")
        print(f" Expected volatility  : {110 * summary['volatilty']:5.2f}%")
        print('\n')

    # Maximize the sharpe ratio:
    print('=== Best Sharpe Ratio ===')

    def max_sharpe(weights):
        return -get_opt_params(weights)[2]

    max_sharpe_opts = sco.minimize(
        max_sharpe,
        num_assets * [1. / num_assets, ],
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    max_sharpe_ret, max_sharpe_vol, max_sharpe_sharpe = get_opt_params(max_sharpe_opts['x'])
    max_sharpe_sum = summarize(max_sharpe_opts['x'], annualized_returns, max_sharpe_vol)
    show_portfolio(max_sharpe_sum)
    
    # Minimize variance:
    print('=== Lowest Variance ===')

    def min_variance(weights):
        return get_opt_params(weights)[1] ** 2

    min_var_opts = sco.minimize(
        min_variance,
        num_assets * [1. / num_assets, ],
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    min_var_ret, min_var_vol, min_var_sharpe = get_opt_params(min_var_opts['x'])
    min_var_sum = summarize(min_var_opts['x'], annualized_returns, min_var_vol)
    show_portfolio(min_var_sum)

    # Maximize returns:
    print('=== Maximise Returns ===')

    def max_returns(weights):
        return -get_opt_params(weights)[0]
    
    max_ret_opts = sco.minimize(
        max_returns,
        num_assets * [1. / num_assets, ],
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    max_ret_ret, max_ret_vol, max_ret_sharpe = get_opt_params(max_ret_opts['x'])
    max_ret_sum = summarize(max_ret_opts['x'], annualized_returns, max_ret_vol)
    show_portfolio(max_ret_sum)

    # Simulate a number of portfolios.
    lrets = []
    lvols = []
    for _ in range(5000):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        lrets.append(get_returns(weights))
        lvols.append(get_volatility(weights))
    lrets = np.array(lrets)
    lvols = np.array(lvols)
    
    # Plot these portfolios rets vs vols.
    plt.figure(figsize=(10, 7))
    plt.scatter(lvols, lrets, c=(lrets - risk_free_rate) / lvols, marker='o')
    
    # Place a blue star on highest sharpe ratio portfolio.
    plt.plot(max_sharpe_vol, max_sharpe_ret, 'b*', markersize=15.0, label='Max Sharp')
    # Place a yellow star on highest return portfolio.
    plt.plot(max_ret_vol, max_ret_ret, 'y*', markersize=15.0, label='Max Return')
    # Place a red star on minimal variance portfolio.
    plt.plot(min_var_vol, min_var_ret, 'r*', markersize=15.0, label='Min Variance')
    
    plt.xlabel('Volatility')
    plt.ylabel('Return')
    plt.legend(numpoints=1)
    plt.colorbar(label='Sharpe ratio')
    plt.title('Simulated portfolios')
    
    # Save output image to figs:
    fnf_image = f"{DIR_THIS}/figs/portfolios.png"
    plt.savefig(fnf_image)
    print(f"Saved portfolios image to: {fnf_image}")

    return {
        'max_sharpe': max_sharpe_sum,
        'max_return': max_ret_sum,
        'max_vol': min_var_sum,
    }


def get_best_portfolio(mpt):
    highest_sharpe = mpt['max_sharpe']
    return_perc = round(highest_sharpe['return_perc'] * 100)
    assets = {}
    for name, perc in highest_sharpe['allocations'].items():
        assets[name] = round(perc * 100)
    vol_perc  = round(highest_sharpe['volatilty'] * 100)
    sharpe_ratio = round(highest_sharpe['sharpe_ratio'] * 100)

    print(f'Allocations for best sharpe ratio portfolio:')
    asorted = sorted([(v,k) for k,v in assets.items()], reverse=True)
    for alloc, asset in asorted:
        print(f'{asset.upper():>15s}: {alloc:>5d} %')
    print(f'Expected return: {return_perc:>5d} %')
    print(f'     Volatility: {vol_perc:>5d} %')
    print(f'   Sharpe Ratio: {sharpe_ratio:>5d} %')

    return {
        'allocations': assets,
        'returns': return_perc,
        'sharpe': sharpe_ratio,
        'volatility': vol_perc,
    }


if __name__ == '__main__':
    mpt = get_mpt()
    portfolio = get_best_portfolio(mpt)
    print(portfolio)
