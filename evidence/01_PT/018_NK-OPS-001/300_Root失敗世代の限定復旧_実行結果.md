# NK-OPS-001 Root失敗世代の限定復旧 実行結果

PG407/SSC144。実装前、未実行・正式未認定。原本/旧Source/PG406失敗は保持。実際のcommand/対象commit/終了code・coverage・manifest hashは完了した実測だけ追記する。

2026-10-01 18:10:45 JST 暫定選択v6: Storage9/Bootstrap4/Batch52=65PT、F/E/S0、NullAway/format/SpotBugs3対象0、43.558秒/exit0。実行commandは `./mvnw -B -o -Dmaven.repo.local=work/toolchain/m2/repository -pl storage,bootstrap,batch -Dtest=LinuxInodeSecurityTest,FixedServiceExecArgumentsTest,RootServiceExecutableAdmissionTest,RootFailedStartRecoveryTest,StartupPermitFilesTest,StartupLaunchFilesTest,BackupStartIntentFilesTest,InspectorUnitSnapshotTest spotless:apply test spotbugs:check`（実moduleはsrc/schubert-nk-接頭辞、JAVA_HOME=work/toolchain/jdk-25.0.4、Node24.19.0 PATH、Linux）。Work PG379/pg407-recovery-selected-v6.log SHA `c7c4b930c135ae9839c76740dacd1ee4c47dee6106f5c5c88e00a5e297d400e1`。未commit Sourceで全/native/coverage100%ではない。v5は64PT、v6は独立post-unlink-sync fault追加の65PT、混算0。

BUG408 RED: postsync-redはformat前拒否/not-run、postsync-red-v2は実FD最終unlink後sync faultでpublication intent無しを再現（1F）。GREEN v6では固定quarantine復旧/INVALID保全を確認。BUG405 nullable leaf・BUG406 private helper/過大close throws・BUG407 corrupt owner固定IO例外も直接再試験に含む。未知runtime/NPEを成功化しない。工具Pg387/Pg407はjavac -Xlint:all -Werrorを通過、工具件数をProduction PTへ加算0。

選択失敗保存: v1 Batch compileでnullable leaf（BUG405）、v2 Testのprivate helper参照、v3 Test.Fixture.closeの過大なthrows ExceptionがInterruptedException可能性として-Werror拒否（BUG406同fixture構築不備）。全てBatch PT not-run、合格0。v3修正前に本欄へ原因を登録し、closeを実delegateと同じStorageIoExceptionへ限定する。compiler警告無効化はしない。

前提観測 2026-10-01 17:48 JST: 真systemd18propertyの旧MorningとAPIはいずれもCode1/status30/Result exit-code、InvocationはPG406捕捉と同一、PID/ControlPID/Job0。Morning start122400577453/end123036616578、API start123033510963/end123035700924 µs。この資料だけではM/A・kernel/DB/typed退役を合格にしない。
