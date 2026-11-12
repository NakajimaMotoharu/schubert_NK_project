# NK-ASY-001 空回答provider単体テスト仕様書

2026-10-22暫定追補：providerのBusiness/Runtime failure graphをQuestionWorkerのERROR/DLQへ分類する前のfatal保持は、011_NK-QST-001/009 provider例外graph仕様と対応結果へ追跡する。元Error/PROCESSING保持・Error無しcycleの既結果を独立に確認する。STB001～005/旧正式provider認定を置換せず、実Root/native/ACK/外部AI/IT/STの合格へ外挿しない。

PG420補足（2026-10-02、暫定・正式provider認定は不変更）：実`QuestionWorkerService`/固定`AnswerBusinessException`のDB/JMS/元ACK接続は011_NK-QST-001の005受付・再送・Worker仕様と006実績へ追跡する。AWORK001～013で本STUB5を再使用し、実PG18・Artemis・削除三点・再配送/最終DLQ・監査を確認中。本文/provider/時刻の単独契約を本書のSTB001～005で維持し、外部AI/ordinary native ready/全100%/IT/STは未受入。

計測対象は実行codeを持つAnswerResult/StubAnswerProvider全体。AnswerProviderは抽象method宣言のみで実行命令がなく、JaCoCo除外設定は追加しない。分岐命令が生成されない場合のbranchは0/0としてmanifestへ明示し、missed branchのあるclassを0/0へ置換しない。

AnswerResultのrecord生成accessor/equals/hashCodeはJaCoCo0.8.15のXMLでは独立method counterに現れず、手書きconstructor/toStringの2methodが記録される。恣意的なexcludes/Generated付与ではない。生成methodの動作もSTB001/004/005のgetter・等値/不等値/hash assertionで確認し、計測上の非表示を未試験扱いの免除に使わない。

PG190、RD123 QST003/101、UI224§5/7・236§12、SS311/312§8.1。AnswerProvider.answer、StubAnswerProvider constructor/answer、AnswerResult constructor/body/answeredAt/equality/hash/toString。providerだけを対象とし、worker DB/JMS/ACKや外部AIは未実装。

| Test ID | method | 入力・事前条件・操作 | 独立期待 |
|---|---|---|---|
| PT-ASY-STB001 | emptyAnswerAndClock | 固定Clock2種、公開質問1/4096文字、interfaceから呼出 | bodyは常に空、Instantは与えた固定値と完全一致しnanosecondを丸めない、1呼出1時計読取 |
| PT-ASY-STB002 | nullContracts | null clock/question/body/time | 各constructor/API境界拒否、null question時時計を読まない、NPE catch正常化なし |
| PT-ASY-STB003 | clockFailures | Runtime/Errorの固定注入、null Instant | 未知例外は同一objectで伝播、nullは成功結果にならず、代替日時/空結果へのfallbackなし |
| PT-ASY-STB004 | resultValueAndRedaction | 合成本文/時刻、等値/不等値 | getterのみ正値、equals/hash整合、toStringは固定REDACTEDで本文/時刻なし |
| PT-ASY-STB005 | concurrentCallsAndEvidence | 同provider64並行、AtomicInteger独立Clock | 全64時刻を独立期待集合と照合、重複/欠落なし、body空、公開traceに質問/秘密値なし |

入力は公開合成文字のみ、Clockはtestで与えたliteral Instantを返しexpected生成にProduction methodを呼ばない。全line/method/class/branch100%、NullAway/static/negativeを要求。分岐のないclassは0/0（除外設定でなく計測対象）を明記する。結果/環境/command/sourcecommit/hashは002・evidence/manifest.jsonへ正式成功後記録。現在未実装・未実行。


WBS-P012-01公開source契約/独立期待値/TestIDは[4102_P01201質問FIFO消費原二source契約対応.md](4102_P01201質問FIFO消費原二source契約対応.md)。metadataのみ、新PT/coverage/正式受入0。
