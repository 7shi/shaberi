"""
ELYZA-tasks-100 評価関数集

このファイルはconv_rubrics.pyによって自動生成されました。
各関数の評価基準はdata/XXX.mdから抽出されています。
"""

def judge_001(score: int, judge: callable) -> int:
    # - 熱意を取り戻すのではなく、仕事の効率化・スキルアップのような文脈になっていたら1点減点
    # - 出したアイデアが5つより多い、少ない場合は1点減点
    # - 5つのアイデアのうち、内容が重複しているものがあれば1点減点
    
    if judge("熱意を取り戻すのではなく、仕事の効率化・スキルアップのような文脈になっている"):
        score -= 1
    if judge("出したアイデアが5つより多い、または少ない"):
        score -= 1
    if judge("5つのアイデアのうち、内容が重複しているものがある"):
        score -= 1
    return score


def judge_002(score: int, judge: callable) -> int:
    # - クマが海辺に行く
    # - クマとアザラシが友達になる
    # - 最後に家に帰る
    # の3つ要素が必要で、欠けている場合: 5点ではなく3点になる
    # 
    # 短編小説として淡白な場合: -1点
    
    a = judge("クマが海辺に行く")
    b = judge("クマとアザラシが友達になる")
    c = judge("最後に家に帰る")
    if not (a and b and c) and score > 3:
        score = 3
    if judge("短編小説として淡白な内容である"):
        score -= 1
    return score


def judge_003(score: int, judge: callable) -> int:
    # - 「独自の文化や哲学、神話が有名です」などのように具体例がない場合は-1点
    # - 事実と異なる内容の場合: -2点

    if judge("「独自の文化や哲学、神話が有名です」などのように具体例がない"):
        score -= 1
    if judge("事実と異なる内容である"):
        score -= 2
    return score


def judge_004(score: int, judge: callable) -> int:
    # - 疑問になっておらず、説明や回答などになっている場合: -4点 (1点になる)
    # - 「ゴミ圧縮機の主な用途は？」「環境負荷を軽減できる？」などの与えられた説明中に明らかに答えが書いてあり、ユーザーが疑問に感じない（読んでいて分からない）であろう質問のみの場合: -1点

    if judge("疑問になっておらず、説明や回答などになっている"):
        score = 1

    if judge("与えられた説明中に明らかに答えが書いてあり、ユーザーが疑問に感じないであろう質問のみの場合"):
        score -= 1
        
    return score


def judge_005(score: int, judge: callable) -> int:
    # - 「読むべき」とあるように小説であるべきで、アバターなどのSF映画だと -2点
    # - 実在しない架空の小説の場合 -2点
    # - ドラゴンボールなどの漫画の場合も -2点
    # - 10冊ではない場合、-2点
    # - 作品名のみの記載で、作品を薦める記述がない場合は-1点

    if judge("SF映画である"):
        score -= 2
    if judge("実在しない架空の小説である"):
        score -= 2
    if judge("漫画である"):
        score -= 2
    if judge("10冊ではない"):
        score -= 2
    if judge("作品名のみの記載で、作品を薦める記述がない"):
        score -= 1
    return score


def judge_006(score: int, judge: callable) -> int:
    # - 1問目は5~9の間であれば正解
    # - 2問目は1~4の間であれば正解
    # - どちらかの問いが不正解なら-2点
    # - 2つ正解しているが、理由の説明がない場合は4点

    is_q1_correct = judge("1問目の答えが5以上9以下である")
    is_q2_correct = judge("2問目の答えが1以上4以下である")
    has_no_explanation = judge("理由の説明がない")

    if not (is_q1_correct and is_q2_correct):
        score -= 2
    elif is_q1_correct and is_q2_correct and has_no_explanation:
        score = 4
        
    return score


def judge_007(score: int, judge: callable) -> int:
    # - 選択肢を外している場合: -4点
    # - 理由が的外れな場合: -2点
    # - 理由の説明として（反論を）予想する旨が記述されていない場合: -1点

    if judge("選択肢を外している"):
        score -= 4
    if judge("理由が的外れである"):
        score -= 2
    if judge("理由の説明として反論を予想する旨が記述されていない"):
        score -= 1
    return score


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


def judge_009(score: int, judge: callable) -> int:
    # - 答えのいずれかが抜けている場合: -2点
    # - 答えは出力しているが、今冬など、余計な要素が入っている場合: -2点
    #   - あす、25日（24日から26日であるため) の場合は減点なし

    if judge("答えのいずれかが抜けている"):
        score -= 2
    
    if judge("答えは出力しているが、今冬など、余計な要素が入っている"):
        score -= 2
        
    return score


def judge_010(score: int, judge: callable) -> int:
    # - 答えのいずれかが抜けている場合: -2点
    # - 答えは出力しているが、織田信長など、余計な要素が入っている場合: -2点

    if judge("答えのいずれかが抜けている"):
        score -= 2
    if judge("答えは出力しているが、余計な要素が入っている"):
        score -= 2
    return score


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


def judge_012(score: int, judge: callable) -> int:
    # - 皮肉が言えていない場合: -2点
    if judge("皮肉が言えていない"):
        score -= 2
    return score


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


def judge_014(score: int, judge: callable) -> int:
    # - そもそもアドバイスになっていない場合: -4点
    # - 平穏を得るためには平穏を見つけることが重要です、などの一見アドバイスに見えてアドバイスになっていない場合: -2点
    # - よく睡眠をとりましょう、などの現代的で具体的なアドバイスの場合: -1点
    # - 自己を超越する、解脱するなどの無理が含まれるアドバイスの場合: -1点

    if judge("そもそもアドバイスになっていない"):
        score -= 4
    if judge("一見アドバイスに見えてアドバイスになっていない"):
        score -= 2
    if judge("現代的で具体的なアドバイスが含まれる"):
        score -= 1
    if judge("自己を超越する、解脱するなど、無理が含まれるアドバイスがある"):
        score -= 1
    return score


def judge_015(score: int, judge: callable) -> int:
    # - 的外れだが、何かしらの教訓（e.g. 互いの違いを受け入れることが大事）を述べている: 2点になる
    # - コミュニケーションが大事という内容のみ: 3点になる
    # - 相手の意見を尊重するコミュニケーションが大事という内容のみ: 4点になる
    # - 「物事の一部の側面しか見えていない場合がある」「1つの物事は視点によって異なる見え方がする」という要素に言及したうえで、相手の意見を尊重することが大事という内容: 5点になる

    has_perspective_insight = judge("物事の一部の側面しか見えていない場合がある、または1つの物事は視点によって異なる見え方がするという要素に言及している")
    has_respect_for_others = judge("相手の意見を尊重することが大事という内容である")

    if has_perspective_insight and has_respect_for_others:
        score = 5
    elif has_respect_for_others:
        score = 4
    elif judge("コミュニケーションが大事という内容である"):
        score = 3
    elif judge("的外れだが、何かしらの教訓（例: 互いの違いを受け入れることが大事）を述べている"):
        score = 2
    else:
        pass
        
    return score


def judge_016(score: int, judge: callable) -> int:
    # - メールになっていない: -4点
    # - メールにはなっているが、返信になっていない: -3点
    # - 返信メールになっているが、丁寧な文体ではない: -2点
    # - 返信メールになっているが、時刻などの内容に誤りがある: -2点

    if judge("メールになっていない"):
        score -= 4
    elif judge("メールにはなっているが、返信になっていない"):
        score -= 3
    
    if judge("返信メールになっているが、丁寧な文体ではない"):
        score -= 2
    if judge("返信メールになっているが、時刻などの内容に誤りがある"):
        score -= 2
        
    return score


def judge_017(score: int, judge: callable) -> int:
    # - CM風の文体でない場合: -2点
    # - 要約に含まれていない内容を書いてしまっている: -2点

    if judge("CM風の文体ではない"):
        score -= 2
    if judge("要約に含まれていない内容を書いてしまっている"):
        score -= 2
    return score


def judge_018(score: int, judge: callable) -> int:
    # - 問題1は左が正解で、南に曲がったは不正解
    # - 問題2は北東が正解で、東や北、東北は不正解
    # 
    # - 1問不正解: -2点
    # - 2問不正解: -4点

    incorrect_count = 0

    if judge("問題1の回答が左ではない"):
        incorrect_count += 1

    if judge("問題2の回答が北東ではない"):
        incorrect_count += 1

    if incorrect_count == 1:
        score -= 2
    elif incorrect_count == 2:
        score -= 4
        
    return score


def judge_019(score: int, judge: callable) -> int:
    # - 出題意図: 下手なプロンプティング、曖昧な指示に対応すること
    # - プロンプティングの構造を理解できてなく、源頼朝の文などの余計な箇所も言い換えてしまっている: -2点
    # - 「こんな感じ」が理解できず、カジュアルな文体に直せていない: -2点
    if judge("プロンプティングの構造を理解できておらず、源頼朝の文などの余計な箇所も言い換えてしまっている"):
        score -= 2
    if judge("「こんな感じ」が理解できず、カジュアルな文体に直せていない"):
        score -= 2
    return score


def judge_020(score: int, judge: callable) -> int:
    # - 不正解の場合、-4点
    
    if judge("不正解である"):
        score -= 4
    return score


def judge_021(score: int, judge: callable) -> int:
    # A. 違いをのべる（可燃性, 難燃性）
    # B. それらが原子番号によるものであると述べる
    # 
    # - A, Bの両方できていない場合: -4点
    # - A, Bの片方のみできていない場合: -2点
    # - 共通点について触れていない場合: -1点
    # - 与えられた文章以外の事実を利用している場合: -1点

    has_A = judge("可燃性と難燃性の違いについて述べている")
    has_B = judge("可燃性や難燃性が原子番号によるものであると述べている")

    if not has_A and not has_B:
        score -= 4
    elif not has_A or not has_B:
        score -= 2

    if judge("共通点について触れていない"):
        score -= 1
    
    if judge("与えられた文章以外の事実を利用している"):
        score -= 1

    return score


def judge_022(score: int, judge: callable) -> int:
    # - 40000kmなど、的外れな回答: 1点になる
    # - 分かりません、という回答: 3点になる
    # - 視点の高さなどの情報が足りないため分かりません、という回答: 4点になる
    # - およそ4-5km程度です、といった回答: 4点になる
    # - 視点の高さなどで変化しますが、仮にOOだった場合OOkmです、という回答: 5点
    #     - 高さが1.5mなら4.4km
    #     - 高さが1.7mなら4.7km
    #     - 高さが20mなら16.6km
    #     - 1kmは0.62マイル程度、マイルで答えてもOK
    if judge("的外れな回答である"):
        return 1

    if judge("分かりませんという回答である"):
        return 3

    if judge("視点の高さなどの情報が足りないため分かりませんという回答である"):
        return 4

    if judge("およそ4-5km程度ですという回答である"):
        return 4

    return score


def judge_023(score: int, judge: callable) -> int:
    # - 三重県と答えられているが、他に嘘の情報が入っている: -2点
    # - 伊勢市のように県を答えていない: -2点

    if judge("三重県と答えられている") and judge("他に嘘の情報が入っている"):
        score -= 2
    if judge("伊勢市のように県を答えていない"):
        score -= 2
    return score


def judge_024(score: int, judge: callable) -> int:
    # - 衆議院, 参議院, 上院, 下院という単語の1つでも抜けている: -4点
    # - 与えられた文章をコピーしているだけ: -3点
    # - 文体が小学生向けではない: -2点
    # - 上院の説明について、昔はOOだったけど今はOOであるというような記載がなく、昔の内容をあたかも今の内容かのように答えてしまっている: -1点

    if judge("衆議院, 参議院, 上院, 下院のいずれかの単語が抜けている"):
        score -= 4
    if judge("与えられた文章をコピーしているだけである"):
        score -= 3
    if judge("文体が小学生向けではない"):
        score -= 2
    if judge("上院の説明で、昔はOOだったが今はOOであるという記載がなく、昔の内容を現在の内容のように記述している"):
        score -= 1
    return score


def judge_025(score: int, judge: callable) -> int:
    # A. 要約をしている
    # B. 不満について言及している
    # 
    # - A, B両方できていない: -4点
    # - A, Bのいずれかが抜けている・誤っている場合: -2点
    #     - 不満については、「もしかしたら契約内容の確認が面倒で不満に思っているかもしれない」程度の推測なら減点としない

    has_summary = judge("要約をしている")
    has_complaint = judge("不満について言及している")

    if not has_summary and not has_complaint:
        score -= 4
    elif not has_summary or not has_complaint:
        score -= 2
        
    return score


def judge_026(score: int, judge: callable) -> int:
    # - 最終的な答えがあっていないが、途中で計算式などを踏まえて考えている様子がある: -3点
    # - 最終的な答えがあっていないし、数字のみを回答している: -4点

    if judge("最終的な答えがあっていないが、途中で計算式などを踏まえて考えている様子がある"):
        score -= 3
    elif judge("最終的な答えがあっていないし、数字のみを回答している"):
        score -= 4
    return score


def judge_027(score: int, judge: callable) -> int:
    # - 適当に選択肢を選び、外している: -4点
    # - 計算式を使って考えようとしているが、外している: -3点
    # - 1桁, 2桁, 3桁の3パターンに場合分けをして考えているが、外している: -2点
    # - 適当に選択肢を選び、正解している: -1点

    if judge("適当に選択肢を選び、外している"):
        score -= 4
    if judge("計算式を使って考えようとしているが、外している"):
        score -= 3
    if judge("1桁, 2桁, 3桁の3パターンに場合分けをして考えているが、外している"):
        score -= 2
    if judge("適当に選択肢を選び、正解している"):
        score -= 1
    return score


def judge_028(score: int, judge: callable) -> int:
    # - 間違えている: 1点になる
    # - 沈まないということを正解しているのみ: 4点になる
    # - 「一般的には沈まない」のように断り書きをしながら正解していたり、「鉛筆が木で出来ているなら沈まない」と前提を置いたうえで正解している: 5点になる

    if judge("断り書きをしながら正解している") or judge("前提を置いて正解している"):
        score = 5
    elif judge("沈まないということを正解しているのみ"):
        score = 4
    elif judge("間違えている"):
        score = 1
    
    return score


def judge_029(score: int, judge: callable) -> int:
    # - 答えが間違っている, 分かりませんという回答: 1点になる
    # - 答えが合っているが、本田圭佑についての誤った情報を含む: 3点になる
    # - 答えが合っているが、理由や説明がない: 4点になる
    # - 答えが合っていて、理由や説明がある: 5点になる

    if judge("答えが間違っている、または「分かりません」と回答している"):
        score = 1
    elif judge("答えは合っているが、本田圭佑についての誤った情報を含む"):
        score = 3
    elif judge("答えは合っているが、理由や説明がない"):
        score = 4
    else:
        score = 5
    
    return score


def judge_030(score: int, judge: callable) -> int:
    # A. 不自然な箇所（新宅空）を見つける
    # B. 不自然な箇所を読み方、あるいは文脈を考慮して修正する
    # 
    # - 対話の続きを生成してしまったり、指示に従えていない: 1点になる
    # - 不自然な箇所を見つけたが、誤った修正をしてしまった: 3点になる
    # - 不自然な箇所を見つけ、その箇所を削除してしまった: 4点になる

    if judge("対話の続きを生成してしまったり、指示に従えていない"):
        return 1

    if judge("不自然な箇所を見つけたが、誤った修正をしてしまった"):
        return 3

    if judge("不自然な箇所を見つけ、その箇所を削除してしまった"):
        return 4

    return score


def judge_031(score: int, judge: callable) -> int:
    # - 燃えると答えた: 1点になる
    # - 燃えないと答えたが、溶けるなどの誤った情報を含む回答: 3点になる
    # - 燃えない、という回答のみ: 4点になる
    # - 燃えないことを示したうえで、なぜ燃えないのかなど、この質問をしたユーザーの役に立つ回答も出来ている: 5点になる

    if judge("燃えると答えた"):
        return 1

    elif judge("燃えないことを示したうえで、なぜ燃えないのかなど、この質問をしたユーザーの役に立つ回答も出来ている"):
        return 5
    
    elif judge("燃えないと答えたが、溶けるなどの誤った情報を含む回答"):
        return 3
    
    elif judge("燃えない、という回答のみ"):
        return 4
    
    return score


def judge_032(score: int, judge: callable) -> int:
    # - 「私はAIなので契約することはできません」という旨の回答: 2点になる
    # - 契約書の内容を確認し、契約するかを判断するといった契約に関する重要なアクションが書かれていない: -2点
    # - 先輩、後輩を活用していない: -1点

    if judge("「私はAIなので契約することはできません」という旨の回答である"):
        return 2

    if judge("契約書の内容を確認し、契約するかを判断するといった契約に関する重要なアクションが書かれていない"):
        score -= 2
    
    if judge("先輩、後輩を活用していない"):
        score -= 1
        
    return score


def judge_033(score: int, judge: callable) -> int:
    # - 具体的なコンセプトを提示していない場合（e.g. 敵を倒すアクションゲーム）: -4点
    # - 新しさ、アクション要素のいずれかが抜けている: -2点
    # - 1-2文程度の簡素な答えで、アイデアを欲しているユーザーの役に立たない場合: -1点

    if judge("具体的なコンセプトを提示していない"):
        score -= 4
    
    if judge("新しさが抜けている") or judge("アクション要素が抜けている"):
        score -= 2
        
    if judge("1-2文程度の簡素な答えで、アイデアを欲しているユーザーの役に立たない"):
        score -= 1
        
    return score


def judge_034(score: int, judge: callable) -> int:
    # - 説明せよ、という指示なのに選択してしまっているなど、指示に従えていない場合: -4点
    # - A, Bそれぞれのメリット、デメリットという計4種類ではなく2種類の記述などになってしまっている場合: -3点
    # - Aのメリットはありません、のような場合: -1点
    # - AのメリットとBのデメリットが裏返しの関係になっていても、減点はしなくていい

    if judge("指示（説明せよ、など）に従わず、別の形式（選択、など）で回答している"):
        score -= 4

    if judge("A, Bそれぞれのメリット、デメリットという計4種類の記述が揃っておらず、2種類の記述などになっている"):
        score -= 3

    if judge("特定のメリットやデメリットが存在しないと明示的に記述している（例: 'Aのメリットはありません'）"):
        score -= 1
    

    return score


def judge_035(score: int, judge: callable) -> int:
    # - 「そのような行動」が「部屋を出ていった」ことを指すことを理解していない様子である場合: -2点
    # - 「急用ができたので部屋を出ていった」というように彼女の感情について言及せず、理由がもっともらしくない場合: -2点

    if judge("「そのような行動」が「部屋を出ていった」ことを指すことを理解していない"):
        score -= 2
    if judge("彼女の感情について言及せず、理由がもっともらしくない"):
        score -= 2
    return score


def judge_036(score: int, judge: callable) -> int:
    # - 返事として長すぎる（4文以上）の場合: -2点
    # - ユーザーに「あなた」と呼ばれているので、返事をすることを求められている主体はアシスタント側であり、主語が「私」である必要がある。このように適切な人称でない場合: -2点
    # - 友人からの暗めの相談として、フレンドリーかつ親切な文体ではない場合: -2点

    if judge("返事が4文以上である"):
        score -= 2
    if judge("主語が「私」ではない、または不適切な人称である"):
        score -= 2
    if judge("フレンドリーかつ親切な文体ではない"):
        score -= 2
    return score


def judge_037(score: int, judge: callable) -> int:
    # - どちらかを選んだだけで、理由や説明がない: -2点
    # - それぞれのパスタについて説明はあるが、選ぶための理由になっていない: -2点
    # - 調理がしやすいなど、レストランで注文というシチュエーションにふさわしくない: -2点

    if judge("どちらかを選んだだけで、理由や説明がない"):
        score -= 2
    if judge("それぞれのパスタについて説明はあるが、選ぶための理由になっていない"):
        score -= 2
    if judge("調理がしやすいなど、レストランで注文というシチュエーションにふさわしくない"):
        score -= 2
    return score


def judge_038(score: int, judge: callable) -> int:
    # - ことわざではない: -4点
    # - ことわざだが、このシチュエーションにふさわしくない: -2点
    #     - e.g. 失敗は成功のもと
    # - ことわざだが、このシチュエーションとしては少し惜しい: -1点
    #     - e.g. 時は金なり, 一期一会, 男心と秋の空
    # - 5点になる正解例
    #     - 後悔先に立たず, 光陰矢のごとし, 後の祭り
    # - 理由の説明などは採点の対象外とします
    if judge("ことわざではない"):
        score -= 4
    elif judge("ことわざだが、このシチュエーションにふさわしくない"):
        score -= 2
    elif judge("ことわざだが、このシチュエーションとしては少し惜しい"):
        score -= 1
    return score


def judge_039(score: int, judge: callable) -> int:
    # - 含まれていません、と不正解な場合: 1点になる
    # - 含まれている、と正解しているが理由が書いていない: 4点になる
    # - 含まれている、と正解していて理由も書いてある: 5点になる

    if judge("回答が不正解である"):
        score = 1
    elif judge("回答が正解だが、理由が書かれていない"):
        score = 4
    
    return score


def judge_040(score: int, judge: callable) -> int:
    # - 共通点を述べていない: 1点になる
    # - 共通点を述べているが、誤っている: 2点になる
    #     - e.g. 全てアフリカ大陸にあります
    # - 3つとも異なるの文化と歴史を持つ国というように、「国」という共通点以外出していない: 3点になる
    # - 人口が多い、豊かな文化などの緩めの共通点を挙げてられている: 5点になる

    if judge("共通点を述べていない"):
        score = 1
    elif judge("共通点を述べているが、誤っている"):
        score = 2
    elif judge("国という共通点以外出していない"):
        score = 3
    
    return score


def judge_041(score: int, judge: callable) -> int:
    # - 不正解の場合: 1点になる
    # - 情報不足、わからないといったように正解している: 4点になる
    # - 正解している上に理由を説明している: 5点になる

    if judge("正解している上に理由を説明している"):
        score = 5
    elif judge("情報不足、わからないといったように正解している"):
        score = 4
    elif judge("不正解である"):
        score = 1
    
    return score


def judge_042(score: int, judge: callable) -> int:
    # - 不正解: 1点
    # - 正解だが理由がない: 4点
    # - 正解で理由がある: 5点
    
    is_correct = judge("正解である")
    has_reason = judge("理由がある")

    if not is_correct:
        score = 1
    elif is_correct and not has_reason:
        score = 4
    
    return score


def judge_043(score: int, judge: callable) -> int:
    # - 不正解: 1点
    # - 正解だが理由がない: 4点
    # - 正解で理由がある: 5点

    if judge("不正解である"):
        score = 1
    elif judge("正解だが理由がない"):
        score = 4
    return score


def judge_044(score: int, judge: callable) -> int:
    # - 熟語の意味を答えていない: 1点
    # - 不自然な意味になっている（e.g. 杯を伝えること）: 3点
    # - 杯, 伝それぞれの単語の意味を組み合わせた意味を考えられている: 4点
    # - 杯, 伝それぞれの単語の意味を組み合わせた意味を考えられていることに加え、どのようにシチュエーションで使う熟語なのかや何故そのような意味になるのかなど、豊かな想像力がある: 5点


    if judge("熟語の意味を答えていない"):
        score = 1
    elif judge("不自然な意味になっている"):
        score = 3
    elif judge("杯, 伝それぞれの単語の意味を組み合わせた意味を考えられている"):
        score = 4

    return score


def judge_045(score: int, judge: callable) -> int:
    # - 長さを正解していない: 1点になる
    # - 長さを正解しているが、最長共通部分列を答えていない: 4点
    # - 長さを正解しているうえで、最長共通部分文字列を答えている: 5点

    if judge("長さを正解していない"):
        score = 1
    elif judge("長さを正解しているが、最長共通部分列を答えていない"):
        score = 4
    elif judge("長さを正解しているうえで、最長共通部分文字列を答えている"):
        score = 5
    return score


def judge_046(score: int, judge: callable) -> int:
    # - ジョークではないと答えている: 1点になる
    # - ジョークであると答えているが、説明がない: 4点になる
    # - ジョークであると答えていて、ジョークの内容を説明している: 5点

    if judge("ジョークではないと答えている"):
        score = 1
    elif judge("ジョークであると答えていて、ジョークの内容を説明している"):
        score = 5
    elif judge("ジョークであると答えているが、説明がない"):
        score = 4
    
    return score


def judge_047(score: int, judge: callable) -> int:
    # - 不正解の場合: 1点になる
    # - 正解の場合: 5点になる
    
    if judge("正解である"):
        score = 5
    else:
        score = 1
    return score


def judge_048(score: int, judge: callable) -> int:
    # - 男, あるいは医者であると回答した場合: 3点
    # - 曖昧であると回答した場合: 4点
    # - 曖昧であると回答し、その理由も説明している場合: 5点

    if judge("曖昧であると回答しており、その理由も説明している"):
        score = 5
    elif judge("曖昧であると回答している"):
        score = 4
    elif judge("男、あるいは医者であると回答している"):
        score = 3
    
    return score


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


def judge_050(score: int, judge: callable) -> int:
    # - (1/3+33)*210/100  と正しく回答できた場合: 5点
    # - 1/3+33*210/100 と括弧をつけ忘れたのみの場合: 3点
    # - それ以外の場合: 1点

    if judge("(1/3+33)*210/100 と正しく回答できた"):
        score = 5
    elif judge("1/3+33*210/100 と括弧をつけ忘れたのみの場合"):
        score = 3
    else:
        score = 1
    return score


def judge_051(score: int, judge: callable) -> int:
    # - 「消防」とは「火を消すこと」や「消防士のこと」など辞書通りの回答: 2点
    # - 「消防」とは「火を消すことから転じてインターネット上の炎上コメントを消すこと」などのように辞書に載っていない意味を想像している: 3点
    # - 「消防」とは小学生の意味、のように正解しているが理由がない場合: 4点
    # - 「似た音を持つ別の短い表現に表される」という指示に従い、「消防」の読み（しょうぼう）を考慮した意味を想像している場合: 5点


    if judge("「似た音を持つ別の短い表現に表される」という指示に従い、「消防」の読み（しょうぼう）を考慮した意味を想像している"):
        score = 5
    elif judge("「消防」とは小学生の意味、のように正解しているが理由がない"):
        score = 4
    elif judge("「消防」とは「火を消すことから転じてインターネット上の炎上コメントを消すこと」などのように辞書に載っていない意味を想像している"):
        score = 3
    elif judge("「消防」とは「火を消すこと」や「消防士のこと」など辞書通りの回答である"):
        score = 2

    return score


def judge_052(score: int, judge: callable) -> int:
    # A. 子供が
    # B. 走った
    # C. 運んだ
    # 
    # - A,B,Cの3つの要素を1つ外すごとに-2点
    # - 余計な要素（e.g. 彼, 水）を1つ入れてしまうごとに-2点

    if not judge("「子供が」という必須要素が存在する"):
        score -= 2
    if not judge("「走った」という必須要素が存在する"):
        score -= 2
    if not judge("「運んだ」という必須要素が存在する"):
        score -= 2

    if judge("余計な要素が1つ以上存在する"):
        score -= 2
    if judge("余計な要素が2つ以上存在する"):
        score -= 2
    if judge("余計な要素が3つ以上存在する"):
        score -= 2
    if judge("余計な要素が4つ以上存在する"):
        score -= 2
    
    return score


def judge_053(score: int, judge: callable) -> int:
    # - 黄色やそれに近い色（黄土色）なら5点
    # - それ以外なら1点

    if judge("黄色やそれに近い色（黄土色）である"):
        score = 5
    else:
        score = 1
    return score


def judge_054(score: int, judge: callable) -> int:
    # A. 誤りを修正すること（キックトック→TikTok）ができるか
    # B. 「あなたが言いたいのはOOですか？」と聞き返したり、「おそらくOOのことだと思います」のように、入力に誤りが含まれ回答が不確実になってしまうことに配慮した回答になっているか
    # C. 1つのクエリの中に2つのエンティティ（TikTok, TikToker）があることを認識し、それぞれに対する説明を行うことができるか
    # 
    # - Aができていない場合: -2点
    #    - TikTokではなく「チクタクとは時計のなる音の擬音語のことです」など「娘がやっている」という条件を満たさない不正解のものだが誤りの修正を試みている場合: -1点のみ
    # - Bができていない場合: -2点
    # - Cができていない場合: -1点



    a_corrected_to_tiktok = judge("キックトックをTikTokに正しく修正できた")
    if not a_corrected_to_tiktok:
        a_attempted_correction_but_wrong = judge("TikTokではなく「チクタクとは時計のなる音の擬音語のことです」など「娘がやっている」という条件を満たさない不正解のものだが誤りの修正を試みている")
        if a_attempted_correction_but_wrong:
            score -= 1
        else:
            score -= 2

    b_handled_uncertainty = judge("入力に誤りが含まれ回答が不確実になってしまうことに配慮した回答になっている")
    if not b_handled_uncertainty:
        score -= 2

    c_recognized_and_explained_two_entities = judge("1つのクエリの中に2つのエンティティ（TikTok, TikToker）があることを認識し、それぞれに対する説明を行うことができた")
    if not c_recognized_and_explained_two_entities:
        score -= 1

    return score


def judge_055(score: int, judge: callable) -> int:
    # - 誤った選択肢を選んでいる場合: 1点
    # - 正しい選択肢を選べている場合: 4点
    # - 正しい選択肢を選び、その理由も回答できている場合: 5点
    # 
    # 
    # - 注: ここでのユーザーの「行くことはできる」には「営業している時間に行くことができる？」というニュアンスが込められているので、営業していない東京タワーの麓までいくことや、遠くから東京タワーを見ることはできる、などは認められない
    # - ヤマカンで選択肢を選んでも5点は取れないような点数設計にしています

    is_correct_choice_considering_opening_hours = judge(
        "営業している時間帯に東京タワーの展望台などに入ることができる旨の正しい選択肢を選んでいる"
    )
    
    is_reason_provided_and_appropriate = judge(
        "正しい選択肢を選んだ理由も適切に回答できている"
    )

    if is_correct_choice_considering_opening_hours and is_reason_provided_and_appropriate:
        return 5
    
    elif is_correct_choice_considering_opening_hours:
        return 4
    
    else:
        return 1


def judge_056(score: int, judge: callable) -> int:
    # ベースの得点:
    # - 今日は雨, お菓子を買っていた のいずれかを出力した場合: 4点
    # - 今日は雨, お菓子を買っていた の両方を出力した場合: 5点
    # 
    # 減点項目:
    # - 遠足は中止になる、と断言してしまった場合: -3点
    # - 遠足は中止になる可能性が高い、と出力した場合: -1点

    has_rain_output = judge("今日は雨と出力した")
    has_snack_output = judge("お菓子を買っていたと出力した")

    if has_rain_output and has_snack_output:
        score = 5
    elif has_rain_output or has_snack_output:
        score = 4
    else:
        score = 0

    if judge("遠足は中止になると断言した"):
        score -= 3
    elif judge("遠足は中止になる可能性が高いと出力した"):
        score -= 1
    
    if score < 0:
        score = 0

    return score


def judge_057(score: int, judge: callable) -> int:
    # - はい、と答えた場合: 1点
    # - いいえ、と答えたがその後の発話が会話として不自然である場合: 3点
    # - いいえ、と答え自然な発話をしている場合: 5点
    #    - 「いいえ、シワは増えていません」くらい簡素でも5点でいい

    if judge("はい、と答えている"):
        score = 1
    elif judge("いいえ、と答えている"):
        if judge("その後の発話が会話として不自然である"):
            score = 3

    return score


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


def judge_059(score: int, judge: callable) -> int:
    # - 不正解の場合: 1点
    # - 正解しているが理由や説明がない場合: 4点
    # - 正解していて理由や説明がある場合: 5点

    if judge("不正解である"):
        score = 1
    elif judge("正解している") and judge("理由や説明がある"):
        score = 5
    elif judge("正解している") and not judge("理由や説明がある"):
        score = 4
    
    return score


def judge_060(score: int, judge: callable) -> int:
    # - 不正解の場合: 1点
    # - 正解しているが理由や説明がない場合: 4点
    # - 正解していて理由や説明がある場合: 5点


    if judge("不正解である"):
        score = 1
    elif judge("正解しているが理由や説明がない"):
        score = 4

    return score


def judge_061(score: int, judge: callable) -> int:
    # - 不正解の場合: 1点
    # - 正解しているが理由や説明がない場合: 4点
    # - 正解していて理由や説明がある場合: 5点

    if judge("不正解である"):
        score = 1
    elif judge("正解しているが理由や説明がない"):
        score = 4
    
    return score


def judge_062(score: int, judge: callable) -> int:
    # - 2つの問題に対して、1つ間違えるごとに-2点
    
    if judge("問題1が不正解である"):
        score -= 2
    if judge("問題2が不正解である"):
        score -= 2
    return score


def judge_063(score: int, judge: callable) -> int:
    # - 不正解の場合: 1点
    # - 正解しているが理由や説明がない場合: 4点
    # - 正解していて理由や説明がある場合: 5点

    is_correct = judge("正解している")
    has_explanation = judge("理由や説明がある")

    if not is_correct:
        score = 1
    elif not has_explanation:
        score = 4
    
    return score


def judge_064(score: int, judge: callable) -> int:
    # ベースの得点:
    # - Summary, Summarizeなどのサマるの語源を想像して踏まえた意味を答えている: 5点
    # - 「OOすると8つということですね。」という文脈に適した意味を答えている: 4点
    # 
    # 減点項目:
    # - 「サマる」は一般的な日本語ではない（一部のビジネスマンが使用する単語）ので、「〜だと考えられます」のようにその意味を断言してはならず。意味を断言してしまった場合 -1点

    if judge("Summary, Summarizeなどのサマるの語源を想像して踏まえた意味を答えている"):
        score = 5
    elif judge("「OOすると8つということですね。」という文脈に適した意味を答えている"):
        score = 4
    else:
        score = 0

    if judge("意味を断言してしまっている"):
        score -= 1

    return max(0, score)


def judge_065(score: int, judge: callable) -> int:
    # - 不正解の場合: 1点
    # - ヴィンセントであることを正解している: 4点
    # - ヴィンセントであることを正解した上で、9歳であることにも触れている: 5点

    if judge("ヴィンセントであることを正解しており、かつ9歳であることにも触れている"):
        return 5
    elif judge("ヴィンセントであることを正解している"):
        return 4
    else:
        return 1


def judge_066(score: int, judge: callable) -> int:
    # - 不正解の場合: 1点
    # - 正解の文を記述できている: 4点
    # - 正解の文を記述できている上で、その理由も説明している: 5点

    is_correct_sentence = judge("正解の文を記述できている")
    is_reason_explained = judge("その理由も説明している")

    if is_correct_sentence and is_reason_explained:
        score = 5
    elif is_correct_sentence:
        score = 4
    else:
        score = 1
    
    return score


def judge_067(score: int, judge: callable) -> int:
    # - 「滅多に」を使った上で適切に言い換えられている: 5点
    # - 「めったに」を使った上で適切に言い換えられているが、漢字ではなくひらがなになってしまっている: 4点
    # - 「滅多に」を使った上で言い換えているが、意味が少し変わってしまっている: 3点
    #     - e.g. 最近の私は滅多に海に行くことがありません
    # - 「滅多に」を使っていなかったり、大きく意味が変わってしまっている

    if judge("「滅多に」を使っていなかったり、大きく意味が変わってしまっている"):
        score = 0
    elif judge("「滅多に」を使った上で言い換えているが、意味が少し変わってしまっている"):
        score = 3
    elif judge("「めったに」を使った上で適切に言い換えられているが、漢字ではなくひらがなになってしまっている"):
        score = 4

    return score


def judge_068(score: int, judge: callable) -> int:
    # - ひまわりであると正解している場合: 5点
    # - 植物である・花である、などと答えている場合: 4点
    #     - 注: ひまわりは植物の一部なので間違ってはいない
    # - 「太陽の光を顔に浴びるのが好きな女性」のように擬人法を見抜けていない回答の場合: 3点
    # - それ以外: 1点

    if judge("ひまわりであると正解している"):
        score = 5
    elif judge("植物である・花である、などと答えている"):
        score = 4
    elif judge("擬人法を見抜けていない回答である"):
        score = 3
    else:
        score = 1
    
    return score


def judge_069(score: int, judge: callable) -> int:
    # ベースの得点:
    # - 以下のいずれかを満たす場合: 5点
    #     - 共感を呼ぶ答えをひとひねりしている場合
    #     - 一般的にドラゴン退治では必要としないことを述べている場合
    #     - 面白い場合
    # - 大喜利ではなく単純にドラゴン退治のアドバイスの回答をしている場合: 2点
    # 
    # 減点項目:
    # - 大喜利としては長すぎる3文以上の回答であったり、文体が笑いを誘うものではない場合, 語感が悪い場合: -1点
    # - 1つ目の例題に関して出力してしまっている場合: -1点

    is_5_point_answer = (
        judge("共感を呼ぶ答えをひとひねりしている") or
        judge("一般的にドラゴン退治では必要としないことを述べている") or
        judge("面白い")
    )

    is_2_point_advice = judge("大喜利ではなく単純にドラゴン退治のアドバイスの回答をしている")

    if is_2_point_advice and not is_5_point_answer:
        score = 2
    else:
        score = 5

    if judge("大喜利としては長すぎる3文以上の回答である、または文体が笑いを誘うものではない、または語感が悪い"):
        score -= 1
    if judge("1つ目の例題に関して出力してしまっている"):
        score -= 1

    return score


def judge_070(score: int, judge: callable) -> int:
    # - 共通点をいくつか提示できている場合: 5点
    # - 共通点を1つのみ提示できている場合: 4点
    # - 共通点をいくつか提示できているが、一部誤りを含む場合: 3点
    # - 共通点を述べていない場合: 1点
    #     - りんごとバナナの説明をそれぞれしてしまっている場合、違いのみを述べている場合など
    if judge("共通点を述べていない") or \
       judge("りんごとバナナの説明をそれぞれしている") or \
       judge("違いのみを述べている"):
        return 1

    if judge("共通点をいくつか提示できているが、一部誤りを含む"):
        return 3

    if judge("共通点を1つのみ提示できている"):
        return 4

    return 5


def judge_071(score: int, judge: callable) -> int:
    # - 生成した前提から仮説がある程度導けるものの完全には導けない場合: 5点
    # - 生成した前提から仮説が完全に導けてしまう場合: 3点
    #    - e.g. 男女2人が赤いバラを見ている
    # - 生成した前提から仮説があまり導けない場合: 3点
    #     - e.g. 2人の男女がレストランにいる

    if judge("生成した前提から仮説が完全に導けてしまう"):
        score = 3

    if judge("生成した前提から仮説があまり導けない"):
        score = 3

    return score


def judge_072(score: int, judge: callable) -> int:
    # ベースの得点:
    # - 新たに作成した選択肢が絵本に近いが、「主に子ども向けのもので、イラストのついた物語が書かれている」という条件を満たしていない: 5点
    # - 新たに作成した選択肢が絵本に近いが、「主に子ども向けのもので、イラストのついた物語が書かれている」という条件を満たしてしまっている: 3点
    #     - 例えば「漫画」などはこの条件を満たしてしまっている
    # - 新たに作成した選択肢が絵本に近くないが、「主に子ども向けのもので、イラストのついた物語が書かれている」という条件を満たしてはいない: 3点
    # 
    # 減点項目:
    # - 選択肢の中に重複したものがある: -2点
    # - 指示に従えてなく、具体的な絵本を4-5こ挙げている場合など: -4点
    # 
    # 注意事項:
    # - 選択肢を5つ作ることが、絵本以外の選択肢を4つ作ることなのか5つ作ることなのかが若干曖昧な指示になっているので、作成された絵本以外の選択肢の数が4つでも5つでも採点には影響させない

    
    is_close_to_picture_book = judge("新たに作成した選択肢が絵本に近い")
    meets_children_criteria = judge("新たに作成した選択肢が「主に子ども向けのもので、イラストのついた物語が書かれている」という条件を満たしている")

    if (is_close_to_picture_book and meets_children_criteria) or \
       (not is_close_to_picture_book and not meets_children_criteria):
        score = 3

    if judge("選択肢の中に重複したものがある"):
        score -= 2
    
    if judge("指示に従えてなく、具体的な絵本を4-5個挙げている"):
        score -= 4
        
    return score


def judge_073(score: int, judge: callable) -> int:
    # - 意味を変えてしまう場合: -2点
    # - 少し読みにくいが、元の文と比べて読みやすくなっている場合: -1点
    # - 修正しているものの、依然として不自然で読みにくい場合: -2点

    if judge("元の文の意味を変えてしまっている"):
        score -= 2
    if judge("修正しているものの、依然として不自然で読みにくい"):
        score -= 2
    if judge("少し読みにくいが、元の文と比べて読みやすくなっている"):
        score -= 1
    
    return score


def judge_074(score: int, judge: callable) -> int:
    # - 生徒の要約をベースに大きな変更を加えずに改善し、改善点を説明する: 4点
    # - 生徒の要約をベースに大きな変更を加えずに改善する: 4点
    # - 生徒の要約をベースにせずに、単純にゼロから記事を要約している: 3点
    # - 生徒の要約をベースにせずに、単純にゼロから記事を要約しているが、その要約の品質が低い: 2点


    if judge("生徒の要約をベースにせずに、単純にゼロから記事を要約しており、その要約の品質が低い"):
        score = 2
    elif judge("生徒の要約をベースにせずに、単純にゼロから記事を要約している"):
        score = 3
    elif judge("生徒の要約をベースに大きな変更を加えずに改善している"):
        score = 4

    return score


def judge_075(score: int, judge: callable) -> int:
    # - 文中で明示されていないことを想像で補足しつつ、メインメッセージが「OOはないが、XXはある」である場合: 5点
    # - 文中で明示されていないことを想像で補足しつつも、メインメッセージが「OOがないこと」である場合: 4点
    #     - ある映画についてのブルーレイ版が存在しないこと
    # - 文中で明示されていること（ブルーレイが存在しないこと）のみを述べてしまう場合: 3点
    # 
    # 補足:
    # - ここでは「は」という助詞が対比の意味で使われているということを想像する必要がある


    if judge("文中で明示されていないことを想像で補足しつつ、メインメッセージが「OOはないが、XXはある」である"):
        score = 5
    elif judge("文中で明示されていないことを想像で補足しつつも、メインメッセージが「OOがないこと」である"):
        score = 4
    elif judge("文中で明示されていること（ブルーレイが存在しないこと）のみを述べてしまう"):
        score = 3
    
    return score


def judge_076(score: int, judge: callable) -> int:
    # A. 全ての単語を使う
    # B. 順番に使う
    # C. 文として自然になっている
    # 
    # - A, B, Cそれぞれ間違えるごとに-2点

    if judge("全ての単語を使っていない"):
        score -= 2
    if judge("単語を順番通りに使っていない"):
        score -= 2
    if judge("文として不自然である"):
        score -= 2
    return score


def judge_077(score: int, judge: callable) -> int:
    # - 正解している場合: 5点
    # - 不正解の場合: 1点

    if judge("正解している"):
        score = 5
    else:
        score = 1
    return score


def judge_078(score: int, judge: callable) -> int:
    # - Aに対応するQが書けている: 5点
    # - Qは書けているが、Aと対応していない: 3点
    #     - e.g. ズボンの履き方は？
    # - Qが書けていない: 1点

    if judge("Qが書けていない"):
        score = 1
    elif judge("Qは書けているが、Aと対応していない"):
        score = 3
    return score


def judge_079(score: int, judge: callable) -> int:
    # - 正解の場合: 5点
    # - 不正解の場合: 1点
    #     - 「飲むことが好きなこと」なども不正解
    
    if judge("不正解である"):
        score = 1
        
    return score


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


def judge_082(score: int, judge: callable) -> int:
    # 出題意図:
    # - 単に言い換えの正誤判定問題ではなく、ユーザーの意図や困り事を汲んで役に立つAIアシスタントとして振る舞う必要がある
    # 
    # ベースとなる得点:
    # - 言い換えの正誤判定に正解し、その上でユーザーの役に立つようにそれぞれの単語の意味の説明や、より適切な言い換えを提示する: 5点
    # - 言い換えの正誤判定に正解しただけ: 4点
    # - 正誤判定が不正解（言い換えが適切である）: 1点

    if judge("正誤判定が不正解である"):
        return 1
    
    if judge("ユーザーの役に立つようにそれぞれの単語の意味の説明や、より適切な言い換えを提示していない"):
        return 4
        
    return score


def judge_083(score: int, judge: callable) -> int:
    # A. 何をやろうとしているか
    # B. なぜやろうとしているか
    # 
    # - A, Bを1つ間違えるごとに-2点
    
    if judge("「何をやろうとしているか」が間違っている、または記述がない"):
        score -= 2
    
    if judge("「なぜやろうとしているか」が間違っている、または記述がない"):
        score -= 2
        
    return score


def judge_084(score: int, judge: callable) -> int:
    # - 検索クエリとして適切なフォーマットで出力できていない場合: -2点
    #     - e.g. スキー用品のブランドや種類、特徴について知りたい!
    # - ユーザーの意図（スキーストックを選ぼう・購入しようとしている）を汲んでいない場合: -1点
    #     - e.g. スキーブーツ 選び方 などを一番最初に出力してしまう

    if judge("検索クエリとして適切なフォーマットで出力できていない"):
        score -= 2
    if judge("ユーザーの意図（スキーストックを選ぼう・購入しようとしている）を汲んでいない"):
        score -= 1
    return score


def judge_085(score: int, judge: callable) -> int:
    # - メインとなる指示である「映画スラムダンクを視聴者に薦めるタローとコタローの対話の生成」ができていない: -2点
    # - そのほかの細かい指定を間違えるごとに1点減点
    #     - タローは物知りで、コタローの疑問に答えてくれる
    #     - まるでスポーツの試合を見ているかのように迫力のあるバスケのシーン
    #     - 漫画の原作を読んだことのない人でも楽しめる、映画として完結しているストーリー
    #     - 来月に公開が終了する
    #     - 10行~15行程度の対話

    if judge("映画スラムダンクを視聴者に薦めるタローとコタローの対話が生成されていない"):
        score -= 2
    if judge("タローが物知りで、コタローの疑問に答える役割を果たしていない"):
        score -= 1
    if judge("スポーツの試合を見ているかのような迫力のあるバスケのシーンについての言及がない、または不適切である"):
        score -= 1
    if judge("漫画原作未読者も楽しめる完結したストーリーであることの言及がない、または不適切である"):
        score -= 1
    if judge("来月に公開が終了することの言及がない"):
        score -= 1
    if judge("対話が10行~15行程度の範囲外である"):
        score -= 1
    return score


def judge_086(score: int, judge: callable) -> int:
    # 出題意図:
    # - ツールとその説明を与えたときにLLMがそれらをAgentのように使いこなせるかを見る
    # 
    # ベースとなる得点:
    # - ピザジャンボのSを注文した: 5点
    # - ラーメン屋に行った、ラーメンを出前として注文した: 3点
    # 
    # 減点項目:
    # - 捏造や誤りを含む: -1点

    if not judge("ピザジャンボのSを注文した"):
        if judge("ラーメン屋に行った、ラーメンを出前として注文した"):
            score = 3
        else:
            score = 0

    if judge("捏造や誤りを含む"):
        score -= 1

    if score < 0:
        score = 0

    return score


def judge_087(score: int, judge: callable) -> int:
    # 減点項目:
    # - シチュエーションとして適切ではない発言が1つある: -1点
    # - シチュエーションとして適切ではない発言が2つ以上ある: -2点
    # - いくつかではなく1つのみ答えてしまう: -2点

    if judge("シチュエーションとして適切ではない発言が2つ以上ある"):
        score -= 2
    elif judge("シチュエーションとして適切ではない発言が1つある"):
        score -= 1
    
    if judge("いくつかではなく1つのみ答えている"):
        score -= 2
        
    return score


def judge_088(score: int, judge: callable) -> int:
    # - 新入社員のオンボーディングに必要で、かつ新入社員が早く馴染めるようにするための施策を提案している: 5点
    # - 新入社員のオンボーディングに必要だが、新入社員が早く馴染めるようにするためではない施策を提案している: 3点
    #     - e.g. 契約書をチェックし、福利厚生について説明しましょう

    if judge("新入社員のオンボーディングに必要だが、新入社員が早く馴染めるようにするためではない施策を提案している"):
        score = 3
    
    return score


def judge_089(score: int, judge: callable) -> int:
    # - 完全正解: 5点
    # - 1,2このみ間違えている: 3点
    # - それ以上間違えている: 1点
    
    if judge("1つか2つ間違えている"):
        return 3
    elif judge("それ以上間違えている"):
        return 1
    return score


def judge_090(score: int, judge: callable) -> int:
    # - 誰が所有しているか不明であり、その理由も説明している: 5点
    # - 誰が所有しているか不明であるとのみ出力している: 4点
    # - 貴族が所有している、と出力している: 3点
    # - OOが所有している可能性が高い、などのように断言は避けながら推測を述べている: 3点
    # - それ以外: 1点

    if judge("誰が所有しているか不明であり、その理由も説明している"):
        score = 5
    elif judge("誰が所有しているか不明であるとのみ出力している"):
        score = 4
    elif judge("貴族が所有している、と出力している") or \
         judge("OOが所有している可能性が高い、などのように断言は避けながら推測を述べている"):
        score = 3
    else:
        score = 1
        
    return score


def judge_091(score: int, judge: callable) -> int:
    # ベースとなる得点:
    # - どちらがポジティブか正解した上で、理由も述べている: 5点
    # - どちらがポジティブか正解したが、理由は述べていない: 3点
    # - どちらがポジティブか不正解: 1点
    # 
    # 減点項目:
    # - 「じまん」の意味を誤って説明している: -1点
    # - 「ほこり」の意味を誤って説明している, 「埃」と勘違いしている: -1点
    
    if judge("「じまん」の意味を誤って説明している"):
        score -= 1
    if judge("「ほこり」の意味を誤って説明している、または「埃」と勘違いしている"):
        score -= 1
    return score


def judge_092(score: int, judge: callable) -> int:
    # - 情景を思い浮かび上がらせるような表現を追加して、風の強さをより強く表現している: 5点
    #     - e.g. 「飛ばされた帽子が道路を転がるように流されていた。」
    # - 小説の文体としては不十分だが、風の強さをより強く表現している: 3点
    #     - e.g. 風がとても強く吹いていた
    # 
    # 減点項目:
    # - 弱い風の表現がある: -1点
    #     - e.g. 風が私の髪を撫でた
    # - 不自然な表現: -1点

    if judge("情景を思い浮かび上がらせるような表現を追加して、風の強さをより強く表現している"):
        score = 5
    elif judge("小説の文体としては不十分だが、風の強さをより強く表現している"):
        score = 3
    else:
        score = 0

    
    if judge("弱い風の表現がある"):
        score -= 1
    if judge("不自然な表現がある"):
        score -= 1
        
    return max(0, score)


def judge_093(score: int, judge: callable) -> int:
    # - シチュエーションを踏まえていない: -2点
    # - 小説中の母親のセリフの文体として不適切: -2点
    
    if judge("シチュエーションを踏まえていない"):
        score -= 2
    if judge("小説中の母親のセリフの文体として不適切"):
        score -= 2
    return score


def judge_094(score: int, judge: callable) -> int:
    # - どんな生き物を作りたいか, 特徴や能力について説明のいずれかが欠けている: -2点
    # - オリジナルではなく既存の動物について記述している: -4点

    if judge("どんな生き物を作りたいかの説明が欠けている") or judge("特徴や能力についての説明が欠けている"):
        score -= 2
    if judge("オリジナルではなく既存の動物について記述している"):
        score -= 4
    return score


def judge_095(score: int, judge: callable) -> int:
    # - 全て正解: 5点
    # - 抜け漏れが1つのみ or 余計な回答を1つだけしている: 4点
    # - 2つ以上ミス: 3点
    # - それ以外: 1点

    if judge("全て正解"):
        return 5
    elif judge("抜け漏れが1つのみ") or judge("余計な回答を1つだけしている"):
        return 4
    elif judge("2つ以上ミス"):
        return 3
    else:
        return 1


def judge_096(score: int, judge: callable) -> int:
    # - 筆者の意図を概ね正しくかけ、理由も説明できている: 5点
    # - 筆者の意図を概ね正しくかけた: 4点
    # - 筆者の意図を想像したが、少しズレた回答になっている: 3点
    #     - e.g. 筆者は自身の成功体験を共有する意図でこの文章を書きました
    # - 本文の一部を切り取っているだけな場合: 1点
    #     - e.g. 彼はバブル期に大金持ちになり豊かな生活に日夜明け暮れたことを示すため

    if judge("本文の一部を切り取っているだけである"):
        score = 1
    elif judge("筆者の意図を想像したが、少しズレた回答になっている"):
        score = 3
    elif judge("筆者の意図を概ね正しくかけたが、理由は説明できていない"):
        score = 4
    return score


def judge_097(score: int, judge: callable) -> int:
    # A. 花粉症の対策をする
    # B. 春の自然を楽しむコツをあげる
    # C. 3つ回答する
    # 
    # A, B, Cそれぞれ間違うごとに-2点

    if not judge("花粉症の対策をしている"):
        score -= 2

    if not judge("春の自然を楽しむコツをあげている"):
        score -= 2
        
    if not judge("3つ回答している"):
        score -= 2
        
    return score


def judge_098(score: int, judge: callable) -> int:
    # - 完全正解: 5点
    # - 正解しているが数字とアルファベットのペアを明確に回答していない: 4点
    # - 1,2このみ間違えている: 3点
    # - それ以上間違えている: 1点

    if judge("3つ以上の間違いがある"):
        score = 1
    elif judge("1つまたは2つの間違いがある"):
        score = 3
    elif judge("正解しているが、数字とアルファベットのペアを明確に回答していない"):
        score = 4

    return score


def judge_099(score: int, judge: callable) -> int:
    # - 物語の続きとして豊かに物語の続きを書いている: 5点
    # - 物語の続きとして豊かに物語の続きを書いているが、少し不自然な箇所がある: 4点
    #     - e.g. いきなり警察官が出てきて世界観を壊す
    #     - e.g. 母親が登場していないのに母との感動の再会をする、など
    # - 物語の続きを予想しているが、表現が豊かではない場合: 3点
    #     - e.g. 主人公は謎の人物との交流を通じて成長していきます。
    # -

    if judge("物語の続きを予想しているが、表現が豊かではない"):
        score = 3
    elif judge("物語の続きとして豊かに物語の続きを書いているが、少し不自然な箇所がある"):
        score = 4
    
    return score


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
