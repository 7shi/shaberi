def judge_083(score: int, judge: callable) -> int:
    # A. 何をやろうとしているか
    # B. なぜやろうとしているか
    # 
    # - A, Bを1つ間違えるごとに-2点
    
    if judge("「何をやろうとしているか」が間違っている、または記述がない"):
        score -= 2
    
    if judge("「なぜやろうとしているか」が間違っている、または記述がない"):
        score -= 2
        
    return score