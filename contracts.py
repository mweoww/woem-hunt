"""
contracts.py - Interaksi dengan smart contract di Base
"""

from web3 import Web3
from eth_account import Account
from config import (
    BASE_RPC_URL,
    PROBLEM_MANAGER_ADDRESS,
    REWARD_DISTRIBUTOR_ADDRESS,
    AGENT_REGISTRY_ADDRESS,
    AGC_TOKEN_ADDRESS
)

# Inisialisasi Web3
w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))

# ===== PROBLEM MANAGER =====
PROBLEM_MANAGER_ABI = [
    {
        "inputs": [
            {"name": "problemId", "type": "uint256"},
            {"name": "answer", "type": "uint256"}
        ],
        "name": "submitAnswer",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "problemId", "type": "uint256"}],
        "name": "getProblem",
        "outputs": [
            {"name": "templateHash", "type": "bytes32"},
            {"name": "state", "type": "uint8"},
            {"name": "deadline", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# ===== REWARD DISTRIBUTOR =====
REWARD_DISTRIBUTOR_ABI = [
    {
        "inputs": [],
        "name": "claimRewards",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "agent", "type": "address"}],
        "name": "getClaimable",
        "outputs": [{"name": "amount", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# ===== AGENT REGISTRY =====
AGENT_REGISTRY_ABI = [
    {
        "inputs": [{"name": "wallet", "type": "address"}],
        "name": "getAgentId",
        "outputs": [{"name": "agentId", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

problem_manager = w3.eth.contract(
    address=PROBLEM_MANAGER_ADDRESS,
    abi=PROBLEM_MANAGER_ABI
)

reward_distributor = w3.eth.contract(
    address=REWARD_DISTRIBUTOR_ADDRESS,
    abi=REWARD_DISTRIBUTOR_ABI
)

agent_registry = w3.eth.contract(
    address=AGENT_REGISTRY_ADDRESS,
    abi=AGENT_REGISTRY_ABI
)

def submit_answer(account, problem_id, answer):
    """Submit answer ke on-chain"""
    if not account:
        print("❌ Account tidak valid")
        return None
        
    try:
        tx = problem_manager.functions.submitAnswer(
            problem_id, 
            answer
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'chainId': 8453  # Base mainnet
        })
        
        signed = account.sign_transaction(tx)
        # FIX: pake raw_transaction (underscore)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        return tx_hash.hex()
    except Exception as e:
        print(f"❌ Submit error: {e}")
        return None

def get_agent_id(account):
    """Dapatkan agent ID dari registry"""
    if not account:
        return None
    try:
        agent_id = agent_registry.functions.getAgentId(account.address).call()
        return agent_id
    except Exception as e:
        print(f"⚠️ Gagal get agent ID: {e}")
        return None

def get_claimable_rewards(account):
    """Cek reward yang bisa di-claim"""
    if not account:
        return 0
    try:
        amount = reward_distributor.functions.getClaimable(account.address).call()
        return amount / 1e18  # AGC 18 decimals
    except Exception as e:
        # Ini normal kalau belum ada reward
        return 0

def claim_rewards(account):
    """Claim reward"""
    if not account:
        return None
    try:
        tx = reward_distributor.functions.claimRewards().build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'chainId': 8453
        })
        
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        return tx_hash.hex()
    except Exception as e:
        print(f"❌ Claim error: {e}")
        return None
