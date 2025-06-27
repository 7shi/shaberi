def judge_013(score: int, judge: callable) -> int:
    # このタスクは以下の3つのタスクのからなります。
    # 
    # - ひらがなへの変換
    # - 単語への分割
    # - 漢字変換候補の提示
    # 
    # 3タスク全てできているが、一位の変換候補をつなげた結果が「10部の書籍」「十部の書籍」のいずれでもない: 4点
    # 3タスクのうち1つ間違い: 3点
    # 3タスクのうち2つ間違い: 2点
    # 3タスクのうち3つ間違い: 1点

    is_hiragana_incorrect = judge("ひらがなへの変換が正しくない")
    is_segmentation_incorrect = judge("単語への分割が正しくない")
    is_kanji_candidates_incorrect = judge("漢字変換候補の提示が正しくない")

    num_incorrect_tasks = 0
    if is_hiragana_incorrect:
        num_incorrect_tasks += 1
    if is_segmentation_incorrect:
        num_incorrect_tasks += 1
    if is_kanji_candidates_incorrect:
        num_incorrect_tasks += 1

    is_final_output_incorrect = judge("一位の変換候補をつなげた結果が「10部の書籍」または「十部の書籍」のいずれでもない")

    if num_incorrect_tasks == 0 and is_final_output_incorrect:
        score = 4
    elif num_incorrect_tasks == 1:
        score = 3
    elif num_incorrect_tasks == 2:
        score = 2
    elif num_incorrect_tasks == 3:
        score = 1

    return score
