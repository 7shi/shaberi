def judge_098(score: int, judge: callable) -> int:
    # - 完全正解: 5点
    # - 正解しているが数字とアルファベットのペアを明確に回答していない: 4点
    # - 1,2このみ間違えている: 3点
    # - それ以上間違えている: 1点

    if judge("3つ以上の間違いがある"):
        score = 1
    elif judge("1つまたは2つの間違いがある"):
        score = 3
    elif judge("正解しているが、数字とアルファベットのペアを明確に回答していない"):
        score = 4

    return score