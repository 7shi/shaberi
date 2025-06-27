def judge_018(score: int, judge: callable) -> int:
    # - 問題1は左が正解で、南に曲がったは不正解
    # - 問題2は北東が正解で、東や北、東北は不正解
    # 
    # - 1問不正解: -2点
    # - 2問不正解: -4点

    incorrect_count = 0

    if judge("問題1の回答が左ではない"):
        incorrect_count += 1

    if judge("問題2の回答が北東ではない"):
        incorrect_count += 1

    if incorrect_count == 1:
        score -= 2
    elif incorrect_count == 2:
        score -= 4
        
    return score