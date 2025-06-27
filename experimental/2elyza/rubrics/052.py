def judge_052(score: int, judge: callable) -> int:
    # A. 子供が
    # B. 走った
    # C. 運んだ
    # 
    # - A,B,Cの3つの要素を1つ外すごとに-2点
    # - 余計な要素（e.g. 彼, 水）を1つ入れてしまうごとに-2点

    if not judge("「子供が」という必須要素が存在する"):
        score -= 2
    if not judge("「走った」という必須要素が存在する"):
        score -= 2
    if not judge("「運んだ」という必須要素が存在する"):
        score -= 2

    if judge("余計な要素が1つ以上存在する"):
        score -= 2
    if judge("余計な要素が2つ以上存在する"):
        score -= 2
    if judge("余計な要素が3つ以上存在する"):
        score -= 2
    if judge("余計な要素が4つ以上存在する"):
        score -= 2
    
    return score