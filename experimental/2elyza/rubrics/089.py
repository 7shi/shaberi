def judge_089(score: int, judge: callable) -> int:
    # - 完全正解: 5点
    # - 1,2このみ間違えている: 3点
    # - それ以上間違えている: 1点
    
    if judge("1つか2つ間違えている"):
        return 3
    elif judge("それ以上間違えている"):
        return 1
    return score