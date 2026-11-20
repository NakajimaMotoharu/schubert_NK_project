# F03 Storage現静的の全物理対応

NK-PRO-003／NK-OPS-001、WBS-F03/2-2、SS311／333／352／354、SSC-461。現製品Core `62b239d4dad561da007e15a290f8a271a165dda9`。Storageは25 Main、現正規JARに79物理。従来80物理から、ServiceCredentialIdの分岐を閉じたMapへ変更した際のcompiler生成クラス1物理がなくなった。対象名と生成原因を新旧のclass一覧とsourceで確認した。検査除外は行っていない。

- 22 Main・74物理は旧NullAway／型付き元証跡と完全一致。元PMD 18件はすべて同一ResourceScope sourceの仕様適用性記録を保持。 [旧証票](evidence/PG36824-storage-main-independent-v1/manifest.json)
- 当3変更Main・5物理は同じStorage JARでCheckstyle／型付きPMD／SpotBugsの指摘・処理エラー・欠落0。SpotBugs XMLのClassStatsも対象5物理と一致。 [局所静的](evidence/PG41310-f03-storage-exact-static-v1/manifest.json)
- 当JARの通常compile終端、StorageのMain・pom・Root設定同一、現79物理のSHA、静的の入力と結果を独立照合した。製品試験再実行0。 [独立確認](evidence/PG41312-f03-storage-static-independent-v1/manifest.json)

静的証拠の継承と現在の計測を区別する。全Storageの新規runtime coverage、実native／DB、F03六モジュールと451・正式受入は引き続き必要。入力、出力、終了値、使用toolとSHAはmanifestとinput/5657・5658を参照。
