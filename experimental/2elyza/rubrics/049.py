def judge_049(score: int, judge: callable) -> int:
    # - 不正解の場合: 1点
    # - 正解では文字列 } ] > ] を追加しなければいけないが、惜しいもの（編集距離が1以下）: 3点
    # - 正解の場合: 5点

    
    if judge("正解である"):
        score = 5
    elif judge("正解では文字列 } ] > ] を追加しなければいけないが、惜しいもの（編集距離が1以下）である"):
        score = 3
    else:
        score = 1
    return score