def judge_081(score: int, judge: callable) -> int:
    # - 全問正解: 5点
    # - 1問のみ不正解: 4点
    # - 2問のみ不正解: 3点
    # - 3~4問不正解: 2点
    # - 5~6問不正解: 1点

    if judge("全問正解である"):
        return 5
    elif judge("1問のみ不正解である"):
        return 4
    elif judge("2問のみ不正解である"):
        return 3
    elif judge("3問または4問不正解である"):
        return 2
    elif judge("5問または6問不正解である"):
        return 1
    return 0