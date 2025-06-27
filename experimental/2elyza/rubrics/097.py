def judge_097(score: int, judge: callable) -> int:
    # A. 花粉症の対策をする
    # B. 春の自然を楽しむコツをあげる
    # C. 3つ回答する
    # 
    # A, B, Cそれぞれ間違うごとに-2点

    if not judge("花粉症の対策をしている"):
        score -= 2

    if not judge("春の自然を楽しむコツをあげている"):
        score -= 2
        
    if not judge("3つ回答している"):
        score -= 2
        
    return score