"""
contracts.py - Interaksi dengan smart contract di Base
FIX: Tangkap revert reason dengan jelas
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
            {"name": "state", "type": "uint8"},
            {"name": "deadline", "type": "uint256"},
            {"name": "winnerCount", "type": "uint256"},
            {"name": "totalSubmissions", "type": "uint256"}
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
            {"name": "answer", "type": "uint256"},
            {"name": "isWinner", "type": "bool"}
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

# ===== AGC TOKEN =====
AGC_TOKEN_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]

# Init contracts
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

agc_token = w3.eth.contract(
    address=AGC_TOKEN_ADDRESS,
    abi=AGC_TOKEN_ABI
)

def get_agc_balance(account):
    """Cek balance AGC token"""
    if not account:
        return 0
    try:
        balance = agc_token.functions.balanceOf(account.address).call()
        return balance / 1e18
    except:
        return 0

def check_problem_status(problem_id):
    """Cek status problem sebelum submit"""
    try:
        result = problem_manager.functions.getProblem(problem_id).call()
        
        if len(result) >= 3:
            state = result[1]
            deadline = result[2]
            
            state_names = ["Open", "Verification", "Settled", "Expired"]
            state_name = state_names[state] if state < len(state_names) else f"Unknown({state})"
            
            print(f"🔍 Problem #{problem_id}: {state_name}, Deadline: {deadline}")
            
            if state != 0:
                print(f"❌ Problem state = {state_name}, bukan Open")
                return False
            if deadline > 0 and time.time() > deadline:
                print(f"❌ Deadline sudah lewat")
                return False
            return True
    except Exception as e:
        print(f"⚠️ Gagal cek problem: {e}")
    return True  # Allow if can't check

def check_already_submitted(account, problem_id):
    """Cek apakah sudah pernah submit"""
    try:
        result = problem_manager.functions.getSubmission(problem_id, account.address).call()
        submitted = result[0] if result else False
        if submitted:
            print(f"⚠️ Already submitted for problem #{problem_id}")
            return True
    except:
        pass
    return False

def submit_answer(account, problem_id, answer):
    """Submit answer dengan penangkapan revert reason yang jelas"""
    if not account:
        return None
    
    # CEK 1: Balance AGC (minimal 100)
    agc_balance = get_agc_balance(account)
    print(f"💰 AGC Balance: {agc_balance}")
    if agc_balance < 100:
        print(f"❌ Balance AGC {agc_balance} < 100, tidak bisa submit")
        return None
    
    # CEK 2: Problem masih open?
    if not check_problem_status(problem_id):
        return None
    
    # CEK 3: Udah pernah submit?
    if check_already_submitted(account, problem_id):
        return None
    
    try:
        # Estimate gas
        try:
            gas_estimate = problem_manager.functions.submitAnswer(
                problem_id, answer
            ).estimate_gas({'from': account.address})
            print(f"  - Estimated gas: {gas_estimate}")
        except Exception as e:
            print(f"⚠️ Gas estimation failed, coba tangkap revert reason...")
            # Coba simulasi untuk dapat revert reason
            try:
                problem_manager.functions.submitAnswer(problem_id, answer).call({
                    'from': account.address
                })
            except Exception as call_error:
                print(f"🔍 REVERT REASON: {call_error}")
                return None
            gas_estimate = 300000
        
        tx = problem_manager.functions.submitAnswer(
            problem_id, answer
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': int(gas_estimate * 1.5),
            'gasPrice': w3.eth.gas_price,
            'chainId': 8453
        })
        
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        
        print(f"⏳ Menunggu konfirmasi...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        
        if receipt.status == 1:
            print(f"✅ SUCCESS! Gas used: {receipt.gasUsed}")
            return tx_hash.hex()
        else:
            print(f"❌ FAILED! Status: {receipt.status}")
            # Coba ambil revert reason
            try:
                w3.eth.call(tx, block_identifier='latest')
            except Exception as call_error:
                print(f"🔍 REVERT REASON: {call_error}")
            return None
            
    except Exception as e:
        print(f"❌ Submit error: {e}")
        return None

def get_agent_id(account):
    if not account:
        return None
    try:
        return agent_registry.functions.getAgentId(account.address).call()
    except:
        return None

def get_claimable_rewards(account):
    if not account:
        return 0
    try:
        amount = reward_distributor.functions.getClaimable(account.address).call()
        return amount / 1e18
    except:
        return 0

def claim_rewards(account):
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
