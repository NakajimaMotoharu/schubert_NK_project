# NK-DAT-001 更新対象暗号binding 実行結果

2026-09-09 最新確定: dev-foundation/sourcef25955f2、正式PT-WEB-20260909-46（21:07:26～21:14:32 JST）、全1103件（Protocol80/Storage50/API634/Web241/Batch57/CHR41）PASS、failed/error/skipped0。6 Java moduleのline/method/class/branch100%、Production5 moduleのSpotBugs未解決0/NullAway・Enforcer・Spotless PASS。固定/run移植性指摘1件のmethod/ID限定レビューを明示（BUG142/005）、coverage除外なし、CHR runnerのSpotBugsは未設定。12collector・35証跡scopeの同run/source/branch/hash/参照、017の1件・019の15件負canary成功。DB26部品240 PT＋batch2部品29 PT＋OPS6部品44 PT＝34部分成果313件確定。PG-D-149/run環境fileのcanonical生成・全byte照合4 PTを追加、新規BUGなし。BUG143～145/YKT113は正式45で完了し46で回帰。親root実配置/停止実行/実backup/DB引渡し/設定publish/固定run永続化SSC055・全cleanup監査・通常Question writer/replay・Logout RERUN-001は残る。QA045はLogin title差分の未回答でLogoutとは別。BUG-014/UIC-006/SSC-049/052継続、加重見積約4割（35～50%、456）を維持。週間残10%、新しい大規模作業は開始せず、既着手PG-D-150/DB引渡し8 PTだけを続けて中断準備。150は仕様のみで未合格。元dev-web Scenario3file保全・不算入、CHR41はrunner PTで実NK互換gateではない。以下は履歴。

## 0. 正式coverage・review

ResultBoundResponseSnapshotCodec: class1/method8/line53/branch20/instruction230、各missed0。35byte位置全変更、3route/ID・UUID両端、長さ/legacy、暗号/AAD/鍵/NULL、借用・100並行、同日時別targetを独立oracleで検証した。encrypt/decryptのprivate prefix・clear包絡を全finallyで消去するsource review済み。入力wire/借用codecを破棄せず、返却wireはcaller所有。JVM/JCA内部copyの物理消去までは保証しない。NPEをcatchして成功扱いする処理なし。

source固定後のsrc/pom/characterization/tools差分0、Current baseline843de94差分0、V001～015差分0、秘密pattern scan0hit（既知private-key/token形式の対象path scanであり全履歴entropy検査を意味しない）。BUG新規発生なし、SSC-052はwriter/consumer/参照接続まで対応中。IT/STおよび実NK Characterizationの合格ではない。

## 1. 個別探索（正式合格に算入しない）

2026-09-09 16:03:20 JST、JDK25.0.4+7/Maven3.9.12、dev-foundation/9705342f＋作業変更で実行。`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=ResultBoundResponseSnapshotCodecTest,FieldCodecTest,StorageAttributeGuardTest test`、exit0、新規8件成功。依存moduleの指定PTは新規8件に加算しない。ローカルraw診断logは`/tmp/pgpt-result-binding-explore-1.log`（Git対象外）。fixture値・暗号・tokenを証跡へ出力しない。

期待値は043の独立binary/JCE経路・literal hex・固定true/falseによる。全条件を含む正式clean verifyと全scope同一run/hash検査が終わるまで、この結果だけで合格・SSC-052完了としない。
