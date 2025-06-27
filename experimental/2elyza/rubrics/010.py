def judge_010(score: int, judge: callable) -> int:
    # - 答えのいずれかが抜けている場合: -2点
    # - 答えは出力しているが、織田信長など、余計な要素が入っている場合: -2点

    if judge("答えのいずれかが抜けている"):
        score -= 2
    if judge("答えは出力しているが、余計な要素が入っている"):
        score -= 2
    return score