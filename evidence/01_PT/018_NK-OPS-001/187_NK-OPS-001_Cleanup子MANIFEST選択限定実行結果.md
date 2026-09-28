# 187 NK-OPS-001 Cleanup子MANIFEST選択限定実行結果

2026-09-28 JST、PG331/SSC-104、branch `dev-foundation`、source `8023aa086cd5fe6e6f0bbfe6228ee562e0a80936`。RD OPS-009/BAK-001、UI251、SS341/343。PT-OPS-BMR017～024と既存BMR001～016。Linux host/JDK25.0.4/Maven3.9.12/Node24.19.0/JaCoCo0.8.15/SpotBugs4.10.4.0。

| 入力・独立期待値 | 実際・判定 |
|---|---|
| 186記載の独立固定MANIFEST SHA・正規dir名、欠落/変化/重複/故障/null/割込/並行。既存`readWithin`のDB/config完全handleを片方ずつ不一致にする | BMR017～024 PASS。選択Storage8＋Bootstrap8＋Batch24＝40件 F/E/S0、3module SpotBugs0。既存完全handle照合は弱体化なし。書込・削除0 |
| 変更`BackupManifestReader`/`NioIo`の4指標 | Reader line200/200・branch142/142・method24/24・class1/1、NioIo line4/4・method4/4・class1/1（branch対象なし）、missed0、除外0 |
| Production全体のsecurity回帰 | 同sourceで6module `clean test spotbugs:check` exit0、2,300PT/337suite F/E/S0、SpotBugs全0。内訳Protocol80/Storage149/Bootstrap175/API742/Web555/Batch599。JaCoCo `report` exit0 |
| Production全体coverage100% | Protocol/Storageは4指標missed0。Bootstrap branch37/line11/method4、API 1/19/3、Web 1/19/3、Batch 0/42/19は未網羅。全module class missed0 |

初回全6試行は2,300PT/static0だったが、既存`readWithin` configuration不一致のbranch1が未網羅でcoverage gate不合格。BMR017でDB/config片方ずつの独立ID不一致を追加した後、上記の最終全6回帰を取り直した。初回を合格数に混ぜない。承認済み仕様と異なる実装済処理の障害ではなく、追加PTで試験欠落を是正したためBUG起票対象なし。

最終証跡: `evidence/provisional/PG331-six-security-final/manifest.json` SHA256 `4986e603722966f7294aaafbb58af00186c22b0f733d098ee6928abf07e64de3`。実行日時・全command・exit・input/expected/actual・coverage・source2/log2 SHAはmanifest参照。Sanitized JUnit337 XML＋coverage/static各6＝349file、source2、Git外原始log2の計353 hash不一致0。JUnit properties/output/failure/skipped除去、保存証跡の秘密pattern scan0。

この限定結果は未信頼MANIFEST claim選択の証明のみ。4file実hash/所有、両DB SUCCESS、親連続M/A・子advisory、真正Cleanup Unit/DELETE/Artemisの受入ではない。正式認定source/run `858713c0bf310ae8bf62078b0a1cedbce4e968db`/`PT-WEB-20260925-24`、1964PT/53scope、暫定中心48.3%は据置。
