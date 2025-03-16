// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Interface for UniSwap Router to interact with UniSwap V2 for token swaps.
interface IUniswapV2Router02 {
    // Get the amount of tokens out for a given input amount.
    function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);

    // Execute a token swap from one token to another.
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
}

// ERC20 Token interface to allow interaction with tokens (transfer, transferFrom, approve).
interface IERC20 {
    function transfer(address recipient, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract RLUSDMPT {
    // UniSwap Router for token swaps.
    IUniswapV2Router02 public uniswapRouter;

    // Uniswap V2 Router address.
    address public uniswapRouterAddress = 0xeE567Fe1712Faf6149d80dA1E6934E354124CfE3;

    // wethToken address.
    address public wethToken = 0x7b79995e5f793A07Bc00c21412e50Ecae098E7f9;
    // rlusdToken address.
    address public rlusdToken = 0xe101FB315a64cDa9944E570a7bFfaFE60b994b1D;

    // Array to hold the addresses of the 2 assets.
    address[] public assets = [
        0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984,  // UNI
        0x779877A7B0D9E8603169DdbD7836e478b4624789   // LINK
    ];

    // Mapping to track the amount of each asset held by a user.
    // userAssets[address][assetIndex] = amount
    mapping(address => uint[2]) public userAssets;

    // Mapping to track the deposited balance of each user.
    mapping(address => uint256) public balances;

    // Array to store the allocation percentages for each of the 2 assets.
    uint[2] public weights;

    // Constructor initializes the contract with the rlusd token address, UniSwap router, and the asset token addresses.
    constructor() {
        // Assign UniSwap router address.
        uniswapRouter = IUniswapV2Router02(uniswapRouterAddress);
    }

    // Function to set the weights for the 2 assets.
    // Weights should sum up to 100%.
    function setWeights(uint[2] calldata _weights) external {
        uint totalWeight = 0;
        // Calculate total weight to ensure it's 100%.
        for (uint i = 0; i < _weights.length; i++) {
            totalWeight += _weights[i];
        }
        // Check that total weight is 100%.
        require(totalWeight == 100, "Total weight must sum to 100%");
        // Set the weights for the 2 assets.
        weights = _weights;
    }

    // Deposit function that allows a user to deposit rlusd and convert it into the 2 assets based on the set weights.
    function deposit(uint _rlusdAmount) external {
        // Transfer rlusd tokens from the user to the contract.
        require(IERC20(rlusdToken).transferFrom(msg.sender, address(this), _rlusdAmount), "Transfer failed");
        // Update the user's deposit balance.
        balances[msg.sender] += _rlusdAmount;
    }

    function deposit_rlusd(uint _rlusdAmount) external {
         // Transfer rlusd tokens from the sender to the contract.
         require(IERC20(rlusdToken).transferFrom(msg.sender, address(this), _rlusdAmount), "Transfer failed");

         // Loop through each asset and perform the conversion.
         for (uint i = 0; i < assets.length; i++) {
             // Calculate how much of each asset the user will receive.
             uint assetAmount = (_rlusdAmount * weights[i]) / 100;
             // Convert rlusd to the specific asset.
             _convertRlusdToAsset(assetAmount, assets[i]);
             // Update the user's asset balance.
             userAssets[msg.sender][i] += assetAmount;
         }
    }

    // Helper function to perform the conversion of rlusd to the specified asset using UniSwap.
    function _convertRlusdToAsset(uint _amountIn, address _assetOut) internal {
        // Define the token conversion path (rlusd -> weth -> asset).
        address[] memory path = new address[](3);
        path[0] = rlusdToken;
        path[1] = wethToken;
        path[2] = _assetOut;

        // Get the minimum amount of the output token we will receive based on current UniSwap rates.
        uint[] memory amountsOut = uniswapRouter.getAmountsOut(_amountIn, path);
        uint amountOutMin = amountsOut[1]; // This is the minimum amount of the asset we should receive.

        // Approve UniSwap to spend the rlusd tokens on behalf of the contract.
        IERC20(rlusdToken).approve(address(uniswapRouter), _amountIn);

        // Execute the token swap on UniSwap
        uniswapRouter.swapExactTokensForTokens(_amountIn, amountOutMin, path, address(this), block.timestamp);
    }

    // Withdraw function allows a user to withdraw their assets, converting them back to rlusd.
    function withdraw(uint256 _amount) external {
        // Check that the user has enough balance to withdraw.
        require(balances[msg.sender] >= _amount, "Insufficient balance");

        // Update the user's deposit balance.
        balances[msg.sender] -= _amount;

        // Transfer the rlusd tokens from the contract back to the user.
        require(IERC20(rlusdToken).transfer(msg.sender, _amount), "Transfer failed");
    }

     function withdraw_rlusd(uint[2] calldata _amounts) external {
         uint rlusdAmount = 0;
         // Loop through each asset and convert the specified amounts back to rlusd.
         for (uint i = 0; i < _amounts.length; i++) {
             if(userAssets[msg.sender][i] >= 0) {
                 uint assetAmount = _amounts[i];
                 userAssets[msg.sender][i] -= assetAmount; // Update user's asset balance by subtracting the withdrawn amount.

                 // Convert the asset to rlusd.
                 uint amountOut = _convertAssetToRlusd(assetAmount, assets[i]);
                 // Add the value to the total rlusd amount.
                 rlusdAmount += amountOut;
             }
         }
         // Transfer the accumulated rlusd back to the user.
         require(IERC20(rlusdToken).transfer(msg.sender, rlusdAmount), "Transfer failed");
     }

    // Helper function to convert a specific asset back into rlusd using UniSwap.
    function _convertAssetToRlusd(uint _amountIn, address _assetIn) internal returns (uint) {
        // Define the token conversion path (rlusd -> weth -> asset).
        address[] memory path = new address[](3);
        path[0] = _assetIn;
        path[1] = wethToken;
        path[2] = rlusdToken;

        // Get the minimum amount of rlusd we will receive based on current UniSwap rates.
        uint[] memory amountsOut = uniswapRouter.getAmountsOut(_amountIn, path);
        // This is the minimum amount of rlusd we should receive
        uint amountOutMin = amountsOut[1];

        // Approve UniSwap to spend the asset on behalf of the contract.
        IERC20(_assetIn).approve(address(uniswapRouter), _amountIn);

        // Execute the token swap on UniSwap.
        uniswapRouter.swapExactTokensForTokens(_amountIn, amountOutMin, path, address(this), block.timestamp);

        // Return the amount of rlusd received.
        return amountOutMin;
    }

    // Function to get the total value of the user's portfolio in rlusd.
    // It sums the value of each asset the user holds.
    function getValue(address _user) external view returns (uint totalValue) {
        totalValue = 0;
        // Loop through each asset and calculate the total value in rlusd.
        for (uint i = 0; i < assets.length; i++) {
            uint assetAmount = userAssets[_user][i];
            // Add the value of each asset to the total.
            totalValue += _getAssetValueInRlusd(assetAmount, assets[i]);
        }
    }

    // Helper function to get the value of a single asset in rlusd using UniSwap.
    function _getAssetValueInRlusd(uint _amountIn, address _asset) internal view returns (uint) {
        // Define the token conversion path (rlusd -> weth -> asset).
        address[] memory path = new address[](3);
        path[0] = _asset;
        path[1] = wethToken;
        path[2] = rlusdToken;

        // Get the output amount of rlusd for the given input amount of the asset.
        uint[] memory amountsOut = uniswapRouter.getAmountsOut(_amountIn, path);
        return amountsOut[1]; // Return the estimated amount of rlusd.
    }

    // Function to get the amount of each asset the user holds.
    function getAssets(address _user) external view returns (uint[2] memory) {
        // Return the array of asset holdings for the user.
        return userAssets[_user];
    }
}