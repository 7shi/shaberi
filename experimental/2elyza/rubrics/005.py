def judge_005(score: int, judge: callable) -> int:
    # - 「読むべき」とあるように小説であるべきで、アバターなどのSF映画だと -2点
    # - 実在しない架空の小説の場合 -2点
    # - ドラゴンボールなどの漫画の場合も -2点
    # - 10冊ではない場合、-2点
    # - 作品名のみの記載で、作品を薦める記述がない場合は-1点

    if judge("SF映画である"):
        score -= 2
    if judge("実在しない架空の小説である"):
        score -= 2
    if judge("漫画である"):
        score -= 2
    if judge("10冊ではない"):
        score -= 2
    if judge("作品名のみの記載で、作品を薦める記述がない"):
        score -= 1
    return score
