# F03 Bootstrap型付き13物理とPMD判定

NK-OPS-001、WBS-F03/2-2、SS311／332／341／342／351／352／354。Core `62b239d4dad561da007e15a290f8a271a165dda9`。現正規Bootstrapの201物理のうち187は旧と同byte、変更は14。旧compiler生成のServiceDatabaseAdmission補助クラス1が退役。当変更のうちnative連携のPublicAgentはJAR目録だけに現れ、今回の解析・初期化には含めていない。

- PG41314。型付きSpotBugsのClassStatsが対象13と一致。指摘・欠落・エラー0。変更11 MainのCheckstyle 0。PMD生51、処理エラー・抑制0。 [原型付き結果](evidence/PG41314-f03-bootstrap-changed-static-v1/manifest.json)
- PG41316。旧922件の個別分類から、method全体、対象箇所、列、元indexを一致させた2件を対応付けた。 [旧証拠との一致](evidence/PG41316-f03-bootstrap-pmd-site-reconcile-v1/manifest.json)
- PG41318。現行の所有・例外伝播・Throwableの参照比較・割込み状態の読取・固定Gsonの終端確認に基づき、45件を追加判断。残4はApiNonSecretConfigとWebNonSecretConfigのparseSource／validate各1。原51を保持し、抑制設定は変更していない。 [個別結果と残件](evidence/PG41318-f03-bootstrap-explicit-pmd-flows-v1/manifest.json)

証拠の継承、現在の差分解析、未実行を区別する。製品試験の再演0。全Bootstrap、F03の六製品、native及び451の正式受入は継続。
