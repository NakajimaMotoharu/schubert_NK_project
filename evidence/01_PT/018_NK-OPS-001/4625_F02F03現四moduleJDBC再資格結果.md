# F02・F03 変更後の4製品モジュール検証

製品Core `13f2fd9bc1345a4dceb360849add2c329bc9b90f`。JDK25.0.4／Maven3.9.12のoffline reactor、8 POM／482 Mainを固定して終了0。4 Main変更、生成物6差分はPG38864／38899／38948の通常PTに使った測定byteと同一。追加・除去の物理classは0。独立全class SHAと両変更moduleのSpotBugs847件を再検査し、指摘・欠落・解析エラー各0。Protocol／Storageの255 Classと解析条件は前回一致。Checkstyleは変更4が指摘0。過去の未変更478と適用性を別証跡で保持。PMD 48生の各該当sourceと個別判定を対応、当4の適用0。

ArchUnitで物理1,102／参照49,822／アクセス36,712を確認。規則違反は引き続きStorageIoException→java.sql.SQLExceptionの一件（BUG-3233）。静的器終了1、禁制module間辺と不明内部参照は0。上位26/104、残78、Storage3直利用と旧入口は継続。現sourceの六module・業務SYS実験、全F02/F03／451、正式受入は未成立。

実行・環境・source／コマンド／元ログと独立証拠は[公開manifest](evidence/PG38959-f02-current-four-physical-independent-v1/manifest.json) SHA256 `6aae48af70d2fb968e922e9b73881dc1d69ba6419ccf7189fdf65a467776a9d3`。製品PTの確認目的の再実行なし。
