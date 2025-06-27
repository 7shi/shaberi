def judge_039(score: int, judge: callable) -> int:
    # - 含まれていません、と不正解な場合: 1点になる
    # - 含まれている、と正解しているが理由が書いていない: 4点になる
    # - 含まれている、と正解していて理由も書いてある: 5点になる

    if judge("回答が不正解である"):
        score = 1
    elif judge("回答が正解だが、理由が書かれていない"):
        score = 4
    
    return score