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
