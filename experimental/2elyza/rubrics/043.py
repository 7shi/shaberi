def judge_043(score: int, judge: callable) -> int:
    # - 不正解: 1点
    # - 正解だが理由がない: 4点
    # - 正解で理由がある: 5点

    if judge("不正解である"):
        score = 1
    elif judge("正解だが理由がない"):
        score = 4
    return score