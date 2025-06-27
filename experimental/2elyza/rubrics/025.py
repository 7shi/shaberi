def judge_025(score: int, judge: callable) -> int:
    # A. 要約をしている
    # B. 不満について言及している
    # 
    # - A, B両方できていない: -4点
    # - A, Bのいずれかが抜けている・誤っている場合: -2点
    #     - 不満については、「もしかしたら契約内容の確認が面倒で不満に思っているかもしれない」程度の推測なら減点としない

    has_summary = judge("要約をしている")
    has_complaint = judge("不満について言及している")

    if not has_summary and not has_complaint:
        score -= 4
    elif not has_summary or not has_complaint:
        score -= 2
        
    return score