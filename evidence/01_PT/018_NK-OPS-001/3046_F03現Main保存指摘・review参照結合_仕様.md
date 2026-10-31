# F03 現Main保存指摘・review参照結合 仕様

2026-10-31 / PG-D973 / 群3381 / 主WBS-F03。開始0.5/2/5共有pp cap10固定、used50。Production6b53/normal14216固定。G13一覧3044～45の次依存として、製造965Mainだけの現source指摘を保存済み解析から構成する。

元PG13253全1821Java/8022rawのうち、旧db33と現6b53でbyte不変の962Mainを使い、変更したquery三MainだけPG14226の新18rawへ置換する。全965のpath/byteを現Git/worktreeで照合し、元XML/findingsのhash・processing errorなしを確認。旧Test指摘、Characterization四、旧source runtime/native/coverageは合算しない。新scanner/Product/VM/DB/鍵/外部操作なし。

公開F03 review.jsonのうち明示family名で選び、成功manifest/reviewhashとrow path/current source hash/全attributes座標/ruleが一致したものだけ参考リンクを付ける。選択inputとhashを固定保存。raw保持/静的レビューのみで、参考リンクの存在を適用性合格・非違反・動的PASSにしない。未参照は詳細queueとして保存する。重複診断occurrenceを消さず個別ID化する。独立検証は集計と全965source/置換条件/元rows/参照条件/未分類・非転用を照合し、変異拒否する。

元計画・raw catalog・過去context ledgerは改変せず、新current Main観測ledgerだけ作る。旧1491などのderived値と新full解析母集団を混同しない。F03/451/正式/工数/HOLD不変更。後続は未参照queueから必要なsource-method PGレビューを選ぶ。
