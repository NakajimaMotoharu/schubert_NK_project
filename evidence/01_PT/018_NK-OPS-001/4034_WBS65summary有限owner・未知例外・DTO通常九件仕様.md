# Summaryの有限owner・未知provider・DTO通常9件仕様

BUG2653/YKT2333、旧INSPPORT001～008を保持し、new INSPPORT009はDB BeforeAllから独立したInspectionSummaryのnull二参照/値getter/complete両値/固定redaction。Production Main変更0、Main8bからbatch199 source/POMが全byte不変のnormal Jarだけを使用する。

所有workerはfuture.get5とfinally shutdownNow/awaitTermination5の両方を有限化。旧8の原sourceはPG26334へ保全、PG26336でbyte逆変換一致、PG26340で規定format後の旧8正規化逆変換が完全一致。先行format stdin引数不足exit2(PG26338)は準備失敗で保全、製品試験に数えない。

INSPPORT006は既16fault point×SQL/ISE/Error三型48を維持し、IAE/NPE二型32を追加。期待値は手組例外instance・固定16point・close数、Main mapperから生成しない。UTC bind期待値は固定OffsetDateTime literalにし、ProductionのInstant.atOffset変換をexpectedに使わない。元priority18組・既assert/literal意味は不変更。

全9を一classで選択し、before/after抽出・旧成功確認目的の再演なし。閉classpathは同byte batchJar/JSpecify1.0.1/Console1.13.4、Test内public JDK Proxyだけ。Main閉包はRepository/Summary/BatchRun/CleanupCounts/JdbcResourceFailures/BatchRepositoryException六classに限定し全sourceを確認。actualDB/SQL実行/driver/InboxCleanup/held四/鍵/Root/native/VM/HTTP/原本操作0。

PG26342 compile0、PG26344全Test静的raw17を各source文脈で非該当と記録し適用0/CS0/解析error0。同byte normalMain NullAway/SpotBugs全batch645ClassStats一致/bug・missing・error0を再利用、不要再compile/staticなし。PG26346 SHA25693a4ff641fb0b274366ec4268aef46ef690f025ed9547d26910af47853bb3173で入力・依存・旧8保持/新32を検査した。

次command（source固定push後だけ）: `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1201_summary_nine_qualifier.py run <固定commit>`。独立post `1203_summary_nine_post.py <同commit>`。六Main全てをreportへ含め、owner内target二classとhelper四のcounterを分けて保存し、helper未網羅があれば残す。target二の測定成功を全三ownedProgram/F02/F03/正式451の完了としない。自然branch0はN/A。

原追補.2/.5/1cap2、実費/工数率null。現在Unit未実行でPASS・coverageは未計上、新規定義予定1/既8。旧正式1964PT53scope・元190新0・globalYKT2177/2328の未了を維持する。
