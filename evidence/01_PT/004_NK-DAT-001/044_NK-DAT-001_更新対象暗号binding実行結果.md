# NK-DAT-001 更新対象暗号binding 実行結果

2026-09-20 最新確定: 正式PT-WEB-20260920-12/source0d0abbb80e91d016f961042e9b9e09cb07b5f7a9、05:24:36～05:36:26 JST/Maven11:48/exit0、全1544PT（Protocol80/Storage82/API689/Web285/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。18collector/41scope整合・60負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web4/44＝78部分成果754PT（全1544の内数）、今回再開比+129PT/+13部分成果。PG194階層3画面16PTを限定認定、BUG213～216/YKT169～172/SSC071限定範囲完了。PG195本文モデルは仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web/Logout/QA045/実NKgateは未完了。固定加重38.25～49.75%（中心44%、約38～50%）、3画面接続で前回から+1 point。残量49%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

## 0. 正式coverage・review

ResultBoundResponseSnapshotCodec: class1/method8/line53/branch20/instruction230、各missed0。35byte位置全変更、3route/ID・UUID両端、長さ/legacy、暗号/AAD/鍵/NULL、借用・100並行、同日時別targetを独立oracleで検証した。encrypt/decryptのprivate prefix・clear包絡を全finallyで消去するsource review済み。入力wire/借用codecを破棄せず、返却wireはcaller所有。JVM/JCA内部copyの物理消去までは保証しない。NPEをcatchして成功扱いする処理なし。

source固定後のsrc/pom/characterization/tools差分0、Current baseline843de94差分0、V001～015差分0、秘密pattern scan0hit（既知private-key/token形式の対象path scanであり全履歴entropy検査を意味しない）。BUG新規発生なし、SSC-052はwriter/consumer/参照接続まで対応中。IT/STおよび実NK Characterizationの合格ではない。

## 1. 個別探索（正式合格に算入しない）

2026-09-09 16:03:20 JST、JDK25.0.4+7/Maven3.9.12、dev-foundation/9705342f＋作業変更で実行。`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=ResultBoundResponseSnapshotCodecTest,FieldCodecTest,StorageAttributeGuardTest test`、exit0、新規8件成功。依存moduleの指定PTは新規8件に加算しない。ローカルraw診断logは`/tmp/pgpt-result-binding-explore-1.log`（Git対象外）。fixture値・暗号・tokenを証跡へ出力しない。

期待値は043の独立binary/JCE経路・literal hex・固定true/falseによる。全条件を含む正式clean verifyと全scope同一run/hash検査が終わるまで、この結果だけで合格・SSC-052完了としない。
