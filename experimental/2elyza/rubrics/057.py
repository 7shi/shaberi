def judge_057(score: int, judge: callable) -> int:
    # - はい、と答えた場合: 1点
    # - いいえ、と答えたがその後の発話が会話として不自然である場合: 3点
    # - いいえ、と答え自然な発話をしている場合: 5点
    #    - 「いいえ、シワは増えていません」くらい簡素でも5点でいい

    if judge("はい、と答えている"):
        score = 1
    elif judge("いいえ、と答えている"):
        if judge("その後の発話が会話として不自然である"):
            score = 3

    return score