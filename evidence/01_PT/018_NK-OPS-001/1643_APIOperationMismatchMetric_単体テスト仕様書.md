# 1643 API operation mismatch metric 単体テスト仕様書

NK-OPS-001/P01809/C07共有費0、RD171/UI252/SS314323324351/PG-D544。OperationMismatchMetricRecorder.constructor/operation/record/detail、Operation enum。OPMIS001～008、`nk_operation_token_mismatch_total{operation}`へ供給済み不一致一回を記録する内部部品。operation labelは更新purpose八layout UCRREQ01/USTREQ01/URLREQ01/UPWREQ01/ULKREQ01/QSBREQ01/NTCREQ01/QDLREQ01だけ（SS323更新catalogと既SessionOperationToken.PURPOSES）。raw token/actor/payload/HMAC/keyは受け取らず、実認証/不一致判定・鍵利用・業務hook/DB/Root操作なし。

| Test ID | fixture/操作 | 独立期待値 |
|---|---|---|
| OPMIS001 | DEBUG/実owned SDK・八Operation | counter名一/key operationだけ/全8series・初期0、canonical literal集合一致 |
| OPMIS002 | 全op各1＋先頭もう1 | UCR2/他7各1、increment一観測一回/label成長0 |
| OPMIS003 | STANDARD/全op/null | counter登録/保持/増分0でもnull先行拒否 |
| OPMIS004 | null registry/mode/op・未知/alias文字列 | side-effect前拒否/固定CONFIG_INVALID、秘密canary文字列のecho/label化0 |
| OPMIS005 | 二番目counter登録でRuntime/Error | 同一故障/attempt2/再試行0/partial registryはcaller所有 |
| OPMIS006 | increment前/後のprovider故障 | 同一故障と一attempt、済増分の補償/自動再試行0・元例外format0 |
| OPMIS007 | 64並行/八op均等 | 各8/全64増分・8series固定、別業務処理は発行しない |
| OPMIS008 | 別owner/反復1000観測 | owner値非共有/8series上限、外部registry close0 |

expectedはSS/既public catalogから独立した固定八literalと整数/SDK Meter.Type.COUNTER/key集合、productionからexpected生成0。counter再起動時の0は新registry内の値で永続業務回数を証明しない。STD最小healthや警報を停止せず詳細だけ0。HMAC/key/token fixtureは作らずOperation enumのみ。

新8＋必要既API48=56PT7suite/全15Java/実12＋metadata1・全1735physical/77sourceは予定未実測。元PG7376/7378以降のordinary verify/XML/真終了/FES0/単一sessionCRC/四counter100/NullAway/SB/PMD-CS/全Jar/traceへsource/branch/OS/JDK/tool・command/time/exit/coverage/BUG-SSC/path/hashを保存。Hikari/SDK等既六aux同byte・harness不変更、旧48成功や歴史Batch/Webへ当source成功を合算0。

actual mismatch検知/業務hook/auth/鍵/DB/VM/Root/exporter/native/CHR/全体451は未受入HOLD。正式1964/53・歴史17/別source新7・原190新受入0/工数null/QA051final/PTALT0不変更、障害は修正前915/916。元見積/群1-3-6pp上限10/共有開始20・専有N-Tnull/通常区切り停止0。

BUG-3881／YKT-2997。OPMIS007の元の固定期待、8worker、64件、10秒、registry個別所有を保持。期限付き終了を共用し、二次失敗は一次を覆わない。現版の真正5件は[PG45494](evidence/PG45494-current-five-api-metric-fixture-owners/manifest.json)。実環境と正規全451は別。
