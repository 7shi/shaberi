def judge_086(score: int, judge: callable) -> int:
    # 出題意図:
    # - ツールとその説明を与えたときにLLMがそれらをAgentのように使いこなせるかを見る
    # 
    # ベースとなる得点:
    # - ピザジャンボのSを注文した: 5点
    # - ラーメン屋に行った、ラーメンを出前として注文した: 3点
    # 
    # 減点項目:
    # - 捏造や誤りを含む: -1点

    if not judge("ピザジャンボのSを注文した"):
        if judge("ラーメン屋に行った、ラーメンを出前として注文した"):
            score = 3
        else:
            score = 0

    if judge("捏造や誤りを含む"):
        score -= 1

    if score < 0:
        score = 0

    return score