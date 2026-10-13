# PG2478 BrokerJournal独立境界

NK-OPS-001／BrokerJournalEvidence anchor/contentSha256/consume/consumeClosedHistory/fields。RDの障害検知・監査秘匿要求、UI運用設計、SS321§13/341/343、SSC125/131/132。主担当WBS-P017-10、N04は参照費0。events0639/0640の着手前予算0.5/1.5/4週次共有ppを保持する。Production cdbc07cdf77370d521e64de8b327da7f6752139b、PG2404全3637PT・1643Main、PG2474資格済みlatest九nativeのみを使用し、旧sourceのnativeは輸入しない。

| Test ID／method先頭 | 独立fixture・操作 | 期待値・根拠 |
|---|---|---|
| PT-BJ2478-001／bj2478001 | 手書きvendor2.56 JSON、boot/Unit/時刻/priority/Invocation/版/メッセージ差、0/65536/65537 byte、UTF8/null | SSの真正metadata条件。正規anchorの三固定値・redacted表示、正確65536 byteは受理、未知/欠落/異常はIOException、null契約は拒否 |
| PT-BJ2478-002／bj2478002 | 空/4MiB+1/末尾LF欠落/不正UTF8/配列/null型/二object/孤立surrogate | 正規化で欠落を成功化しない。IOException、診断へraw fixtureを含めない。null契約拒否 |
| PT-BJ2478-003／bj2478003 | 手書きTreeMapからNKJOURNAL1/ROW/ordinal/key/UTF8hexを独立構成し標準SHA256、cursor/time/digestを一つずつ変更 | 三vendor eventの完全historyだけ成功、raw SHAを独立計算。終了anchor不一致は拒否。expectedをproduction methodから作成しない |
| PT-BJ2478-004／bj2478004 | 専用test JVM、provider registryの全除去とfinallyで元order復元 | 両digest経路のprovider欠落は秘匿IOException。復元後known SHA256 abc固定vectorとgolden三eventが正常。並列無効・JUnit Isolated。VM/業務providerに作用しない |

実commandはclean固定後、固定PYTHONPATHで `python3 -B tools/quality/pg2478_broker_journal_selected.py`。専用LANのfresh PG2478-selected-v1のみ、immutable PG2404 Main/fixtures/依存JARと当九nativeの前後hashを検査、javac -Xlint:all -Werror、独立JUnit XML四件/FES/aborted/not-runを確認する。全Main classByteMismatch0と六moduleの四counter/XML/hashを保存する。未実行を合格にしない。Production変更・VM操作0、全体回帰/451正式受入/工程完了はこの選択試験では宣言しない。

既実装が仕様違反なら修正前にBUG/YKTを起票する。fixture/新工具の初回未完成は試験製造として実失敗を保存し、成功へ補完しない。実行日時/commit/command/OS/JDK/終了値/入力SHA/実XML/coverage/関連番号は結果manifestで追記する。
