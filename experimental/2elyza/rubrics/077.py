def judge_077(score: int, judge: callable) -> int:
    # - 正解している場合: 5点
    # - 不正解の場合: 1点

    if judge("正解している"):
        score = 5
    else:
        score = 1
    return score