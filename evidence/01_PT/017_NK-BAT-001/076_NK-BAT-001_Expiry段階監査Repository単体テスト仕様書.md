# NK-BAT-001 Expiry段階監査Repository PT仕様

PG249、`ExpiryAuditRepository`（stage/read/finish）、PT-BAT-284～287。RD OPS-009/MQ-009/DAT-009、UI251 §8/11、SS331 §8.2/8.3・341 §9、SSC-077/078、BUG-237/238、YKT-188/189。隔離PostgreSQL18へV001～022をFlyway適用し、`schubert_batch`借用READ_COMMITTED transactionと固定run/完全`BatchStepAttempt`を使用する。RepositoryはConnectionを生成・commit/rollback/close・設定変更せず、親のOS lock/子停止/実Broker削除も代行しない。

| Test ID | 目的・事前条件・fixture・入力/操作 | 独立した期待値・根拠 |
|---|---|---|
| PT-BAT-284 | CLEAN_EXPIRY RUNNINGを`BatchRunRepository.begin`で作り、pre-purge観測before3/target2/推定byte200をstageし、commit前後を別DB接続から読む。exact cutoffは固定runから7日差 | V022のexpiry_cutoff_atはµs exact、before3、after NULL、target2、success0、failure0、byte200。未commitは他接続から不可、commit後のみ可。観測/値を推測しない |
| PT-BAT-285 | stage後、実after1/削除2のSUCCESSをterminal同transactionへ保存、同値再試行と異値replayを比較 | `before-after=success=target=2`、failure0、ended固定、同値冪等、異値拒否。独立SQL SELECTを期待としProduction算出methodを使わない |
| PT-BAT-286 | stage rollback、非Expiry/skipped/別handle、cutoff・before/target/byte異値、未stageの終端、after不明FAILEDとafter既知WARNINGを検査 | rollback後のDBは3列NULL/4count0。異handle/異stageは0更新・他row不変。未知afterはNULL/成功0、非成功診断固定。既知afterは実値だけ保存。V022 CHECKとSS331 §8.3 |
| PT-BAT-287 | null/負値/target>before/time逆転、未観測/段階/終端Snapshot全fieldの独立負変異、接続guard・SQL/close故障、再読と資源所有。BUG-240のWARNING既知after差分1/成功0を修正前RED→修正後拒否 | 不正値は副作用0で固定契約例外。after既知の全statusで`before−after=success`、未知afterでは成功0。固定投影22・stage差異8・terminal差異11を拒否。DB故障/接続null/ResultSet null/close競合は原因・suppressed・SQL原文を外へ出さない。接続を閉じず、親がcommit/rollbackを決定する。run原本・完全handleで再読し、未知値を0に補完しない |

実装とtestは同小単位で進める。選択試験は`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl :schubert-nk-batch -Dtest=ExpiryAuditRepositoryTest test jacoco:report`。正式run/target commit/branch/日時・OS/JDK/PG/Flyway/pgJDBC、Test ID別input/期待/実際・coverage/static、関連BUG/SSC、evidence path/hashは対の077とmanifestに固定する。Failed/flaky/skipped/not-runは合格算入しない。親の二transaction commitと実Artemis、同run不確定commitは別必須受入。
