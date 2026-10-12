# 未提供port拒否・所有不明保全 単体テスト仕様／結果

## 次の独立3PT（PG1626、未実行）

| Test ID / method | 独立期待値・事前条件・後条件 |
|---|---|
| PT-ORIGINAL-PORT-001 / originalPort001DefaultResumeVerificationNeverProvesOriginalOrRetainedOwnership | SS343/SSC178、手書run/cutoff/activation、alive=trueのscoped OriginalProof。Files.verifyを未提供とし、verify/retainedともliteral IOException、二回のpre gateだけ、post gate0/resume発行0。alive=falseではIO前拒否。native owner受入ではない。 |
| PT-ROOT-IDENTITY-PORT-001 / rootIdentityPort001AbsentUidProviderRejectsOtherwiseValidSamePeerService | SS343/SSC164、独立proc/Unit literal fixtureのMorning42/targetAPI200。Io.serviceRootUid未提供。captureServiceRootがsanitized IO、cause/suppressed0、target Unit初回読1/成功二読目0、Morning不変。 |
| PT-TRANSFER-FAILURE-001 / transferFailure001OneUnlinkFailureRetainsBytesCountsWarningAndContinuesOtherFile | SS341/343/SSC118、実Linux retained FD/独立070? 実dir0750/file0640、cutoff09-30以前二file abc3B/二byte。一fileだけunlink port IO拒否。他fileは実削除。target2/success1/failure1/retained0/byte2、WARNING/IO_FAILURE、失敗原byte不変/非空dateとroot保持/全実FD一回閉鎖。 |

実dirは0750（表中070?は使用しない）、testfixtureは専用TempDirであり、業務原本を操作しない。request/原本/Backup/実VM変異0。actual selected6＝新3＋直前3の影響resource回帰、exactmethodとfound/started/succeeded6/FES-aborted-notrun0が条件。新target `/runs/PG1626-selected-v1`、`pg1626_unsupported_ports_selected.py`。Main変更0、全6Maven再回帰trigger無し、群0466 .25/.75/2pp凍結。対象commit/実結果は実行後追記。

## PG1625実結果（2026-10-12、限定3PT成功）

test/tool source ddacda3e296723cd18adf87818cf7321732699f5、Production4d6不変更。上記実行command終了0、JUnit actual found/started/succeeded3、F/E/S/aborted/not-run0、javac-Xlint/Werror0、全fixtureclass byte前後同値、六MainJAR資格/classCRC0、VM変異0。三Test IDとも成功。手書abc/SHA/固定run/IO literal・resource後条件を検査、Productionからexpected生成0。新target/XML/execと16資格native及びhost1532の同Main coverage残L797/M154/C6/B707。直前800/157/8/707との差3/3/2/0は技術測定であり工数/全leafへ加点0。

host safe manifest `/home/mini/codex/project1/work/pgpt-runs/PG379/pg1625-unsupported-ports-selected-v1/manifest.safe.json`、LAN `/home/mini/schubert-nk-pgpt/runs/PG1625-selected-v1/manifest.safe.json` SHA4aa80403b8f6599d9f3350fb5be6842c82af31c634166fa80d8ea9c0538e4ffd、実generated script521f34c1ddc71bb3b8908c6109de3934f649ae24e699c5ac62b5e30a9ff17a2d。manifestにactual command/tool/source/file/fixture/lib/JAR/XML/exec/hash/日時/coverageを保存。Main静的6module0は資格済みunchanged byte、test追加のみなので全6Maven再回帰0。正式1964PT/53scope/global451/Java四100/CHR/traceは未受入として維持。新障害0。

Program NK-OPS-001、RD BAK/BKO・UI251・SS341/343・SSC092/178/186、451。Production4d6、Java25.0.4/JUnit5.13.4-Platform1.13.4/Jacoco0.8.15、専用LAN host PT。native所有/実Unit資格/IT-STではない。

| Test ID / method | 独立fixture・操作・期待値 | 結果 |
|---|---|---|
| PT-BVERIFY-PORT-001 / bverifyPort001UnsupportedVerificationRejectsAndClosesWithoutSecretOrRegeneration | `BackupDatabaseWorker.Ports.verifyDump`を提供しないportで実execute。手書NKBACKUPVERIFY1/run日時/64a manifest/dump literal abc/3B/SHA ba7816bf…15ad、独立UNAVAILABLE契約。原dump abc不変、dump/pgpass/runtime/createPrivateFile呼出0、request zero、全FD閉鎖。 | 未実行 |
| PT-SERVICE-MARKER-PORT-001 / serviceMarkerPort001MissingRetainedProofNeverGrantsDaemonReadiness | 実BackupUnitStartClient(API)＋終了0 synthetic child、retained proof未提供。requireRetainedがliteral IO拒否、post-proof gate未呼出、retire0、stream全閉鎖。 | 未実行 |
| PT-SERVICE-MARKER-PORT-002 / serviceMarkerPort002MissingObservationClosePreservesUnknownAndCannotRetire | 同WEB、close observation未提供。初回literal IO拒否、再close及びretireも拒否、retire0、全stream閉鎖。 | 未実行 |

oracleはSSのfail-closed/所有不明保全及び固定入力・後条件。Production methodでexpectedを生成0、private Production reflection0。既資格1532のfixtureクラスを使用するが、合格証跡の流用は0。新JUnit launcherはexact3method、found/started/succeeded3、F/E/S/aborted/not-run0を要求。新only target/exec/XML、六MainJAR hash・全fixtureclass hashを実行前後照合。Main静的6module0はunchanged byte資格として保持し、新testのcompile-Werror・formatを別記する。全工程coverage合格には算入しない。

実行予定command: `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg1625_unsupported_ports_selected.py`。専用 `/runs/PG1625-selected-v1`・host `/PG379/pg1625-unsupported-ports-selected-v1`、元target更新0、VM/Root/Backup/start/stop0。新source確定後に対象commit/実日時/終了code/XML/hash/coverageを追記する。関連新BUG無し（TDD未実行）。群0464 .25/.75/2pp着手前固定、実N/T/個別費null、正式認定不変更。
