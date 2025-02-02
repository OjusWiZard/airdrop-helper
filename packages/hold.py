# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2021-2024 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""Hold"""

import csv
import os
from pathlib import Path

from packages.constants import CONTRACTS
from packages.erc20_parser import ERC20Parser


class veOLAS:
    """veOLAS"""

    def __init__(self, contract_manager) -> None:
        """Initializer"""
        self.contract_manager = contract_manager
        if "ethereum" not in self.contract_manager.skip_chains:
            self.veolas = contract_manager.contracts["ethereum"]["other"]["veolas"]
            self.wveolas = contract_manager.contracts["ethereum"]["other"]["wveolas"]

    def _get_veolas_holders(self, block=None):
        """Get events"""
        deposits = self.veolas.events.Deposit.create_filter(
            fromBlock="earliest",
            toBlock=block if block else "latest",
        ).get_all_entries()

        withdraws = self.veolas.events.Withdraw.create_filter(
            fromBlock="earliest",
            toBlock=block if block else "latest",
        ).get_all_entries()

        addresses = set()
        for event in deposits + withdraws:
            addresses.add(event.address)
            addresses.add(event.args.account)  # TODO: do we need both?

        return list(addresses)

    def get(self, block, min_power=0, csv_dump=False):
        """Get voting power per holder"""
        if "ethereum" in self.contract_manager.skip_chains:
            print("Warning: Missing ETHEREUM_RPC. Skipping call to Ethereum chain")
            return {}

        if block == "latest":
            block = (
                self.contract_manager.apis["ethereum"].eth.get_block("latest").number
            )

        holders = self._get_veolas_holders(block)

        address_to_votes = {
            address: self.wveolas.functions.getPastVotes(address, block).call() / 1e18
            for address in holders
        }

        address_to_votes = {k: v for k, v in address_to_votes.items() if v >= min_power}

        if csv_dump:
            self.dump(address_to_votes)

        return address_to_votes

    def dump(self, address_to_votes):
        """Write to csv"""
        with open(Path("data", "veolas_power.csv"), "w") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(["address", "veolas_power"])
            writer.writerows(list(address_to_votes.items()))


class OLAS:
    """OLAS"""

    DEPLOYMENT_BLOCKS = {
        "ethereum": 15000000,
        "gnosis": 30254468,
        "arbitrum": 173139043,
        "polygon": 50976704,
        "base": 12393538,
        "optimism": 117443138,
    }

    def __init__(self, contract_manager) -> None:
        """Initializer"""
        self.contract_manager = contract_manager
        if "ethereum" not in self.contract_manager.skip_chains:
            self.contracts = contract_manager.contracts

    def get(self, blocks, min_balance_wei=0, csv_dump=False):
        """Get voting power per holder"""

        address_to_balance = {}
        for chain_name in blocks.keys():
            if chain_name in self.contract_manager.skip_chains:
                print(
                    f"Warning: Missing {chain_name.upper()}_RPC. Skipping call to {chain_name} chain"
                )
                continue

            block = blocks[chain_name]

            if block == "latest":
                block = (
                    self.contract_manager.apis[chain_name]
                    .eth.get_block("latest")
                    .number
                )

            # Parse events
            olas_contract = self.contracts[chain_name]["other"]["olas"]
            events_csv_file = Path("data", f"events_{chain_name}.csv")
            balances_json_file = Path("data", f"balances_{chain_name}.json")
            token_parser = ERC20Parser(
                olas_contract, chain_name, events_csv_file, balances_json_file
            )

            if not os.path.isfile(events_csv_file):
                token_parser.parse_transfer_events(
                    from_block=self.DEPLOYMENT_BLOCKS[chain_name], to_block=block
                )
            else:
                print(
                    f"Event file found: {events_csv_file}. Using that file instead fo pulling events from the chain."
                )
            token_parser.sort_events()
            token_parser.clean_event_duplications()
            token_parser.build_balance_history()

            # Add balances
            for address in token_parser.balances.keys():
                balance = token_parser.get_balance(address, block)
                address_to_balance[address] = (
                    address_to_balance.get(address, 0) + balance
                )

        # Filter addresses
        address_to_balance = dict(
            filter(lambda item: item[1] >= min_balance_wei, address_to_balance.items())
        )

        if csv_dump:
            self.dump(address_to_balance)

        return address_to_balance

    def dump(self, address_to_balance):
        """Write to csv"""
        with open(Path("data", "olas_balances.csv"), "w") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(["address", "balance"])
            writer.writerows(list(address_to_balance.items()))
