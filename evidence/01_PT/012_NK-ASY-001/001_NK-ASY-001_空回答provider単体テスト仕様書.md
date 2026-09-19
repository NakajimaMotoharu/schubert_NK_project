# NK-ASY-001 空回答provider単体テスト仕様書

計測対象は実行codeを持つAnswerResult/StubAnswerProvider全体。AnswerProviderは抽象method宣言のみで実行命令がなく、JaCoCo除外設定は追加しない。分岐命令が生成されない場合のbranchは0/0としてmanifestへ明示し、missed branchのあるclassを0/0へ置換しない。

PG190、RD123 QST003/101、UI224§5/7・236§12、SS311/312§8.1。AnswerProvider.answer、StubAnswerProvider constructor/answer、AnswerResult constructor/body/answeredAt/equality/hash/toString。providerだけを対象とし、worker DB/JMS/ACKや外部AIは未実装。

| Test ID | method | 入力・事前条件・操作 | 独立期待 |
|---|---|---|---|
| PT-ASY-STB001 | emptyAnswerAndClock | 固定Clock2種、公開質問1/4096文字、interfaceから呼出 | bodyは常に空、Instantは与えた固定値と完全一致しnanosecondを丸めない、1呼出1時計読取 |
| PT-ASY-STB002 | nullContracts | null clock/question/body/time | 各constructor/API境界拒否、null question時時計を読まない、NPE catch正常化なし |
| PT-ASY-STB003 | clockFailures | Runtime/Errorの固定注入、null Instant | 未知例外は同一objectで伝播、nullは成功結果にならず、代替日時/空結果へのfallbackなし |
| PT-ASY-STB004 | resultValueAndRedaction | 合成本文/時刻、等値/不等値 | getterのみ正値、equals/hash整合、toStringは固定REDACTEDで本文/時刻なし |
| PT-ASY-STB005 | concurrentCallsAndEvidence | 同provider64並行、AtomicInteger独立Clock | 全64時刻を独立期待集合と照合、重複/欠落なし、body空、公開traceに質問/秘密値なし |

入力は公開合成文字のみ、Clockはtestで与えたliteral Instantを返しexpected生成にProduction methodを呼ばない。全line/method/class/branch100%、NullAway/static/negativeを要求。分岐のないclassは0/0（除外設定でなく計測対象）を明記する。結果/環境/command/sourcecommit/hashは002・evidence/manifest.jsonへ正式成功後記録。現在未実装・未実行。
