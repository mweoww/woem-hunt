"""
contracts.py - Interaksi dengan smart contract di Base
FIX: Anti revert dengan pengecekan lengkap
"""

from web3 import Web3
from eth_account import Account
import time
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
            {"name": "state", "type": "uint8"},  # 0=Open, 1=Verification, 2=Settled
            {"name": "deadline", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "problemId", "type": "uint256"},
            {"name": "agent", "type": "address"}
        ],
        "name": "getSubmission",
        "outputs": [
            {"name": "submitted", "type": "bool"},
            {"name": "answer", "type": "uint256"}
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

def check_problem_status(problem_id):
    """Cek status problem sebelum submit"""
    try:
        problem = problem_manager.functions.getProblem(problem_id).call()
        state = problem[1]  # 0=Open, 1=Verification, 2=Settled
        deadline = problem[2]
        
        print(f"🔍 Problem #{problem_id}:")
        print(f"  - State: {['Open', 'Verification', 'Settled'][state]}")
        print(f"  - Deadline: {deadline} ({time.ctime(deadline) if deadline > 0 else 'No deadline'})")
        
        # Cek apakah masih bisa submit
        if state != 0:
            print(f"❌ Problem sudah tidak bisa di-submit (state={state})")
            return False
        if deadline > 0 and time.time() > deadline:
            print(f"❌ Problem sudah lewat deadline")
            return False
            
        return True
    except Exception as e:
        print(f"⚠️ Gagal cek problem: {e}")
        return True  # Allow if can't check

def check_already_submitted(account, problem_id):
    """Cek apakah sudah pernah submit untuk problem ini"""
    try:
        submitted, answer = problem_manager.functions.getSubmission(problem_id, account.address).call()
        if submitted:
            print(f"⚠️ Already submitted answer {answer} for problem #{problem_id}")
            return True
        return False
    except:
        # Function mungkin gak ada, assume belum submit
        return False

def submit_answer(account, problem_id, answer):
    """Submit answer ke on-chain dengan pengecekan lengkap"""
    if not account:
        print("❌ Account tidak valid")
        return None
    
    # CEK 1: Problem masih open?
    if not check_problem_status(problem_id):
        print("❌ Skip submit karena problem tidak valid")
        return None
    
    # CEK 2: Udah pernah submit?
    if check_already_submitted(account, problem_id):
        print("❌ Skip submit karena sudah pernah")
        return None
    
    try:
        # Estimate gas dulu
        gas_estimate = problem_manager.functions.submitAnswer(
            problem_id, answer
        ).estimate_gas({'from': account.address})
        
        tx = problem_manager.functions.submitAnswer(
            problem_id, 
            answer
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': int(gas_estimate * 1.2),  # +20% buffer
            'gasPrice': w3.eth.gas_price,
            'chainId': 8453  # Base mainnet
        })
        
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        
        # Tunggu receipt
        print(f"⏳ Menunggu konfirmasi...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        
        if receipt.status == 1:
            print(f"✅ SUCCESS! Gas used: {receipt.gasUsed}")
            return tx_hash.hex()
        else:
            print(f"❌ FAILED! Status: {receipt.status}")
            # Coba ambil revert reason
            try:
                # replay transaction to get error
                w3.eth.call(tx, block_identifier='latest')
            except Exception as e:
                print(f"🔍 Revert reason: {str(e)}")
            return None
            
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
        return amount / 1e18
    except:
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
