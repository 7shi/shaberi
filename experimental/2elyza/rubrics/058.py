def judge_058(score: int, judge: callable) -> int:
    # - 義父, 義理の親と答えられた場合: 5点
    # - 結婚相手である葵の親、のように明確に「義父」のようなキーワードが出ていない場合: 4点
    # - 「善吉は悠にとっての敵」のような血縁ではない関係性の場合: 3点
    # - 家族, 親族と答えた場合: 3点
    # - （義理ではない）父親, 親と答えた場合: 2点

    determined_score = 1

    if judge("義父、または義理の親と答えている"):
        determined_score = 5
    elif judge("結婚相手である葵の親、のように明確に「義父」のようなキーワードが出ていないが関係性が示されている"):
        determined_score = 4
    elif judge("「善吉は悠にとっての敵」のような血縁ではない関係性であると答えている") or \
         judge("家族、または親族と答えている"):
        determined_score = 3
    elif judge("（義理ではない）父親、または親と答えている"):
        determined_score = 2

    return determined_score