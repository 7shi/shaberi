def judge_078(score: int, judge: callable) -> int:
    # - Aに対応するQが書けている: 5点
    # - Qは書けているが、Aと対応していない: 3点
    #     - e.g. ズボンの履き方は？
    # - Qが書けていない: 1点

    if judge("Qが書けていない"):
        score = 1
    elif judge("Qは書けているが、Aと対応していない"):
        score = 3
    return score