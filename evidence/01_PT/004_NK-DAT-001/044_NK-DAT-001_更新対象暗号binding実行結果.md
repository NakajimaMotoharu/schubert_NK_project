# NK-DAT-001 更新対象暗号binding 実行結果

2026-09-20 最新確定: dev-foundation/source e63b7d045fa7d64aa532fa95494020e3c4492514、正式PT-WEB-20260920-04（02:27:35～02:39:18 JST、Maven11:41/exit0）、全1471件（Protocol80/Storage82/API660/Web241/Batch367/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定path3method限定静的レビュー・coverage除外なし、CHR runnerのSpotBugs未設定。15collector/38scope同run/source/branch/hash・48負canary成功。DB29部品266＋Batch25部品281＋OPS16部品134＝70部分成果681 PT（全1471の内数）。9月19日再開比+56 PT/+5部分成果。PG186 private子directory8PT/SSC068限定完了、PG185全6768位置の独立4shard化も認定（新件数加算0）。BUG195/206・YKT154/162・SSC063の別境界分類、実archive/7世代/親全体/Question/Web/Logout/QA045/実NK互換gateは未完了。固定加重約4割（35～50%、456）、利用枠残72%で継続、元dev-web3file保全、PGPT・IT/ST未完了。以下は履歴。

## 0. 正式coverage・review

ResultBoundResponseSnapshotCodec: class1/method8/line53/branch20/instruction230、各missed0。35byte位置全変更、3route/ID・UUID両端、長さ/legacy、暗号/AAD/鍵/NULL、借用・100並行、同日時別targetを独立oracleで検証した。encrypt/decryptのprivate prefix・clear包絡を全finallyで消去するsource review済み。入力wire/借用codecを破棄せず、返却wireはcaller所有。JVM/JCA内部copyの物理消去までは保証しない。NPEをcatchして成功扱いする処理なし。

source固定後のsrc/pom/characterization/tools差分0、Current baseline843de94差分0、V001～015差分0、秘密pattern scan0hit（既知private-key/token形式の対象path scanであり全履歴entropy検査を意味しない）。BUG新規発生なし、SSC-052はwriter/consumer/参照接続まで対応中。IT/STおよび実NK Characterizationの合格ではない。

## 1. 個別探索（正式合格に算入しない）

2026-09-09 16:03:20 JST、JDK25.0.4+7/Maven3.9.12、dev-foundation/9705342f＋作業変更で実行。`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=ResultBoundResponseSnapshotCodecTest,FieldCodecTest,StorageAttributeGuardTest test`、exit0、新規8件成功。依存moduleの指定PTは新規8件に加算しない。ローカルraw診断logは`/tmp/pgpt-result-binding-explore-1.log`（Git対象外）。fixture値・暗号・tokenを証跡へ出力しない。

期待値は043の独立binary/JCE経路・literal hex・固定true/falseによる。全条件を含む正式clean verifyと全scope同一run/hash検査が終わるまで、この結果だけで合格・SSC-052完了としない。
