def judge_045(score: int, judge: callable) -> int:
    # - 長さを正解していない: 1点になる
    # - 長さを正解しているが、最長共通部分列を答えていない: 4点
    # - 長さを正解しているうえで、最長共通部分文字列を答えている: 5点

    if judge("長さを正解していない"):
        score = 1
    elif judge("長さを正解しているが、最長共通部分列を答えていない"):
        score = 4
    elif judge("長さを正解しているうえで、最長共通部分文字列を答えている"):
        score = 5
    return score