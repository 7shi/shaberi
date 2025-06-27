def judge_079(score: int, judge: callable) -> int:
    # - 正解の場合: 5点
    # - 不正解の場合: 1点
    #     - 「飲むことが好きなこと」なども不正解
    
    if judge("不正解である"):
        score = 1
        
    return score