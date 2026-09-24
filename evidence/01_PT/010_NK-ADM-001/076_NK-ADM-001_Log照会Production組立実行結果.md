# NK-ADM-001 Log照会Production組立実行結果

PT-ADM-075/076 / PG256選択段階: `LogQueryApplicationServiceTest` 9/9、failure/error/skipped0。隔離PG18/Flyway＋実Artemis、Production `LogQueryApplicationAssembly`→`ApiLogPathApplicationRuntime.startWithLoginAndLog`のLog初回0000/再送0200、Inbox1行/再送監査1行、factory null4引数を確認。初回選択試行は試験側のresult欄offset誤記（193）で1 failure、SS324の208へ修正。続く2回目はSpotless書式違反で試験未実行、3回目に9/9成功。いずれも正式認定へ算入せず、正式全reactor/coverage/静的解析/証跡hash待ち。実NK CHR-L01と全API起動は本caseの合格範囲外。
