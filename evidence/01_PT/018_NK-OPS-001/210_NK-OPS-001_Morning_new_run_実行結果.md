# 210 NK-OPS-001 Morning新規run原本・連続所有・限定実行結果

2026-09-28 JST、branch `dev-foundation`、source/test commit `d5e9dcb5231de554c741d14484cd41e7359a15b9`。対象・独立期待は209。JDK25.0.4、Maven3.9.12、JaCoCo0.8.15、SpotBugs4.10.4.0、Node24.19.0、Linux host UID1000。

選択 `MorningNewRunAdmissionTest`10＋`MorningControlScopeTest`9＋`MaintenanceRunFilesTest`28＋`MorningDatabaseSessionTest`12＝59PT/4suite F/E/S0、Batch SpotBugs0・Maven exit0。新規runはM保持の内側で専用DB owner・全3参照不存在→durable原本開始→固定8 stop→A→fresh8→同state continuationの順序を手書きeventで照合した。DB/原本失敗時のstop0、元例外保持、wrong run/activation/completion拒否、null、未知Runtime、別thread保留中の二owner保持を確認。port試験のDB ownerは実advisory取得の代用ではなく、既存MDB12がSQL/lockを別に確認する。

共通root/security/所有境界変更をtriggerに、同一sourceでProduction6を `clean test spotbugs:check jacoco:report`。Protocol80、Storage149、Bootstrap175、API742、Web555、Batch674＝2,375PT/349suite F/E/S0、6module SpotBugs BugInstance0、Maven exit0。失敗した初回format・testCompile・追加root recheckの試行はこの結果へ混入しない。全JUnitをproperties/stdout/stackなしでsanitizedし、aggregate coverage2・static6・JUnit349＝357fileのpath/SHA照合済み。manifest `evidence/provisional/PG343-morning-original/manifest.json` SHA-256 `48d484dd80279b01656fe49370c333d96c5b8501a51d96b2ed35e104431f70d9`。原始logはGit外 `/tmp/pgpt-pg343-selected-59.log` と `/tmp/pgpt-pg343-six-clean.log` に保持し、manifestにhashのみ記録。秘密・raw session/cookie/token/InvocationIDはGit証跡へ保存しない。

4指標coverageのmissedはProtocol/Storageが各0。Bootstrap branch37/line11/method4/class0、API1/19/3/0、Web1/19/3/0、Batch9/161/63/6。変更本体 `MorningNewRunAdmission` branch3/line13/method2/class0、`MorningControlScope` branch0/line11/method4/class0。native factory・固定private credential・真のM/A/8Unit成功経路未実行につき100%未達、除外なし。全6成功は正式同source coverage100% gateではない。

外部`MorningProcessMain`はPG339 fail-closed exit30のままで新scopeを起動しない。実VMの既存保留原本/旧current/PG323 test-only Morning Unitは不変更。新規runのみのscopeでありresume選択、current INVALID、Artemis clean journal、backup/Cleanup、permit、5未配置の正規Unit、handleなしUNKNOWNのhard-timeout後保全（BUG315/YKT248）は未達。R2/R3・実NK CHR-A01/L01を合格扱いにしない。正式認定source `858713c0bf310ae8bf62078b0a1cedbce4e968db`、run `PT-WEB-20260925-24`、1964PT/53scopeと中心48.3%は据え置く。
