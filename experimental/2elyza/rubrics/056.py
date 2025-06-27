def judge_056(score: int, judge: callable) -> int:
    # ベースの得点:
    # - 今日は雨, お菓子を買っていた のいずれかを出力した場合: 4点
    # - 今日は雨, お菓子を買っていた の両方を出力した場合: 5点
    # 
    # 減点項目:
    # - 遠足は中止になる、と断言してしまった場合: -3点
    # - 遠足は中止になる可能性が高い、と出力した場合: -1点

    has_rain_output = judge("今日は雨と出力した")
    has_snack_output = judge("お菓子を買っていたと出力した")

    if has_rain_output and has_snack_output:
        score = 5
    elif has_rain_output or has_snack_output:
        score = 4
    else:
        score = 0

    if judge("遠足は中止になると断言した"):
        score -= 3
    elif judge("遠足は中止になる可能性が高いと出力した"):
        score -= 1
    
    if score < 0:
        score = 0

    return score