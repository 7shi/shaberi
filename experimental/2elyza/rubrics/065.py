def judge_065(score: int, judge: callable) -> int:
    # - 不正解の場合: 1点
    # - ヴィンセントであることを正解している: 4点
    # - ヴィンセントであることを正解した上で、9歳であることにも触れている: 5点

    if judge("ヴィンセントであることを正解しており、かつ9歳であることにも触れている"):
        return 5
    elif judge("ヴィンセントであることを正解している"):
        return 4
    else:
        return 1