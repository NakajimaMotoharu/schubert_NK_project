# 共用Web所有scope・実OS資源PT仕様（PG290、未認定）

Program NK-OPS-001、ServiceProcessResources.Inputs/execute/withDatabase、API/Web各ProcessMainと既存JdbcPool。RD SYS-002/004・DAT-001、UI212/243/253、SS311/331/342/343、SSC084、471 D01/02/05。実装/試験を並行、共有処理を複製せず既存API-RES-001～006を移動継承し、WEB-RES-001を追加する。

WEB-RES-001: 専用5材料、technical role `schubert_web_session`、pool最大2/min1、API ID拒否、入力null/材料closeを確認。期待roleはSS331 role表/provisioning SQL、poolはSS342を独立literalにする。Production role methodでexpected生成しない。元API6件の正常/途中故障/compound/negative/null/並行とshared71件を全実行。

| Test ID | 操作・独立期待値 |
|---|---|
| PT-OPS-NATIVE-001/002 | 隔離Ubuntu/systemdで専用UID、固定5 LoadCredentialを配布。Production共有scope/実API-Web factoryからSCRAM接続。role/database/recovery=false、API8/2・Web2/1、正常終了後pool/credential handle不可。秘密byteは証跡保存しない |
| PT-OPS-NATIVE-003 | VM内mq-api sourceを一時退避、Unit起動非成功・元材料復元 |
| PT-OPS-NATIVE-004 | VM内鍵を独立不正文法fixtureへ一時置換、起動非成功・復元 |
| PT-OPS-NATIVE-005 | db-apiを別のrandom MQ passwordへ置換、SCRAM拒否・復元 |
| PT-OPS-NATIVE-006 | 両serviceからroot private DB source読取が全拒否、復元後001/002成功 |
| PT-OPS-NATIVE-007/008 | 追加設計仮説のtest-only Unit。root shell fixtureが既存readonly lock FD3を明示継承し`!`/setprivで固定UID/GID/groupsへ降下。Javaでreadonly/CLOEXEC/zeroCaps/NoNewPrivileges、親root競合exit1、close後exit0。本番はraw path/shellを採用せず、未実装のsafe root/fresh gateを証明しない |

fixture事前条件/固定VM marker/秘密の生成・配布・復元/commandはtools/quality/vm/041～044と各fixture Unit、環境424。scriptは専用VM root以外拒否。DB dump/秘密key/password/cookie/token/raw journalをGitへ保存しない。終了/途中失敗後復元を必須、失敗/skipは不合格。native8件は主JUnit外の暫定必要条件、全PGPT認定や実NK CHRに加算しない。結果096とprovisional PG290 manifestにTest ID対応。
