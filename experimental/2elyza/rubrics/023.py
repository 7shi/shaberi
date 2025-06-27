def judge_023(score: int, judge: callable) -> int:
    # - 三重県と答えられているが、他に嘘の情報が入っている: -2点
    # - 伊勢市のように県を答えていない: -2点

    if judge("三重県と答えられている") and judge("他に嘘の情報が入っている"):
        score -= 2
    if judge("伊勢市のように県を答えていない"):
        score -= 2
    return score