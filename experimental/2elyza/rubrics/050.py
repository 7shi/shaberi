def judge_050(score: int, judge: callable) -> int:
    # - (1/3+33)*210/100  と正しく回答できた場合: 5点
    # - 1/3+33*210/100 と括弧をつけ忘れたのみの場合: 3点
    # - それ以外の場合: 1点

    if judge("(1/3+33)*210/100 と正しく回答できた"):
        score = 5
    elif judge("1/3+33*210/100 と括弧をつけ忘れたのみの場合"):
        score = 3
    else:
        score = 1
    return score