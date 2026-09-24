# NK-OPS-001 Artemis実効Address設定 PT実行結果

PG237/PT-OPS-MQ-010～012は選択実行3/3、既存005～009も5/5、collector負canary96/96 PASS。実認証Brokerの6 Address実効設定をSS321 literalと独立試験表で照合し、代表`nk.sync.request`の共通22 field＋容量4 fieldを各1項目変異、他5 Addressも容量4 fieldずつ誤数値へ変異して拒否を確認。欠落/Null/不正JSON・未知Address既定fallback拒否、借用session/一時Address残存0を確認。`MessageWriter`の汎用Exception静的指摘を修正し、encoder/cleanup例外の固定redacted PTを追加。直前Batch全380件/coverage100%は成功したがそのsourceのSpotBugs1で不認定、修正後SpotBugs0と選択8件はPASS。正式全reactorは未実施でありPG237の完了/工程進捗へ算入しない。正式run/対象commit/OS/JDK/command/coverage/証跡hashは実測後に追補する。
