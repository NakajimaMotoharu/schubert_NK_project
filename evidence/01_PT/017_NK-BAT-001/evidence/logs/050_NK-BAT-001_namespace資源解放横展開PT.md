# NK-BAT/OPS root・namespace資源解放横展開 PT追補

正式PT-WEB-20260913-14/source b234a4b356a9b456d3fdd245dbd6baed568be426/dev-foundation、2026-09-13 10:51:57～11:08:12 JST、Maven16分13秒/exit0。1415件PASS（Protocol80/Storage66/API660/Web241/Batch327/CHR41）、failed/error/skipped0。6 Java全4coverage100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、3固定path限定review・coverage除外なし。15collector/38scopeの同run/source/hashと41負canary成功。PG171～174の306compoundを既存Test ID内で認定し新JUnit/部品増算0。BUG198/YKT157完了、BUG195/YKT154/SSC063はSQL残候補等のため継続。実NK Characterization/IT/ST/親全体は未完了。 実行command/環境/input/expected/actual/coverage/関連BUG/SSC・SHA256は本書および017/018各evidence/manifest.json、同runの各JUnit XMLを正とする。以下は正式前の仕様・探索履歴。

## 2026-09-13 選択試験結果（正式認定待ち）

設計先行6d5e4901、branch dev-foundation。修正前10:37:09 JST/7.908秒/exit1（/tmp/pgpt-pg172-red.log）でLOCK006/NS002/BAT079全3件がself-suppression IllegalArgumentExceptionとなり失敗。修正後の初回compileはimport欠落BUG198/YKT157で失敗（/tmp/pgpt-pg172-green.log、Batch未実行）。欠落2class修正後、10:40:46 JST/1分09秒/exit0（/tmp/pgpt-pg172-green2.log）、Storage13＋Batch80=93 PT成功・failed/error/skipped0、84compound全通過、NullAway/Spotless/SpotBugs未解決0。PG171の54compoundも同実行で再確認。

command: JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-batch -am -Dtest=ResourceScopeTest,ExistingFileAccessTest,MaintenanceFileLockTest,InspectorEnvironmentFilesTest,MaintenanceRunFilesTest,DurableRecordFilesTest,InspectorEnvironmentReaderTest,InspectorEnvironmentPublisherTest,MaintenanceRetirementRecordsTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check。cwd=work/pgpt-foundation、未commit作業treeは後続source commit・正式runで固定する。

対象選択coverage: FileLock5class/24method/81line/52branch、EnvironmentFiles2/23/117/30、DurableRecordFiles1/31/180/76の全missed0。PG171で未選択だったplan/markerの3分岐もMaintenanceRetirementRecordsTestで通過。MaintenanceRunFilesはGC関連class2/method37/line251/branch110が未選択で、全体100%とはまだ判定しない。次の全reactorでGC PTと併せる。除外追加なし。

探索log SHA256: red=26bb0f0d99030442274a7c1b5de63c9ae67afb2dede7fd6f6112d9e8bde1dd46、初回compile失敗=c8db01b900b91021e9bfb217d78ef6d642e3216d3954f803b94f01240c79fe8f、green2=bddb5b1495216fe0af96a2a74b1b127768043ba0f3a0f5c1a390d998fa90067f。公開合成fixtureだけを使用。019の40＋017の1負canaryも成功。source/formalを固定するまで本項は探索結果。BUG195/YKT154は広域残候補、BUG198/YKT157は正式再試験待ち。

PG172/SSC063継続、BUG195/YKT154、実装前仕様。NK-BAT-001/NK-OPS-001、OPS009・UI251・SS311/341/343。正式13/source82055460へ未実行観点を遡及加算しない。

SSC063継続/PG172・BUG195/YKT154: MaintenanceFileLockのrun/app取得・再照合、InspectorEnvironmentFilesの5 root取得・再照合、MaintenanceRunFilesの6 root取得・再照合とnames列挙を共通ResourceScopeへ横展開する。取得順・取得直後のadmission順・逆順一度close・Session無効化の時点・static参照byte消去・失敗時run環境保持・borrowed能力を変更しない。DirectoryIteratorExceptionは列挙body内で既知IOへ固定化してからcloseし、未知cleanupを隠さない。未知bodyと同じThrowableをcloseが投げても元identity＋固定secondary1、既知IO bodyと未知cleanupは同じ未知cleanupを伝播する。Runtime/NPE/Errorを正常化せず、入力null契約と公開仕様を維持する。process/JDBC候補は別段で未完了を維持する。

## Test ID・独立期待値

- LOCK006 MaintenanceFileLock.tryExclusive/verifyCurrent: callback失敗後に外側app/runの各closeへ未知を注入。2位置×既知IO/同一未知body×IllegalStateException/NPE/AssertionError3型=12case。callback中のclose数からentry→app→runの3終了を独立計数、native FD全解放、外部flock再取得0、lockfile 0byte維持。
- NS002 InspectorEnvironmentFiles.execute/verify: callback失敗後に外側5rootの各close。5×2×3=30case。取得済全FD/readers/writers解放・callback1・5close、公開run環境は固定RUNTIME byteのまま保持、unlink0、静的CONFIG byte不変更。
- BAT079 MaintenanceRunFiles.execute/Session.verifyNamespace: callback失敗後に外側6rootの各close。6×2×3=36case。6close、全FD/readers/writers/listings解放、Sessionは閉鎖状態、recordsの新規生成なし。
- BAT079 MaintenanceRunFiles.names: 最初のnamesIteratorの既知IO（DirectoryIteratorException）または同一未知bodyとnamesClose未知を組み合わせ、2×3=6case。取得済stream一度close、全資源解放、何もpublishしない。

追加合計84compound caseは既存3 Test ID内の観点であり、新JUnit数/部品数は0。期待値はProductionから算出せず、Throwable identity/固定Storage secondaryのreason・cause/suppressed、close注入1回/実native解放/固定byte・ファイル集合を独立assertする。未知primaryの場合は同一元例外＋固定StorageIoException secondary1、既知IOの場合は同一cleanup未知・secondary0。借用資源は解放しない。

外側root取得13個と再照合root13個・列挙1個の全27scopeを修正対象とする。再照合の各unknown組合せを別々に網羅したと主張せず、共通ResourceScopeの全契約PT＋既存全open/close/metadata IO故障matrix・前後identity交換・全分岐PTを併用する。null/missing/parallel/割込と成功時cleanup/失敗時保全を既存PTで再実行する。

## 実行・証跡方針

Ubuntu26.04.1 amd64/JDK25.0.4/Maven3.9.12（421）。変更前red→変更後3class・PG171の4class・ResourceScope・MaintenanceRetirementRecordsTestの選択PT→全reactor/4coverage100%/NullAway/Spotless/SpotBugs。format後に同時Mavenなしで実行。未実行/failed/flaky/skippedは成功へ算入しない。

source/branch/command/日時/exit/coverage/BUG/SSC/結果/hashは本追補と017/018の正式manifestへ固定する。既存Current baseline・RD/UI/test oracle/coverage除外は変更しない。PG171の未選択retirement分岐も関連PTと全体試験で再確認する。process/JDBC/親/backup生成/IT/STは未完了。
