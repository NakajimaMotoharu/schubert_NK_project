# NK-MED-001 Media三namespaceの静的検査と通常試験結果

PG42916、2026-11-23 JST、dev-foundation、Core `e8368d22c4da2ec841f008df793594d3be9066af`、試験 `57505261c834422592a1e11d18b94732baac30d2`。通常25件（製品24とfixture1）全成功、失敗・エラー・skip・選択漏れ0。13製品物理とProtocol補助5を現型品質のbyteと確認した。旧3反射の再演0。PT-MED-STATIC001～003の静的証明はPG42914で当同一物理に照合。

現単一exec無フィルターは行129/135、method36/39、class9/9、branch74/74、命令701/722。欠落はHttpByteRangeParser／ContentDispositionFactory／MediaBodyStreamerのprivate constructor各2行・1 method。除外、元coverageの加算なし。4つのコードを持たない型も個別物理として証跡に保持。YKT-2863とF03全製品、実HTTP／FileStore、正式受入を継続。

公開 `evidence/01_PT/018_NK-OPS-001/evidence/PG42916-web-media-without-private-reflection-v1/manifest.json` SHA-256 `5746dcf5445afa94517242266e78455c9e388c94074559d98b08307efdf7b1a3`。
