def judge_100(score: int, judge: callable) -> int:
    # - 順番を全て適切に並べ替えている: 5点
    # - 順番を全て適切に並べ替えているが、文を引用する際に元の文から変化してしまっている: 3点
    # - 1つでも順番を間違えている: 1点

    is_all_correct_order = judge("順番を全て適切に並べ替えている")
    is_text_changed = judge("文を引用する際に元の文から変化してしまっている")

    if is_all_correct_order:
        if is_text_changed:
            score = 3
    else:
        score = 1
        
    return score