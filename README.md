# RLUSD-MPT

RLUSD (Ripple USD) Modern Portfolio Theory (MPT) guides DeFi investors in balancing risk and reward. 

It helps maximize returns for a specific risk level or minimize risk for a target return by diversifying investments. By combining assets with different risks and correlations, MPT aims to reduce overall portfolio risk and achieve optimal performance.

## Overview

Modern Portfolio Theory (MPT) is a foundational concept in finance that focuses on optimizing asset allocation to achieve the best trade-off between risk and reward. 

RLUSD-MPT applies this methodology to the volatile and diverse cryptocurrency market, providing portfolio recommendations that are stored on-chain for transparency and accessibility.

In this project, we:

1. __Analyze Historical Data__: Gather crypto pricing data using decentralized oracles (e.g., ChainLink).
2. __Optimize Portfolios__: Apply MPT to generate three portfolio strategies:
   - Minimized Risk: Prioritizes stability in a volatile market.
   - Maximized Returns: Focuses on growth potential.
   - Optimal Sharpe Ratio: Balances risk and reward effectively. 
3. __Store Allocations On-Chain__: Publish optimized allocations to a smart contract deployed on multiple blockchains, ensuring transparency and global accessibility.
4. __Combine RLUSD__ with __Smart Contracts__ to transparently benefit from optimized portfolios. 

## How it works

RLUSD-MPT is divided into 3 main sections. On the first one, primarily inside the ```./datasource``` folder, we retrieve historical data from ChainLink oracles. The second section, inside ```./mpt```, involves analyzing prices and generating exploring correlations between them to create portfolios with certain risk/rewards. Finally, using ```./contract```,we store the details of certain asset allocations on various chains for easy of use and to used as a building block for more advanced operations.

1. __Data Collection__:

   - Historical price data is gathered using ChainLink oracles. Example assets include XRP, Bitcoin, Ethereum, Solana, UniSwap, ChainLink, Dogecoin, Pepe.

2. __Analysis and Optimization__:

   - Variance and covariance are calculated for the assets.
   - MPT is applied to generate three portfolio strategies: Min Risk, Max Return, and Optimal Sharpe Ratio.

3. __On-Chain Deployment__:

   - Optimized allocations are stored in a Solidity smart contract, RLUSDMPT.sol.
   - Allocations are mapped to week numbers derived from timestamps for efficient data lookup.

4. __Accessing the Data__:
   - Anyone can query the smart contract to retrieve the latest portfolio allocations.

## Test deployments

This project's smart-contract was deployed, and __verified__, using Sepolia's Testnet:


  * Sepolia Testnet: [0x284dae20099c497b97cc1992f2c484922686cf53](https://sepolia.etherscan.io/address/0x284dae20099c497b97cc1992f2c484922686cf53#code)


## Presentation

This project's presentation is available [here](./RLUSD-MPT.pdf).

### About the author

António Roldão is the creator of RLUSD-MPT. António is an entrepreneur and a passionate technologist with a Ph.D. in Electronics and Computer Engineering from Imperial College London. Antonio’s career spans diverse fields, including aerospace, finance, and artificial intelligence. He is the co-founder and CEO of [muse.ai](https://muse.ai), where he has pioneered advanced video search technology leveraging cutting-edge AI. Antonio combines deep technical expertise with a drive to create technologies that empower people and simplify complexity.

## Contributing
We welcome contributions to enhance RLUSD-MPT! Please submit issues or pull requests to this repository.

## License
This project is licensed under the MIT License.

