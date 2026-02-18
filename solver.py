"""
solver.py - Menjawab soal matematika dengan presisi tinggi
"""

import re
import math

def solve_math_problem(problem_text):
    """
    Memecahkan soal matematika dengan berbagai pola
    """
    print(f"🔍 Solving: {problem_text[:150]}...")
    
    # Extract AGENT_ID atau N
    n_match = re.search(r'(?:N|AGENT_ID)\s*=\s*(\d+)', problem_text)
    agent_id = int(n_match.group(1)) if n_match else 42909
    
    # ===== POLA 1: Sum of numbers divisible by 3 or 5 but not 15 =====
    if "divisible by 3 or 5, but not by 15" in problem_text:
        return solve_divisible_sum(agent_id)
    
    # ===== POLA 2: Divisible by (AGENT_ID mod 17) or (AGENT_ID mod 23) =====
    elif "divisible by either (AGENT_ID mod 17) or (AGENT_ID mod 23)" in problem_text:
        return solve_mod_divisible(agent_id)
    
    # ===== POLA 3: Smallest N where sum divisible by AGENT_ID =====
    elif "smallest positive integer N" in problem_text:
        return solve_smallest_n(agent_id, problem_text)
    
    # ===== POLA 4: Simple arithmetic =====
    else:
        return solve_arithmetic(problem_text, agent_id)

def solve_divisible_sum(N):
    """Sum of numbers ≤ N divisible by 3 or 5 but not 15"""
    total = 0
    for k in range(1, N+1):
        if (k % 3 == 0 or k % 5 == 0) and (k % 15 != 0):
            total += k
    return total % (N % 100 + 1) if N > 0 else total

def solve_mod_divisible(agent_id):
    """Sum of numbers ≤ 1000 divisible by (agent_id mod 17) or (agent_id mod 23) but not both"""
    mod1 = agent_id % 17
    mod2 = agent_id % 23
    
    # Handle modulus 0 (treat as 17 or 23)
    if mod1 == 0:
        mod1 = 17
    if mod2 == 0:
        mod2 = 23
    
    total = 0
    for k in range(1, 1001):
        by_mod1 = (k % mod1 == 0)
        by_mod2 = (k % mod2 == 0)
        if (by_mod1 or by_mod2) and not (by_mod1 and by_mod2):
            total += k
    return total

def solve_smallest_n(agent_id, problem_text):
    """Smallest N where sum condition holds"""
    if "sum of the first N positive integers is divisible by" in problem_text:
        # Sum 1..N = N(N+1)/2 divisible by agent_id
        for n in range(1, 10000):
            total = n * (n + 1) // 2
            if total % agent_id == 0:
                return n % 1000
    
    elif "sum of the squares of the first N positive integers" in problem_text:
        # Sum of squares = N(N+1)(2N+1)/6 divisible by agent_id+1
        target = agent_id + 1
        for n in range(1, 10000):
            total = n * (n + 1) * (2*n + 1) // 6
            if total % target == 0:
                return n % 1000
    
    return agent_id % 1000

def solve_arithmetic(problem_text, agent_id):
    """Simple arithmetic with AGENT_ID replacement"""
    # Replace {AGENT_ID} with actual number
    clean = problem_text.replace('{AGENT_ID}', str(agent_id))
    
    # Remove '= ?' and clean up
    clean = clean.replace('= ?', '').strip()
    clean = clean.replace('×', '*').replace('÷', '/')
    clean = clean.replace('mod', '%')
    
    # Handle Unicode
    clean = clean.replace('≤', '<=').replace('≥', '>=')
    
    try:
        result = eval(clean)
        return int(result) if isinstance(result, (int, float)) else 0
    except:
        # Fallback: return last number
        numbers = re.findall(r'\d+', problem_text)
        return int(numbers[-1]) if numbers else 0
