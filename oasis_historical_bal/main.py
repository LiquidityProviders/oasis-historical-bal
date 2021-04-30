
import sys
import json
import requests
import argparse
from web3 import Web3, HTTPProvider
from pprint import pprint
from pymaker import Address, web3_via_http, Wad, Contract
from pymaker.model import Token
from pymaker.oasis import MatchingMarket


class OasisHistoricalBal:

    def __init__(self, args: list):
        parser = argparse.ArgumentParser(prog='oasis-historic-balances')

        parser.add_argument("--rpc-host", type=str, default="http://localhost:8545",
                            help="JSON-RPC endpoint URI with port (default: `http://localhost:8545')")

        parser.add_argument("--rpc-timeout", type=int, default=10,
                            help="JSON-RPC timeout (in seconds, default: 10)")

        parser.add_argument("--addresses-config", required=True, type=argparse.FileType('r'),
                            help="configuration file to identify Oasis and our respective oasis market maker account addresses.")

        parser.add_argument('--block-number-to-query', type=int, default=None,
                            help="block from which to pull at historical Dydx balances")


        self.arguments = parser.parse_args(args)
        self.block_number = self.arguments.block_number_to_query if self.arguments.block_number_to_query else 'latest'
        self.web3 = Web3(HTTPProvider(endpoint_uri=self.arguments.rpc_host))
        print(f"URL (Ethereum Node) Endpoint - {self.arguments.rpc_host}")
        print(f"Client Verion - {self.web3.clientVersion} ")
        print(f"The blocknumber where balances are requested: {self.block_number}")

        address_config = json.loads(self.arguments.addresses_config.read())

        self.members = address_config['members']
        self.tokens = address_config['tokens']
        self.pairs = address_config['pairs']

    def get_token(self, symbol):
        decimal = self.tokens[symbol].get('tokenDecimals') if self.tokens[symbol].get('tokenDecimals') else 18
        return Token(symbol, Address(self.tokens[symbol]['tokenAddress']), decimal)


    def get_balance(self, oasis,  member):
        balances = {}
        for member_token1 in self.tokens:
            balance_in_our_sell_orders = Wad(0)
            for member_token2 in self.tokens:
                token1 = self.get_token(member_token1)
                token2 = self.get_token(member_token2)
                if token1.address != token2.address:
                    orders = oasis.get_orders(token1, token2, self.block_number)
                    our_sell_orders = filter(lambda order: order.maker == Address(member['config']['marketMakerAddress']), orders)
                    balance_in_our_sell_orders += sum(map(lambda order: order.pay_amount, our_sell_orders), Wad(0))

            if balance_in_our_sell_orders != Wad(0):
                balances[token1.name] = token1.normalize_amount(balance_in_our_sell_orders).value / 10**18

        return balances



    def add_member_to_total(self, total, member):

        if type(member) == str:
            return total

        for symbol, balance in member['balances'].items():

            if total.get(symbol):
                total[symbol] += balance

            else:
                total[symbol] = balance

        return total


    def main(self):
        total = {}
        member_balances = {}

        for member in self.members:
            if member['type'] == 'oasis-market-maker-keeper':
                member_balances[member['id']] = {
                        'address': '',
                        'balances': {}
                        }
                member_balances[member['id']]['address'] = member['config']['marketMakerAddress']
                oasis = MatchingMarket(self.web3, Address(member['config']['oasisAddress']))
                member_balances[member['id']]['balances'] = self.get_balance(oasis, member)

                total = self.add_member_to_total(total, member_balances[member['id']])

        print(f"--- MEMBERS ---: ")
        pprint(member_balances)
        print(f"--- TOTALS ---: ")
        pprint(total)





if __name__ == '__main__':
    OasisHistoricalBal(sys.argv[1:]).main()
