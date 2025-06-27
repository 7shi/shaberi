def judge_093(score: int, judge: callable) -> int:
    # - シチュエーションを踏まえていない: -2点
    # - 小説中の母親のセリフの文体として不適切: -2点
    
    if judge("シチュエーションを踏まえていない"):
        score -= 2
    if judge("小説中の母親のセリフの文体として不適切"):
        score -= 2
    return score