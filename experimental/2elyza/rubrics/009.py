def judge_009(score: int, judge: callable) -> int:
    # - 答えのいずれかが抜けている場合: -2点
    # - 答えは出力しているが、今冬など、余計な要素が入っている場合: -2点
    #   - あす、25日（24日から26日であるため) の場合は減点なし

    if judge("答えのいずれかが抜けている"):
        score -= 2
    
    if judge("答えは出力しているが、今冬など、余計な要素が入っている"):
        score -= 2
        
    return score
