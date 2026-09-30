# Broker・Expiry親接続 単体テスト仕様書

PG394 class/method対応：BROKERLIVE=ArtemisUnitSnapshotTest/ChildBrokerTest（parser/自己actor）、BROKERSTART=MorningBrokerUnitCycleTest/BrokerJournalEvidenceTest（cycle/live/journal）、BROKERQUERY001～003=BrokerJournalQueryTest（executeStreaming normal/limit/timeout/exit/IO/unknown/close/interrupt）、EXPARENT=ExpiryOwnerTest/ArtemisParentDeadlineTest/MorningExpirySessionTest（owner/deadline・実PG fresh→sameRun SKIP）。nativeはMorningBrokerExecution/MorningExpiryExecution/CleanupExpiryExecution/各Mainから同Source execを採取する。管理transportのconnect timeoutも親残秒以下とし、default無期限は使わない。期待値はliteral JSON/Unit fields・手書きaudit SQL/固定2削除対象200byte等で独立算出。

BUG370/YKT291（修正前起票）：既存Expiry native入口/Source Unitの同Morning owner未継承と親期限不使用を是正する。正常単体データやRoot/current値だけでowner生存を代用しない。private credentialの欠落時はDB/MQ前に拒否し、元deadlineの負試験・実外部接続を別々に採取する。

NK-OPS-001/NK-BAT-001、RD SYS004/MQ/OPS009、UI251/253、SS321/341§9/342/343、SSC117/119/125・BUG369/YKT290。既存真正Cleanup後、同Morning所有からBroker→Expiryを接続する。正常parser/live値はsrc/deployment/systemd/artemis.serviceの実3directive＋下表の手書き18property、実DBは独立SQLの全列、MQは固定Queue/selectorと個別管理readbackをoracleにする。Production expected生成禁止。

| Test ID | 目的・入力/操作・fixture | 期待値/根拠 |
|---|---|---|
| BROKERLIVE001 | 固定18property・ARTEMIS実simple/on-failure/no、inactiveとactive/running | 正確なSource Unit契約をparse。稼働はJob空/MainPID>=2/Control0/start>0/end0/非nilInvocation一致・manager正常値だけ。inactiveはlive不可 |
| BROKERLIVE002 | Type/Restart/Remain矛盾、欠落/重複/非ASCII/数字境界/null/別Invocation・signal/timeout/旧終了 | reject/live false・redaction・owned close、古いworker activating/startをbroker稼働へ代用不可 |
| BROKERLIVE003 | 全5固定Targetとoneshot拒否回帰 | BACKUP/CLEANUP/INSPECTOR/EXPIRYのoneshot/no条件・fresh正常receipt不変更、generic daemon化なし |
| BROKERLIVE004 | PG392実systemd read-only projection・凍結JAR再現→修正同Source再試験 | 実Type=simple/on-failure/noを旧parserは拒否（BUG369）、修正後受理。start/secret/permitなし、外部live受入とは別 |
| BROKERSTART001 | Cleanup実0/10・同M/A/run/current INVALID/元期限から固定Brokerをstart | genuine fresh Invocation/実live・全Ops/recovery、Cleanup Requires再実行0、client0単独成功不可 |
| BROKERSTART002 | client非0/unknown/親期限/manager交換・反復restart | 実未成功/不確定を区別、未知marker/M/A保全、旧Invocationを今回成功にしない |
| BROKERSTART003 | actual Ops/private credential/全Topology/role/settings/acceptor/Queue/journal | fixed loopback/vendor/current BOM/証拠全一致、provider値/secretをGitへ残さない |
| BROKERSTART004 | 外部Morningから正常→再開、同Source byte/coverage | native source/class不一致0、未測定coverageを100%としない、正式run/S2全部と分離 |
| EXPARENT001 | Cleanupの実7step観測後だけ別一度の親advisory handoff | 同callback/DB/M/A、再取得後最新Expiry監査・実receipt/全終端独立一致。Cleanup未完/二回目/再入/別thread拒否 |
| EXPARENT002 | EXPIRY固定target/intent/private request/maintenance-owner | Morningだけstart、任意Unit不可、Root copy/真正同親boot/run/activation/Epoch・絶対deadlineがSQL/MQ前とmutation前後に一致 |
| EXPARENT003 | fresh真正Expiry0/10/30・DB監査全列・原本cutoff-7日selector | 実stage/commit/purge/readback。未実行/after不明を0/SUCCESS/FAILEDへ埋めない。DLQやOS journal削除0 |
| EXPARENT004 | 旧ExpirySUCCESS・今回実SKIP/別handle・fresh selected0 | 元監査不変・ALREADY_SUCCESSFUL/all0同start/end、元SUCCESS handleから監査、今回SKIPでは代用不可 |
| EXPARENT005 | 親死亡/期限/null/欠落/guard/commit/rollback/close/marker退役故障 | 不確定所有と保存真実を維持、同30分から新budgetを作らない。秘密scan0/traceとBUG/YKT全対象確認 |

実行環境は既存隔離PG/PT VM。旧active/成功Backup/DB25rowを保全し、同run resumeを用いる。JDK/toolchain/command/Source/branch/日時/終了code/coverage/障害再試験/入力・実値・期待値hashは294とsanitized manifestへ採取後記録する。必要dirだけ作成、raw credential/session/token/password/key/dumpは禁止。IT/ST本体は後続Linux serverで別工程。
