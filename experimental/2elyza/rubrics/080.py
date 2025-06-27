def judge_080(score: int, judge: callable) -> int:
    # ベースとなる得点:
    # - だれ, なに の2つを両方正解している場合: 5点
    # - だれ, なに の片方のみを答えている場合: 3点
    # 
    # 減点項目
    # - だれ, なに 以外の答えを出力している場合: -1点
    # - 正しくない理由や説明を書いている場合: -1点
    #     - e.g. ドライバーという単語はだれという疑問詞タグを持ち、「ドライバーは誰ですか」などの疑問文に直すことができます。

    is_dare_correct = judge("「だれ」に対する回答が正しい")
    is_nani_correct = judge("「なに」に対する回答が正しい")

    intended_base_score = 0
    if is_dare_correct and is_nani_correct:
        intended_base_score = 5
    elif is_dare_correct or is_nani_correct:
        intended_base_score = 3

    if score > intended_base_score:
        score = intended_base_score

    if judge("「だれ」「なに」以外の答えを出力している"):
        score -= 1

    if judge("正しくない理由や説明を書いている"):
        score -= 1

    return max(0, score)