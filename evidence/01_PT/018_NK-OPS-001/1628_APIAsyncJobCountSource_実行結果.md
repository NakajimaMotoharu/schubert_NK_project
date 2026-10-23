# 1628 API Async job count source 実行結果

source `faf7b0756d5a4fbb4098c17c2667ee7cf54b585c`、1627/PG-D540/group1864。PG7314-api-async-count-host-v1原SHA `30068e70b4bd18df636ea04cff0b18554671527fe018d0f37d0e54ff14d169c4` は真正verify0/16PT2suite/FES・rerun/flaky0/六format0。新ASYNCDB001～008と必要既ASYNCGAUGE8を当sourceで実行し、歴史Batch169/source743・Web23/source19cを現在のPASSへ加算していない。

PG7316-api-async-count-post-v1原SHA `c8547c6f9407202ff4f7a5a6beb4681ce9d1eacd019e9ec3863da7af9ad1d241`：全5Java/実4class＋metadata1・単一sessionCRC0、**L76/M15/C4/B41全miss0**。親Enforcer/lint/Werror/NullAway/Spotless・SpotBugs/Checkstyle0、PMD raw2/exit4・processing error0。raw2を削除/0へ改記せず、7324で両行の適用性を個別確認する。除外/抑制/規則変更0。

新8件は自己所有JDBC proxyのみ。独立固定SQL一SELECT・queryTimeout1秒、五rowの1..5/total15、emptyの全0・sparse7+3=10、null/無効txはprepare0、NULL state/COUNT・未知・負数・重複はchecked failure、最大long保持/総和overflow非成功、部分取得/null PS/RS・各getter/prepare/timeout/query/close故障を確認。RS→PSの全exit閉鎖、借用Connectionの変更/commit/rollback/close0、SQLException/Runtime/Errorの同一伝播/循環cause非走査・close suppressed順を確認。64並行でowner別counts、query一回、全資源close。DB/JDBC driver接続・業務worker・実期限測定0。

PMD二行は`AsyncJobCountRepository.read`のstatement（39行）/rows（43行）へのCloseResource。実codeはJava既存変数TWR `try (statement)` / `try (rows)`で資源を所有し、成功/全故障/部分取得/close故障を当ASYNCDBの独立fixtureで確認したためFALSE_POSITIVE。rawを保全し対象source SHA/行/変数/rule/methodを限定して分類、未分類・有効違反0とraw0を混同しない。仕様違反/実装障害は確認されず、新BUG起票0。旧1657/1658は限定閉鎖のまま。旧受入結果を分類根拠に転用0。

操作上の非成功：最初のSpotless引数`-pl schubert-nk-api`はroot reactor相対path不足でexit1、実compile/PT前。正しい`-pl src/schubert-nk-api`でformat0後にsourceを固定、失敗をPASSへ算入0/Production修正理由に転用0。全job元セッションとmanifestの真正終端を回収済み。元原本/DB/Backup/鍵/native/stash/Scenario3/Currentbaseline保全。

actual DB identity/role/tx真正性・query plan/driver取消/outer有限collector/Root/exporter/native/CHR/全体451は未受入HOLD。正式1964/53・歴史17/別source新7・原190新受入0/工数null/QA051final/PTALT0不変更。OS/JDK/tool/branch/source・command/日時/終了/XML/coverage/static/path/hashは元7314/7316へ一意対応。7316工具終了0はPMD raw2を消さず、分類前のquality全完了ではない。
