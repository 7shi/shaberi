def judge_003(score: int, judge: callable) -> int:
    # - 「独自の文化や哲学、神話が有名です」などのように具体例がない場合は-1点
    # - 事実と異なる内容の場合: -2点

    if judge("「独自の文化や哲学、神話が有名です」などのように具体例がない"):
        score -= 1
    if judge("事実と異なる内容である"):
        score -= 2
    return score