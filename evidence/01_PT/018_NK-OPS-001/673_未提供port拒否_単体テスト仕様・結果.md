# 未提供port拒否・所有不明保全 単体テスト仕様／結果

Program NK-OPS-001、RD BAK/BKO・UI251・SS341/343・SSC092/178/186、451。Production4d6、Java25.0.4/JUnit5.13.4-Platform1.13.4/Jacoco0.8.15、専用LAN host PT。native所有/実Unit資格/IT-STではない。

| Test ID / method | 独立fixture・操作・期待値 | 結果 |
|---|---|---|
| PT-BVERIFY-PORT-001 / bverifyPort001UnsupportedVerificationRejectsAndClosesWithoutSecretOrRegeneration | `BackupDatabaseWorker.Ports.verifyDump`を提供しないportで実execute。手書NKBACKUPVERIFY1/run日時/64a manifest/dump literal abc/3B/SHA ba7816bf…15ad、独立UNAVAILABLE契約。原dump abc不変、dump/pgpass/runtime/createPrivateFile呼出0、request zero、全FD閉鎖。 | 未実行 |
| PT-SERVICE-MARKER-PORT-001 / serviceMarkerPort001MissingRetainedProofNeverGrantsDaemonReadiness | 実BackupUnitStartClient(API)＋終了0 synthetic child、retained proof未提供。requireRetainedがliteral IO拒否、post-proof gate未呼出、retire0、stream全閉鎖。 | 未実行 |
| PT-SERVICE-MARKER-PORT-002 / serviceMarkerPort002MissingObservationClosePreservesUnknownAndCannotRetire | 同WEB、close observation未提供。初回literal IO拒否、再close及びretireも拒否、retire0、全stream閉鎖。 | 未実行 |

oracleはSSのfail-closed/所有不明保全及び固定入力・後条件。Production methodでexpectedを生成0、private Production reflection0。既資格1532のfixtureクラスを使用するが、合格証跡の流用は0。新JUnit launcherはexact3method、found/started/succeeded3、F/E/S/aborted/not-run0を要求。新only target/exec/XML、六MainJAR hash・全fixtureclass hashを実行前後照合。Main静的6module0はunchanged byte資格として保持し、新testのcompile-Werror・formatを別記する。全工程coverage合格には算入しない。

実行予定command: `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg1625_unsupported_ports_selected.py`。専用 `/runs/PG1625-selected-v1`・host `/PG379/pg1625-unsupported-ports-selected-v1`、元target更新0、VM/Root/Backup/start/stop0。新source確定後に対象commit/実日時/終了code/XML/hash/coverageを追記する。関連新BUG無し（TDD未実行）。群0464 .25/.75/2pp着手前固定、実N/T/個別費null、正式認定不変更。
