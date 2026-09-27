# NK-OPS-001 外部main単体テスト仕様書（PG285/SSC083）

対象: API `ApiProcessMain.main/run/startNative/fatal`、Web `WebProcessMain.main/run/startNative/fatal`。RD SYS002/004、UI212/243/253、SS311/342/343、471 R1/D05。実業務assemblyは未結線で、成功起動R2/CHR R3は対象外。未達gateを飛ばして公開しない。

Java25.0.4/Maven wrapper/Linux上の独立固定oracleを用いる。fixture設定sourceは空common/serviceから既定値、環境は非秘密の固定位置2値のみ。実外部main試験は新しいJVMの環境をclearし、argv0件または固定override文字だけを渡す。credential/cookie/tokenは一切使わない。

| Test ID（API/WEB各4件） | 操作・入力 | 独立期待値 |
|---|---|---|
| PT-OPS-API-MAIN-001 / WEB-MAIN-001 | 設定検査→明示注入operation、native未結線、argv上書き・位置欠落 | 注入operationだけ1回、空argv検証済入力のみ内部0。nativeは50、argv/位置不備70。拒否時file IO0。内部0を実NK受入に算入しない |
| PT-OPS-API-MAIN-002 / WEB-MAIN-002 | source IO/assembly IO、IllegalArgument/IllegalState/Error、境界null | IO50、未知3型は同一identityの非成功伝播、nullは境界NPE。NPEを正常化しない。BUG262/YKT196再発防止 |
| PT-OPS-API-MAIN-003 / WEB-MAIN-003 | 秘密風診断を持つuncaught failure | stderr固定API/WEB process failed＋LF、元診断・cause/stackなし |
| PT-OPS-API-MAIN-004 / WEB-MAIN-004 | 実外部JVMで環境欠落/argv上書き | bounded終了15秒以内、OS exit70、stdout空、stderr固定process stopped＋LF。TERM cleanup後に子なし。HTTP/JMS/DB未開始 |

正常/異常/null/例外は上表。並行サービス寿命・再起動・実credential/DB/JMS/root/単一instanceは後続D01～05で別途必要、未検証として保持する。限定commandは`./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-<api|web> -Dtest=<Api|Web>ProcessMainTest,... --no-transfer-progress test jacoco:report`。JAVA_HOME固定25.0.4。

対象source/hash、日時、実際値、coverage、失敗履歴、未実行範囲は088へ記録する。全工程正式認定は別run/source/全scopeが必要。failed/flaky/skipped/not-runを合格に算入しない。
