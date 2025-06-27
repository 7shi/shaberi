def judge_048(score: int, judge: callable) -> int:
    # - 男, あるいは医者であると回答した場合: 3点
    # - 曖昧であると回答した場合: 4点
    # - 曖昧であると回答し、その理由も説明している場合: 5点

    if judge("曖昧であると回答しており、その理由も説明している"):
        score = 5
    elif judge("曖昧であると回答している"):
        score = 4
    elif judge("男、あるいは医者であると回答している"):
        score = 3
    
    return score