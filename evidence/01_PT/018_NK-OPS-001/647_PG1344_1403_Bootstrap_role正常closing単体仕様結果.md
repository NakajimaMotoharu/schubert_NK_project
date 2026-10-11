# NK-OPS-001 current769 Bootstrap role・既存ADMIN・closing限定仕様結果

関連RD OPS009/TST004、UI251、SS343/353/355、SSC263（main8ac7fdd1/PR102）、451。Production `769ddb15cd735c25fef581b5f9850ef9d0053c0f`、release PG1292/BOMecae187/schema028。Java source・DDL・承認済業務仕様は変更しない。正常Root1320/停止1336は再発行しない。正式1964PT/53scope据置、IT/ST完了ではない。

|Test ID・対象|事前条件/入力・操作・独立期待値|結果/証跡|
|---|---|---|
|PT-OPS-BOOT1344001/現before|全24/full32/187/原本BackupStartup、元11role・18exec、唯一既ADMIN、current769と全停止を独立二読|1344 actual0、old baseline f64ed468…、後から書換え0|
|PT-OPS-BOOT1348001/compiler/Expected|flat実ABI、固定三桁PG998 DB applicationと四桁filenameを別契約、実constructor正常/拒否|1348/1356/1363/1397 Werror0、actual Expected vector5及びCLI。旧四桁DB拒否・partial出力保持|
|PT-OPS-ROLE1369001/有限role policy|Root0755/ACL0/11role/18exec全9値保持、唯一new Bootstrap inode0700/999:981、nlink+1/size+20/time実操作区間。全旧field改変/null/unknown/余剰/境界を独立literalから検査|policy2host0、1387 prepared実検査0・1389/1391/1395/1400再読で全元値保持|
|PT-OPS-ROLE1371001/held directory IO|new-only/NOFOLLOW/0700/held child FD・owner変更/dirsync、正常/各fault位置/既存拒否/親保全|real host FD、独立69assert/19fault position0、runtime4 libraryをSHA資格化。byte資格の再読を新PT成果へ加点0|
|PT-OPS-ROLE1380001/実SQL|backend正常/最小最大/null/型/空/未知、actual AST queryと独立完全SQL literalの一致。実PostgreSQL READ ONLY EXPLAIN3・rollback、DB writes0|2host0/1383actual0。旧pid数値直後AND欠落はBUG1090、旧TEN_REFS UNKNOWN/143を保全|
|PT-OPS-ROLE1382001/旧失敗owner|現在PID/ticks/exe/argvSHA・唯一子/私有Bus/十Ref宣言/M-A FLOCK/DB peer消失/全原値を二読、pidfd child→parent各一回・耐久予約|1381proof0/1382handoff0・全資源0、old1377prepare143。現role作成前の旧工具を再prepareしない|
|PT-OPS-ROLE1389001/作成後失敗owner|実保存before/prepared/有限role差分と唯一pair、DB0・原値保全。作成済roleを変更せずchild→parent一回回収|1389proof0/1390handoff0、after1e1b3fc3…、old1387prepare143。DATABASE_CLOSEの旧不具合BUG1091/oldNormalClose=false|
|PT-OPS-ROLE1392001/state-action DB|独立16pair matrix：READY-before/BEFORE-preparedはDB1、PREPARED-closed/CLOSED-releaseはDB0、他順序/型/null/未知は拒否。actual送信functionを試験|2host0、旧stateでDB1を要求する実装を別世代是正。既roleはheld openExistingChildで読取確認、mkdir/chown/修復0|
|PT-OPS-ROLE1394001/管理全scope|current署名187/genuineDONE保持、新M→A/RObatchDB/advisory/heartbeat/十Ref/FD、現role/全値不変→DBclose/Ref/FD/A/M正常|new stage0/verification0（10.632409秒）、全新scope正常。old作成試行のnormalcloseはfalseのまま|
|PT-OPS-ROLE1395001/独立全post|元native全値・唯一empty role/ACL/tmpfs/NSS、tool全recursive byte/hash、全24/full32/187/原本Backup/credential/runtime/全資源0|1395actual0、new baseline37715c53…/31nodes18exec。旧f64baselineを改変0|
|PT-OPS-ADMIN1396001/正常CLI・Unit|現baseline/current769/既ADMIN/元RootDONE、固定app/NSS/Unit30秒/秘密は私有、一回stage→verify0→execute。業務DB不変更/正常exit20・捕捉PID1 job・同INV terminal/closing2|1396 stage/verify/execute全0、Unit1.489676秒、PID1 job139918、新INV SHAed49bb43…。credentialは同inodeの私有退役、Gitへ実体0|
|PT-OPS-ADMIN1400001/独立post|捕捉正常20をGCより先に検証、同INV/native2/元11role18exec+新roleの有限効果、credential有限retire・元session/DB全行不変、全十Ref current/全kernel/client/advisory/FLOCK0|1400actual0/4.006165秒、33nodes20exec・source一致、全original/新scope正常。GCを過去成功根拠にしない|
|PT-OPS-NATIVE1401001/実同source|1279 frozen6host +1341 currentRoot8 +新Bootstrap2のみ、各実inode/hash/session/Unit時間・同一JVM二dump・全6JAR独立CRC/noMatch|1401actual0、10native/9JVM executions・全classByteMismatch0。increment L27/M2/C0/B1、missL897/M176/C12/B723|
|PT-OPS-GAP1402001/独立XML|16data inputsをhashjoin、XML四counter exact一致・class/method/line座標、除外0/VM操作0|1402actual0、gap SHAa158b62c…。Bootstrap残L1/M1/C0/B0=inspectorUnit572、API22L/2M/0B、Batch874L/173M/12C/723B|
|PT-OPS-TOOLS1403001/変更工具回帰|変更31test moduleを限定実行、失敗/skipを加算しない・実行source/command/hash記録|37test/F0/E0/S0、Production PT加点0。public manifest SHA69ece9eb…|

実行commandは各Test IDに対応する `tools/quality/vm/050_s1/pg<番号>_*.py`（manifestに固定source/hash/exit/UTC/環境/branch/commandを保存）。Java25.0.4/Python3.14.4/Ubuntu26.04/PostgreSQL18.6/JaCoCo0.8.15。期待値は独立literal、実保持FD/inodeの前後条件、全SQL後条件、PID1 receipt/明示Unit結果、独立JaCoCo分析を使い、Productionでexpectedを作らない。raw credential/session/native/DB/全journalは私有、publicはhash/countのみ。

全sourceの技術coverageは L42856/43753=97.950%、M7121/7297=97.588%、C1184/1196=98.997%、B17516/18239=96.036%。これは工程完成率ではない。四100未達、正式認定不変更。当default export177/Checkpoint lambda107は正規Bootstrap closingで新たに網羅、InspectorUnit572は別合法Inspector実経路が残る。当日履歴/時計を変えない。

BUG1081～1091/YKT850～860の旧失敗は保存、新再試験と原因scopeは台帳追補へ記録。role補足→正規ADMIN20/closing→全post/nativeは限定成果、WBS leaf全受入加点0。QA051最終L01、当sourceInspector、Log/replay/故障・競合matrix、残CHR/451/trace/引継ぎ・隔離Web副担当統合は未完。通常のこの保存で作業を停止せず後続へ進む。

エビデンス: [manifest](evidence/provisional/PG1344-1403-current-bootstrap-role-admin/manifest.json)。保存する私有場所はmanifestのhash参照のみで、実体をGitへ加えない。
