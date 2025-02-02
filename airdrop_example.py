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

"""Airdrop example"""

from packages.airdrop import Airdrop
import json

#############################################################################
# WARNING: the airdrop tool requires API keys or RPCs to be set             #
# in a .env file. Please rename the sample.env file to .env and fill in the #
# RPCs/keys you need to retrieve the required data.                         #
#############################################################################

# Prepare the airdrop parameters
parameters = {
    "token_allocation_per_weight_unit": 1,
    "blocks": {  # only for holders, stakers (ethereum only) and bonders (ethereum only)
        "ethereum": "latest",
        "arbitrum": "latest",
        "polygon": "latest",
        "gnosis": "latest",
        "base": "latest",
        "optimism": "latest",
    },

    # Contributors
    "weight_per_contributor": 1,
    "min_contribute_points": 100,
    "use_decile_based_multiplier": True,

    # Voters
    "weight_per_vote": 1,
    "min_votes": 1,

    # veOLAS holders
    "weight_per_veolas_holder": 1,
    "min_voting_power": 1,

    # OLAS holders
    "weight_per_olas_holder": 1,
    "min_olas_balance_wei": int(100e18),
    "constant_reward": True,  # same amount for olas holder. Set to False to make it proportional to balances

    # Bonders
    "weight_per_bonder": 1,
    "min_bond_amount": 100,

    # Component NFT owners
    "weight_per_nft_owner": 1,

    # Stakers
    "weight_per_staker": 1,

    # Skip wallets
    "skip_wallets": [],
}

# Instantiate the airdrop
airdrop = Airdrop(parameters)

# Calculate rewards (takes up to a few minutes)
rewards = airdrop.calculate(csv_dump=True)
print("Rewards\n", json.dumps(rewards, indent=4))