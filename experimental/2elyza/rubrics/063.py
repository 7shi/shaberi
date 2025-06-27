def judge_063(score: int, judge: callable) -> int:
    # - 不正解の場合: 1点
    # - 正解しているが理由や説明がない場合: 4点
    # - 正解していて理由や説明がある場合: 5点

    is_correct = judge("正解している")
    has_explanation = judge("理由や説明がある")

    if not is_correct:
        score = 1
    elif not has_explanation:
        score = 4
    
    return score