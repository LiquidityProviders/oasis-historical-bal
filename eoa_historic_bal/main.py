
import sys
import json
import requests
import argparse
from web3 import Web3, HTTPProvider
from eoa_historic_bal.token_contract import TokenContract
from pprint import pprint
from pymaker import Address, web3_via_http, Wad, Contract
from pymaker.token import ERC20Token


class EoaHistoricBalances:

    def __init__(self, args: list):
        parser = argparse.ArgumentParser(prog='eoa-historic-balances')

        parser.add_argument("--rpc-host", type=str, default="http://localhost:8545",
                            help="JSON-RPC endpoint URI with port (default: `http://localhost:8545')")

        parser.add_argument("--rpc-timeout", type=int, default=10,
                            help="JSON-RPC timeout (in seconds, default: 10)")

        parser.add_argument("--addresses-config", required=True, type=argparse.FileType('r'),
                            help="configuration file to identify DYDX addresses.")

        parser.add_argument('--block-number-to-query', type=int, default=None,
                            help="block from which to pull at historical Dydx balances")


        self.arguments = parser.parse_args(args)
        self.block_number = self.arguments.block_number_to_query if self.arguments.block_number_to_query else 'latest'
        self.web3 = Web3(HTTPProvider(endpoint_uri=self.arguments.rpc_host))
        print(f"URL (Ethereum Node) Endpoint - {self.arguments.rpc_host}")
        print(f"Client Verion - {self.web3.clientVersion} ")
        print(f"The blocknumber where balances are requested: {self.block_number}")

        address_config = json.loads(self.arguments.addresses_config.read())

        self.members= self.extract_members(address_config)
        self.tokens = address_config['tokens']


    def extract_members(self, json_config):
        members = json_config['members']
        members.insert(0, json_config['reserve'])
        return members


    def get_balance(self, address):
        balances = {}
        for symbol, address_dict in self.tokens.items():

           decimal = address_dict.get('tokenDecimals') if address_dict.get('tokenDecimals') else 18

           if symbol == 'ETH':
               token_bal = self.web3.eth.getBalance(address, self.block_number) / 10**decimal

           else:
               wad_token_bal = ERC20Token(web3=self.web3, address=Address(address_dict['tokenAddress'])).balance_at_block(Address(address), self.block_number)
               token_bal = wad_token_bal.value / 10**decimal

           if token_bal != 0.0:
               balances[symbol] = token_bal

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
            member_balances[member['id']] = {
                    'address': '',
                    'balances': {}
                    }

            if member['type'] == 'oasis-market-maker-keeper' or \
               member['type'] == 'uniswapv2-market-maker-keeper' or \
               member['type'] == 'dydx-market-maker-keeper' or \
               member['type'] == 'idex-market-maker-keeper' or \
               member['type'] == 'radarrelay-market-maker-keeper':
                   member_balances[member['id']]['balances'] = self.get_balance(member['config']['marketMakerAddress'])
                   member_balances[member['id']]['address'] = member['config']['marketMakerAddress']

            elif member['type'] == 'ethereum-account' or \
                 member['type'] == 'reserve-account' or \
                 member['type'] == 'auction-keeper':
                   member_balances[member['id']]['balances'] = self.get_balance(member['config']['address'])
                   member_balances[member['id']]['address'] = member['config']['address']

            elif member['type'] == 'imtoken-market-maker-keeper':
                   member_balances[member['id']]['balances'] = self.get_balance(member['config']['marketMakerProxyAddress'])
                   member_balances[member['id']]['address'] = member['config']['marketMakerProxyAddress']

            else:
                   member_balances[member['id']] = 'No Ethereum address to pull balances for'

            total = self.add_member_to_total(total, member_balances[member['id']])

        print(f"--- MEMBERS ---: ")
        pprint(member_balances)
        print(f"--- TOTALS ---: ")
        pprint(total)


if __name__ == '__main__':
    EoaHistoricBalances(sys.argv[1:]).main()
