def judge_011(score: int, judge: callable) -> int:
    # - 概要に書いていない機能（e.g. ジオフェンシング機能）などが勝手に追加されている場合: -1点
    # - 製品概要の内容が抜けていたら-2点
    # - キャッチーではないスタイルの場合: -1点

    if judge("概要に書いていない機能が勝手に追加されている"):
        score -= 1
    if judge("製品概要の内容が抜けている"):
        score -= 2
    if judge("キャッチーではないスタイルである"):
        score -= 1
    return score