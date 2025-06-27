def judge_042(score: int, judge: callable) -> int:
    # - 不正解: 1点
    # - 正解だが理由がない: 4点
    # - 正解で理由がある: 5点
    
    is_correct = judge("正解である")
    has_reason = judge("理由がある")

    if not is_correct:
        score = 1
    elif is_correct and not has_reason:
        score = 4
    
    return score