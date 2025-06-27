def judge_006(score: int, judge: callable) -> int:
    # - 1問目は5~9の間であれば正解
    # - 2問目は1~4の間であれば正解
    # - どちらかの問いが不正解なら-2点
    # - 2つ正解しているが、理由の説明がない場合は4点

    is_q1_correct = judge("1問目の答えが5以上9以下である")
    is_q2_correct = judge("2問目の答えが1以上4以下である")
    has_no_explanation = judge("理由の説明がない")

    if not (is_q1_correct and is_q2_correct):
        score -= 2
    elif is_q1_correct and is_q2_correct and has_no_explanation:
        score = 4
        
    return score