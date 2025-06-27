def judge_062(score: int, judge: callable) -> int:
    # - 2つの問題に対して、1つ間違えるごとに-2点
    
    if judge("問題1が不正解である"):
        score -= 2
    if judge("問題2が不正解である"):
        score -= 2
    return score