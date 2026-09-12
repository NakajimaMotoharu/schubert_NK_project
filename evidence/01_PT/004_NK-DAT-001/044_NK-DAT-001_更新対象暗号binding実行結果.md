# NK-DAT-001 更新対象暗号binding 実行結果

2026-09-13 最新確定: dev-foundation/source 956a2f47c04730c940dc15b0817721b1c7848b49、正式PT-WEB-20260913-04（03:33:29～03:48:59 JST）、全1247件（Protocol80/Storage58/API644/Web241/Batch183/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/etc・/run・/varの3 method限定静的レビューを維持しcoverage除外なし、CHR runnerのSpotBugsは未設定。13collector/36scopeの同run/source/branch/hashと24負canary成功。DB27部品250＋batch9部品113＋OPS11部品94＝47部分成果457 PT（全1247の内数）。PG161の限定400日GC/回復plan・marker24 PT、独立6768 IO全位置・crash/並行/DB参照再検査を認定、BUG171～174/YKT132～135を完了。R001は原本codec/永続IO/lifecycle/DB参照/GCが確定したが親結線未完了、R002環境fileは確定。実子制御/backup artifact・全cleanup caller・通常Question writer/replay・Logout RERUN001・QA045は残る。PG162の親summary/attempt照合24件は仕様のみで未算入。固定加重約4割（35～50%、456）を維持、残件は460。実NK CHR/IT/ST完了とはしない。利用枠残57%でPG/PT継続中、元dev-web3file保全。以下は履歴。

## 0. 正式coverage・review

ResultBoundResponseSnapshotCodec: class1/method8/line53/branch20/instruction230、各missed0。35byte位置全変更、3route/ID・UUID両端、長さ/legacy、暗号/AAD/鍵/NULL、借用・100並行、同日時別targetを独立oracleで検証した。encrypt/decryptのprivate prefix・clear包絡を全finallyで消去するsource review済み。入力wire/借用codecを破棄せず、返却wireはcaller所有。JVM/JCA内部copyの物理消去までは保証しない。NPEをcatchして成功扱いする処理なし。

source固定後のsrc/pom/characterization/tools差分0、Current baseline843de94差分0、V001～015差分0、秘密pattern scan0hit（既知private-key/token形式の対象path scanであり全履歴entropy検査を意味しない）。BUG新規発生なし、SSC-052はwriter/consumer/参照接続まで対応中。IT/STおよび実NK Characterizationの合格ではない。

## 1. 個別探索（正式合格に算入しない）

2026-09-09 16:03:20 JST、JDK25.0.4+7/Maven3.9.12、dev-foundation/9705342f＋作業変更で実行。`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=ResultBoundResponseSnapshotCodecTest,FieldCodecTest,StorageAttributeGuardTest test`、exit0、新規8件成功。依存moduleの指定PTは新規8件に加算しない。ローカルraw診断logは`/tmp/pgpt-result-binding-explore-1.log`（Git対象外）。fixture値・暗号・tokenを証跡へ出力しない。

期待値は043の独立binary/JCE経路・literal hex・固定true/falseによる。全条件を含む正式clean verifyと全scope同一run/hash検査が終わるまで、この結果だけで合格・SSC-052完了としない。
