def judge_066(score: int, judge: callable) -> int:
    # - 不正解の場合: 1点
    # - 正解の文を記述できている: 4点
    # - 正解の文を記述できている上で、その理由も説明している: 5点

    is_correct_sentence = judge("正解の文を記述できている")
    is_reason_explained = judge("その理由も説明している")

    if is_correct_sentence and is_reason_explained:
        score = 5
    elif is_correct_sentence:
        score = 4
    else:
        score = 1
    
    return score