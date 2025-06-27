def judge_061(score: int, judge: callable) -> int:
    # - 不正解の場合: 1点
    # - 正解しているが理由や説明がない場合: 4点
    # - 正解していて理由や説明がある場合: 5点

    if judge("不正解である"):
        score = 1
    elif judge("正解しているが理由や説明がない"):
        score = 4
    
    return score