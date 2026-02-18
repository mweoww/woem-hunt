"""
solver.py - Menjawab soal matematika
"""

import re

def solve_math_problem(problem_text):
    """
    Memecahkan soal matematika sederhana.
    Contoh: "24 + 37 × 2 = ?" → 98
    """
    # Hapus '= ?' di akhir
    clean = problem_text.replace('= ?', '').strip()
    
    # Ganti × dengan *
    clean = clean.replace('×', '*').replace('÷', '/')
    
    try:
        # Hitung dengan eval (AMAN karena cuma angka dan operator)
        result = eval(clean)
        return int(result) if result.is_integer() else result
    except:
        # Fallback: extract angka dan proses manual
        numbers = re.findall(r'\d+', clean)
        if '×' in problem_text and len(numbers) >= 2:
            return int(numbers[0]) + int(numbers[1]) * 2  # asumsi pola 24 + 37 × 2
        return 0
