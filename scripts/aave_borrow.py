from brownie import network, config, interface
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3

amount = Web3.toWei(0.01, "ether")

def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    #get_weth() since we alreay had done this process of getting wth we are not going to execute it now
    if network.show_active() in ["mainnet-fork-dev"]:
        get_weth()

    #ABI
    #Address
    lending_pool = get_lending_pool()
    print(lending_pool)
    # Approve sending ERC20tokens
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    print("Depositing...")
    # function deposit(address asset, uint256 amount, address onBehalfOf, uint16 referralCode)
    tx = lending_pool.deposit(erc20_address,amount, account.address, 0, {"from": account})
    tx.wait(1)
    print("Deposited")

    # how much to be borrowed?
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)

    print("Let's borrow...")

    #DAI interms of ETH
    dai_eth_price = get_asset_price(config["networks"][network.show_active()]["dai_eth_price_feed"])
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.5)
    print("We are going to borrow", amount_dai_to_borrow, "DAI")
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"), 
        1, 
        0,
        account.address, 
        {"from": account}
    )
    borrow_tx.wait(1)
    print("Borrowed some dai")
    get_borrowable_data(lending_pool, account)
    #gives info about accounts
    # repay_all(amount, lending_pool, account)
    print("DONE")

def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account}
    )
    repay_tx.wait(1)
    # print("You just deposited, borrowed and repaid with aave brownie and hainlink")
    # get_borrowable_data(lending_pool, account)




def get_asset_price(price_feed_address):
    #ABI
    #Address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    price= dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(price, "ether")
    print("The DAI/ETH price is", converted_latest_price)
    return price


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor
    ) = lending_pool.getUserAccountData(account.address)

    available_borrow_eth = available_borrow_eth
    total_collateral_eth = total_collateral_eth
    total_debt_eth = total_debt_eth
    print("You can borrow",available_borrow_eth, "worth of ETH")
    print("You have", total_collateral_eth,"worth of ETH deposited")
    print("You have", total_debt_eth,"worth of ETH in debt")
    return (float(Web3.fromWei(available_borrow_eth,"ether")), float(Web3.fromWei(total_debt_eth,"ether")))

def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)  #wait for ine block confirmation
    print("Approved!")
    return tx
    #ABI
    #Address
    # pass

def get_lending_pool():
    #ABI
    #Address
    lending_pool_address_provider = interface.ILendingPoolAddressProvider(
        config['networks'][network.show_active()]["lending_pool_address_provider"]
    )
    lending_pool_address = lending_pool_address_provider.getLendingPool()
    #ABI
    #Address
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool

    
