def judge_002(score: int, judge: callable) -> int:
    # - クマが海辺に行く
    # - クマとアザラシが友達になる
    # - 最後に家に帰る
    # の3つ要素が必要で、欠けている場合: 5点ではなく3点になる
    # 
    # 短編小説として淡白な場合: -1点
    
    a = judge("クマが海辺に行く")
    b = judge("クマとアザラシが友達になる")
    c = judge("最後に家に帰る")
    if not (a and b and c) and score > 3:
        score = 3
    if judge("短編小説として淡白な内容である"):
        score -= 1
    return score
