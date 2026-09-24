# NK-DAT-001 Expiry batch監査DDL 実行結果

PG245/SSC-077/BUG-237/YKT-188、PT-DB-016/017。正式`PT-WEB-20260924-40`/source`c1512bf61d288dd8a08a7bd5cc2b47bdb04bd197`で**V021監査DDLの限定PTを認定**。親transaction・Expiry清掃全体/PGPTは未完了。

検証対象は対の064仕様書に固定した独立期待値。PostgreSQL18.6隔離clusterを用いる。未commit候補の選択実行は2026-09-24 13:32:23 JST終了、`/tmp/PG245-selected.log`、exit0、API33件（DB17/StepCleanup8/InspectionParent8）、failure/error/skipped0。V021適用21件・旧SUCCESS安全停止20件・他step監査NULL・正負CHECK/権限を実PGで確認した。選択探索結果なので正式認定へ流用しない。

初回正式`PT-WEB-20260924-38`/source`fc4c0300`は2026-09-24 13:38:59 JST、exit1で不認定。APIの旧回帰で5件（CHECK件数154→155の旧oracle4件、監査3列なし`CLEAN_EXPIRY SUCCESS` fixture1件）が失敗し、Web/Batch未実行。`/tmp/PT-WEB-20260924-38.log`とAPI Surefire XMLで原因確認。SSC-077/BUG-237/YKT-188の横展開として、旧migrationや承認済み監査条件を変えず、4独立catalog期待値と1合成fixtureを更新して再試験する。run38を合格/coverage/正式証跡へ算入しない。

修正後の選択6class/65件は2026-09-24 13:40:40 JST、`/tmp/PG245-regression.log`、exit0、failure/error/skipped0。新たに`037_collect_expiry_audit_database.py`へPT-DB-016/017と独立oracleを固定し、019の99負canaryが成功した。探索結果を正式認定へ流用しない。

次の正式`PT-WEB-20260924-39`/source`8480edc7`も2026-09-24 13:56:39 JST、exit1で不認定。API725/Web513/Batch395の試験が走ったが、Batchの旧migration数20期待値が`BackupStepRepositoryTest.databaseGuardsAndLocks`と`BatchRunRepositoryTest.independentSqlInventoryAndGrants`の2件で失敗した。API/Webでの失敗は0、Batchは2 failure。`/tmp/PT-WEB-20260924-39.log`/Surefire XMLで確認。YKT-188の全module inventory検索へ追加し、実適用21件の独立期待値へ修正・選択/全体再試験する。run39を合格/coverage/正式証跡へ算入しない。

Batch2classの修正後選択24/24件は2026-09-24 13:57:59 JST、`/tmp/PG245-batch-regression.log`、exit0、failure/error/skipped0。正式run40: 2026-09-24 13:58:50～14:11:05 JST、`dev-foundation`、Ubuntu/Linux7.0.0/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/Flyway13.4.0/pgJDBC42.7.13/Artemis2.56.0、`sh tools/quality/030_run_pgpt_verify.sh PT-WEB-20260924-40`（内部offline `clean verify`）、exit0。全1836PT（CHR41/Protocol80/Storage82/API725/Web513/Batch395）、failure/error/skipped0。Java6 moduleのinstruction/line/method/class/branch missed0、Production SpotBugs0、019負canary99/99、018の49scope収集・`--validate-only`再照合PASS。PT-DB-016の実catalogは21 migration/3列型/正常・23514・権限、PT-DB-017は旧成功行でV021非成功・旧history20・新列0を、064の独立SQL期待値と一致させた。

証跡: `evidence/expiry-audit/input/independent-oracle.txt`、`output/results.xml`、`manifest.json`/`checksums.sha256`。専用manifest SHA-256 `f5240671e3a66bfcee1ff5212d8117c1c3b30639ada5b0cbaeb310ef672da4d1`、root `evidence/01_PT/008_NK-SCN-001/evidence/manifest.json` SHA-256 `a6fbe76a0ea1f048237e189a5520cdaf478fb14d901c1053e832ba2b2d2033b3`。環境・source・command/終了code・input/expected/actual・coverage・静的結果と全file SHAは専用manifestへ格納。run38/39の失敗は正式合格数に含めない。PG244正式`PT-WEB-20260924-37`は本V021を含まない。

障害票BUG-237と横展開YKT-188は、親による同transaction監査値保存・同run再実行・commit不明・rollbackのPTが残るため対応中。PG/PT全体は未完了。
