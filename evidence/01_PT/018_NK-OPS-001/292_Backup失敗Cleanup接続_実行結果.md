# Backup失敗Cleanup接続 実行結果

## PG393 固定全6・外部通常再開（23:12～23:21 JST）

固定Source/push `7bb8b1b45fdc0af60a50b8d0a972878a203e61d3`、全6 clean2,615PT/386suite、F/E/S0/static6zero、23:12:44 JST。module80/153/192/760/565/865。sanitized full manifest `evidence/provisional/PG393-failed-cleanup-baseline/manifest.json` hash `8559ec538daeed26de14996db9a3f2aa807d1b8e1c32d1df72d5b0d7dbf9d7b6`。全coverage100%ではなくhost未網羅B/L/M/C614/1761/341/26（前PG392538/1639/325/26から+76/+122/+16/0）。追加は主に失敗用native composer/Root観測面であり未実行を合格としない。

Source同一の新177artifact/61依存/23SQL、release manifest SHA256 `9ae29b220ea02a6f38d0bb7750a307046bee9e0519fdaeeef640dc47fece9c5c`。M/A/全停止/hostRO/pin署名/全BOM/current INVALID、8Unit base全byte一致・正規activation後、外部Morning同run resume→fresh Backupの元4file検証→fresh Cleanup0→今回7step ALREADY_SUCCESSFUL/all0→親advisory再取得/全14列readback/namespace全退役を確認。旧25行をbyte比較で全保持、今回Backup2＋Cleanup7行だけ追加（DB34行）。Transferは旧2file5byte成功を保持し今回正規SKIP、Inspectorは旧END保持のため今回未起動。Artemis/Expiry/issuer未接続のためMorning全体は正常30、permit0・旧active/未完了beginを保全。

Native manifest `evidence/provisional/PG393-native-success-resume/manifest.json` hash `12340ad7d2b1b8fd288a5ae27f349b1893a7f46372b841212a4ee086c7c69a15`。3 actual exec（parent/backup/cleanup）＋純hostを凍結JARと照合、全class mismatch0。旧Inspector execは別Source/今回未起動のため混ぜない。同byteunion missB/L/M/C537/1111/199/12、hostから77/650/142/14解消。PG392実Inspector回の値へ巻き戻さず、異なる実経路を区別。FAILEDの真正Unit試験と100%は未完了。最初の外部SQL `-f <private stage path>` はpostgres roleに読取権限がなく終了1・start未delivery；正常stdin方式で別log採取し、誤commandを合格に加算しない。

次はBUG369/YKT290/SSC125・293/294の同run Broker/Expiry接続。正式run24/1964PT/53scope・中心48.3%据置、実枠16%使用/84%残。通常全6・native回帰だけで停止しない。

2026-09-30実装開始前。SSC124/291、CFREQ/CFDB/CFLOWは未実行・未認定。保存Sourceはd097e998e（PG392実成功はFFD Source固定）。既存PG392 whole Morning30/permit0、Cleanup正常0・7step SUCCESS・Transfer2file5byte実結果と旧DB/Backup/originalは保全し、成功値を失敗に変更しない。Parent同budgetのFAILED branchから実六SKIP/Transferを接続して測定する。

## 2026-09-30 22:51:12 JST 選択試験（暫定、外部受入ではない）

JDK25.0.4/Maven3.9.12/SpotBugs4.10.4.0、dev-foundation。Storage3/Bootstrap3/Batch86＝92件、F/E/S各0、静的3module各0。Source未commitの変更群（Source固定・全6回帰は次段）。実行は `./mvnw -B -o -Dstyle.color=never -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-batch spotless:apply test spotbugs:check -Dtest=LinuxMonotonicClockTest,ChildMaintenanceParentTest,BackupFailureSnapshotTest,CleanupFailedBackupRequestTest,CleanupWorkerRequestTest,BatchRunRepositoryTest,CleanupMaintenanceWorkTest,CleanupTerminalRepositoryTest,MorningDatabaseSessionTest,CleanupWorkerRequestFilesTest,RootBatchCredentialReaderTest -Dsurefire.failIfNoSpecifiedTests=false`。終了code0。

Log `/home/mini/codex/project1/work/pgpt-runs/PG379/pg393-failed-connect-final-reader.log`、SHA256 `476a3df835db925bc9c15c35bf6c89bb4433433769ea5d9730ba9a6ddb361592`。直前選択78件/static3zeroのlog `pg393-failed-connect-final-selected.log`/hash `81c8fd2fe7184090be46d71052f466d8f56414a5803cb82a90aa3010150281e8`は内数回帰、二重加算しない。

独立PostgreSQL後条件で実FAILED二行照合と非変異、今回六SKIP/全0/BACKUP_UNAVAILABLE/開始終了同値/旧SUCCESS保持・転送実2/2/0/5・Inspector不実行・9削除関連table件数不変・全7step親読戻し・成功profileへの混入拒否を確認。型付きrequestの手書きbyte/全18property receipt/正常非0だけ/別Invocation・時刻・signal・timeout、private成功/失敗kind排他・新規限定/重複part保全/退役、親終了pair専用guardの正常/誤handle/null/寿命を確認。これらは合成OS＋実DBのhost試験で、実UnitのFAILED経路ではない。全branch100%・CFREQ006/CFDB004全例外・CFLOW外部は未認定。

初期試験は合格に含めない：単独Batchが旧依存JARを参照（retest.log）、新接続compile2誤り（initial.log）、fixture誤table名（retest.log）、重複発行時のpart保全を試験が見落とし（retest2.log）、移動済methodへの不要な静的suppression（retest3.log）。各logをworkへ保持し、既存仕様の期待値を実装都合で変えていない。新規TDD構築中の誤りで既存accepted処理の障害ではない。最後の固定試験だけを暫定合格とする。

外部FAILEDの前提：旧runはactive/未完了beginを保全、別fresh不可（SS343§6.15）。未実行fixture草案は取り下げ、VM/旧DB25行/Backup9・10/Unit/credential変更0。次は同run Broker/Expiry→正規issuer→API/Web→原本の許容完了を接続し、その後に真正FAILEDを測定する。新枠の実used16/rem84、正式run24/1964PT/53scope・中心48.3%は不変。IT/ST完了を主張しない。
