def judge_008(score: int, judge: callable) -> int:
    # - 微積分学101, 美術史のいずれかが抜けている場合: -2点
    # - 微積分学101, 美術史は出力しているが、科目名という概念などを理解できずに田中教授など余計な要素が入っている場合: -2点
    # - 表をそのまま出力してしまった場合: -4点

    missing_calculus = judge("微積分学101が抜けている")
    missing_art_history = judge("美術史が抜けている")
    if missing_calculus or missing_art_history:
        score -= 2

    has_extraneous_elements = judge("田中教授など科目名以外の余計な要素が含まれている")
    if not missing_calculus and not missing_art_history and has_extraneous_elements:
        score -= 2
        
    if judge("表をそのまま出力してしまった"):
        score -= 4
        
    return score
