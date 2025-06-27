def judge_007(score: int, judge: callable) -> int:
    # - 選択肢を外している場合: -4点
    # - 理由が的外れな場合: -2点
    # - 理由の説明として（反論を）予想する旨が記述されていない場合: -1点

    if judge("選択肢を外している"):
        score -= 4
    if judge("理由が的外れである"):
        score -= 2
    if judge("理由の説明として反論を予想する旨が記述されていない"):
        score -= 1
    return score
