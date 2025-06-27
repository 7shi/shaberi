def judge_020(score: int, judge: callable) -> int:
    # - 不正解の場合、-4点
    
    if judge("不正解である"):
        score -= 4
    return score