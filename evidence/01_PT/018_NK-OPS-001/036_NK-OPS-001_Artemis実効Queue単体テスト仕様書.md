# NK-OPS-001 Artemis実効Queue単体テスト仕様書

PG223、RD MQ-001/002/009/010・SYS-004・TST-001～005、UI231/251、SS311 §7・321 §3/4/13・341 §10・342 §4。対象`ArtemisReadinessClient.verifyTopology`。callerが限定Ops credentialで開いた借用Artemis Core sessionについて、稼働Brokerの全6 Address/Queue実効トポロジーを確認する。単なるJMS consumer生成やXML静的parseではない。sessionはcaller所有で、検査ではQueue作成/削除、message送受信をしない。

| Test ID | fixture・入力/操作 | 独立期待値 |
|---|---|---|
| PT-OPS-MQ-001 | SS321の隔離実Broker/File Journal、Core session、verifyTopology | 6 Addressと各1 Queueが存在、ANYCASTのみ、Queue durable、temporary/auto-created=false、名前・所属Address一致、auto-create=false。期待6組はSS321 literalから独立列挙。借用sessionは呼出後も使用可能 |
| PT-OPS-MQ-002 | 稼働Brokerから承認済みQueueを1件削除して再照会 | Queue不存在で固定redacted起動拒否。黙って再作成しない |
| PT-OPS-MQ-003 | Core query結果のAddress/Queue各属性を1項目ずつ変異・null/欠落 | 誤Routing/非durable/別名/別Address/auto-create等のいずれも拒否。列挙済み他5組で欠落を覆い隠さない |
| PT-OPS-MQ-004 | null session、Core provider例外/未知Runtime/close境界 | nullはfail-fast、provider本文を外部診断へ出さず固定例外。借用sessionをcloseしない。並行呼出の観点も検査 |

本PTが確認するのはSS321 §13のうち6組の実効トポロジーだけ。journal load error、acceptor loopback、disk<90%、DLQ/Expiry閾値、security role、address settings全体、Expiry purgeは別の必須readiness gate。Production credential取得/親起動/実NK CHR/IT/STも未完了。実行command、環境、source commit、exit/coverage/結果、証跡path/hashは037とmanifestへ記録する。failed/error/skippedを合格算入しない。
