# NK-BAT/OPS/MED 既存file資源解放横展開 PT追補

PG171/SSC063継続・BUG195/YKT154。source修正前の仕様。正式13/source82055460はこの追加反例をまだ実行していない。新しいJUnit件数・部品数への加算0、既存Test IDの再発防止観点として管理する。

SSC063継続/PG171・BUG195/YKT154: 同じIO close優先順位をDurableRecordFiles.readFile/write/force、InspectorEnvironmentReader.readFile、InspectorEnvironmentPublisher.writeNew/forceExisting、ExistingFileAccess.walkのchannel/childへ適用する。nullable IO resourceは従来の固定IO拒否（ExistingFileAccessのnonnull channelは境界NPE拒否）を所有受領前に実施し、callbackの値/IO順/サイズ/metadata/partial保全/借用root・非公開能力を変更しない。8所有scopeを既知IO＋未知cleanup/同一未知body＋cleanupの各Runtime/NPE/Error3型で独立再試験する。Directory/Process/JDBC等の残候補は別段で未完了を維持する。IO型と回復責務を変える一般frameworkや追加coverage除外は採用しない。

## 対象・Test ID・独立oracle

| Program・関連RD/UI/SS | class/method・Test ID | 追加反例・固定期待 |
|---|---|---|
| NK-BAT-001、OPS009/UI251/SS343 §6.14 | DurableRecordFiles.readFile/write/force / BAT056 interruptionsAndUnknownRuntime | read/new/reuseでread/readClose・write/writerClose・force/writerClose。3scope×2 primary種別×3未知型=18。既知IO時はcleanupの同一未知、未知bodyと同一close時はbody同一・固定Storage secondary1。全readers/writers/entries0、借用root継続・既存GOLDEN/部分保全不変更 |
| NK-OPS-001、OPS009/UI251/SS343 §6.9 | InspectorEnvironmentReader.readFile / EFILE007 ioFaultsAndRedaction | static/run2kind×2 primary×3未知型=12。read/channelCloseのpositive到達と一度close、全取得byte消去、元byteとroot保全 |
| NK-OPS-001、OPS009/UI251/SS343 §6.11 | InspectorEnvironmentPublisher.writeNew/forceExisting / PUB010 interruptionAndRuntime | new/reuseのwrite/force→writerClose、2scope×2 primary×3未知型=12。未知同一/固定secondary/全owned解放、new未公開part保全・reuse原本不変更 |
| NK-MED-001、FIL006/007/UI237/243/SS333 | ExistingFileAccess.walk channel/child / MED024 | channel.closeとchild descriptor.closeを別注入。2scope×2 primary×3未知型=12。未知同一/固定secondary、開いたchannel全closeと借用root継続、元3byte固定値不変更 |

合計54 compound case（既存JUnit Test ID4件の中）。既知primaryは既存IO fault port、未知は新しい公開合成IllegalStateException/NullPointerException/AssertionErrorを各caseで生成する。expectedをProductionで生成しない。same identity/例外型/固定reason・suppressed件数/注入回数/close回数/実byte・mode/inode状態を独立assert。未取得resource/借用rootをcloseしない。failed/flaky/skipped/not-runは合格に含めない。

## 実行・証跡

JDK25.0.4/Maven3.9.12/Ubuntu26.04.1/amd64（421）。source修正前に選択4 Test IDでredを実行し、標準TWRが期待を満たさないことを確認する。修正後は対象4class＋ResourceScope/OwnedTransferDirectory/LinuxFileLock/Backup Reader/Verifier/Probe、既存全fault inventory、NullAway/Spotless/SpotBugs、全reactor/4coverage100%を確認する。同時Mavenは禁止。実行時刻/command/exit/branch/source・BUG/SSC・結果/coverage・SHA256を本書と017/018/MED各manifestへ記録する。

探索結果: 2026-09-13 10:18:09 JST/4.137秒/exit1のStorage MED024でself-suppression反例1件を確認（/tmp/pgpt-pg171-red.log）。依存Storage failureでBatchは未実行だったため、既存ResourceScope8件を依存側選択として別実行し、10:18:37/8.004秒/exit1にBatch3対象で同じ反例3件を確認（/tmp/pgpt-pg171-batch-red.log）。期待IllegalStateException同一、実際IllegalArgumentException。修正前の4失敗を合格へ算入しない。

修正後は10:20:11/30.677秒/exit0、Storage13＋Batch32=45件成功、54複合case全通過、NullAway/Spotless/SpotBugs未解決0（/tmp/pgpt-pg171-green.log）。readのcompoundは2回目へ注入し、内容を読んだ後の配列消去を確認。write側も実引数配列を保持して終了後のzeroを検証。既存partial保全とGOLDENを不変更。対象coverageはExistingFileAccess2class/11method/39line/10branch、EnvironmentReader2/19/70/34、Publisher3/32/127/40が全missed0。DurableRecordFilesは全31method/1classを実行したが、既存retirementのplan/marker分岐3・line2は今回の選択対象外であり100%とはしない。次のretirement関連PT/全reactorで検証する。

実行command: JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-batch -am -Dtest=ExistingFileAccessTest,ResourceScopeTest,DurableRecordFilesTest,InspectorEnvironmentReaderTest,InspectorEnvironmentPublisherTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check。cwd=work/pgpt-foundation、branch=dev-foundation、対象はPG171未commit作業tree（後続source commitと正式runで固定する）。

BUG195/YKT154とSSC063は継続、正式認定待ち。検索だけで他対象を完了としない。正式認定後も実backup生成・親終端・全PGPT・IT/STの完了を意味しない。
