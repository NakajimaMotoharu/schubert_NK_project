# FailedBackupPair境界・null独立実DB試験

2026-10-15JST、Program NK-BAT-001/BackupFailureSnapshot.constructor/verifyLatest/verifyRow、PT-CFDB-2916-001..003、DAT009/OPS009/UI251/SS331/341/343/355・451/487、主担当WBS-P017-06。Production a9、Test source4a6ed8bbce8a9b2a71183c476ca7627f2b89ee0f、Main byte不変更。

fixture=隔離PostgreSQL18の固定run/cutoff、BACKUP_DB7/BACKUP_CONFIG8・attempt4・日時2026-09-13T02:00:00～03Z・FAILED/target1/success0/failure1/byte0/COMMAND_FAILURE/batch command failedのliteral二行。期待値はSQL literalと固定型値から独立に作成しProduction自身から生成0。

| Test ID / method | 操作・異常入力 | 独立期待値 |
|---|---|---|
| 001 / cfdb2916001FirstAndFinalIdentityDriftRejectWithoutMutation | 実JDBCの最初/最後のidentity_consistentのみfalseへprojection | fixed IOException、cause null、前後二段の必要reread、実connectionをborrowedのまま保持、全14列二行不変 |
| 002 / cfdb2916002EveryNullColumnAndMissingResourceIsBounded | 全14typed column個別null、PreparedStatement/ResultSet個別null（実resourceを先にcloseして返す） | NPEでなくfixed IOException、cause/suppressedなし、対象column注入一回・資源null時はcolumn注入0、実原14列不変 |
| 003 / cfdb2916003PairRejectsEqualIdAndForeignRunAtConstructor | 同id又は同cutoffだが別runの二handle | constructor IllegalArgumentException/failed backup pair invalid、authority/SQL操作なし |

既3methods（正常read/DBlock必須/各terminal drift/constructor null）と合わせ全6実行。`python3 -B tools/quality/pg2916_failed_pair_boundary_selected.py`、PYTHONPATH838同値、session42985 actual0/F-E-S-aborted-notRun0/Xlint-Werror0。JAVA25.0.4/aru専用host DB fixture、原host fixture/oldXML/library/source allhash不変。現guest/原DBBackup/Root/業務操作0。

WorkPG379 `pg2916-failed-pair-boundary-selected-v1/manifest.safe.json`、payload7d254009934a3b8ab6a190d8a74836633e004ac69f38c3ee58209a47c9557578、XML e83f7b461b9b9c9e57bdd57eec9e9b7e2a8ea5592444a31d255a2fa16b353743、LANmanifest4fa8b7560cb112c78a0ac0280c5d975be5c9b760a703104c36b8384952c955c7。実時刻/OS/tool/command/input/output/hashはmanifest、raw SQL結果・credential非Git。関連BUG1257/1258工具側は各915/916へ分離。

当source限定成功でcoverage claimfalse/正式1964-53/leafdelta0/effortnull。group全体2918はformatで失敗してbatch未実行、成果は流用合格0。Maven applyでも当Test byte不変更を実照合し、new2930全体へ同入力として統合。四counter測定は全体後に実証し、未実行を合格に算入しない。

## SSC-461 SQL診断接続の独立単体試験

PT-BAT-SSC461-BF001～004、PG43828、BUG-3233／YKT-2680、WBS-F02-b-a／P017-06。公開verifyLatestに固定run、同一の開始・終了時刻と二段階のJDK Connection代理を供給する。最初の独立identityはhistory=true、inbox/log=false、consistent=true。一件終端後に所定14列照会のprepare／bindへ進む。実行は既接続を借用し、実DB、Backupとnativeを使わない。

|ID|入力と独立期待|
|---|---|
|BF001|二番目の文executeで通常SQLException。固定IOExceptionの文言と空cause・空suppressedを照合。identity行→identity文→backup文のclose各一回、Connection操作は固定read属性とprepareのみ。|
|BF002|SQL次辺のcauseにError。同じErrorを伝播し、資源closeの期待はBF001と同じ。|
|BF003|普通causeとSQL次辺双方に別Error。普通causeにある先行Errorを同じインスタンスで伝播。閉鎖順は同じ。|
|BF004|次辺・抑制辺の重複と有限循環にErrorなし。固定IOExceptionと同一資源閉鎖、有限終了。|

初回の旧Mainと移管後の同fixtureを別runで記録する。コードは既SQL・留保済み実DB試験・公開ABIを保持する。局所coverageの不足を明記し、全F02の受入に加えない。
