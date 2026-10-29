# API-Web Payload 原whole52：単体テスト仕様

2026-10-30 / PG-D908 / group3077・WBS-F03/P01809 / source6b53/dev-foundation、着手0.75/4/8pp cap10。Api/WebCustomMetricPayloadTest各26（pure13/full13）/全1336行、二Main85・StandardMetricSource196/StandardMetrics95/sixJvmSystemGC297・先行Scrape/Exporter/recordersを全body/Fixture/initializer読取。原456/460のStandardMetrics97行は実wc95の転記誤りとしてevent3077へ追記訂正、読取内容/scope/予算不変。RD171・UI252・SS351・1800/1812/2195/2201、APIPAY/WEBPAY001..013・APIFULL/WEBFULL001..013、元classname#method/XMLへ一意join。

## PT_DEFAULT・対象と副作用

純goldenのほか、原FULL002/011は新しい専用JVM内の標準SDK binderを実登録する。CPU availableProcessors/memory/class/thread/uptime/FD等の自分のJVMの標準計測とGC通知handle保持・caller closeを含みmock-onlyとしない。JvmGcMetrics handleは登録前にStandardSourceが保持、TWR/finallyでGC→registry順に閉鎖。forceGC、他PIDへのattach/全process調査、外部VM/SSH/Root/業務server/DB/JMS/cohort/graph9/鍵/既存サービス操作0。元Testから部分抽出や新fakeへ置換せずwhole52のまま、原source/Main/Test/Fixture不変更。

## 独立期待値

literal `# TYPE schubert_nk_api_ready gauge` /WEBとready0-1の改行まで正確、customはpool7.5/counter2.5の役割別固定文字列、fullはready→custom→standardの固定順。FullProbe標準TYPE/system_cpu_countの42.0固定golden、actual SDKのCPU数期待はProduction renderでなくJDK Runtime.availableProcessorsから独立取得、jvm_memory_used_bytes presence/TYPE重複0。動的OS数値をサーバ性能やIT/ST受入へ換算しない。

STD sourcefactory/customsupplier read0（owner閉鎖後もready-only）、DEBUG supplier一回・戻りnull/invalidmode/nullstandard/nullsupplier/未bind/closedsourceを異常、borrowedsource再open/close0。custom failure優先・standard未read、各Runtime/Error同一物/非normalization・standard nulltextを文字列nullへしない、formatter failure後もborrowedowner保持。二source独立/finite4thread64task・30秒、caller closeがsource間に入るとpartial返却せずExecutionException cause IllegalStateException・標準read0。helper拒否candidateはTWR/finallyでcloseし元固定診断/回数を維持（自己所有probeのみ）。期待値をProductionから生成せず、raw標準metricsを公開dumpしない。

## command・品質

`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14494_api_web_payload_whole_fifty_two_pt.py`。normal14216/静的14224/全currentinput/六Jar/元SDK/selftestedReporter固定、新一JVM/session/exec一回。PG14496が元52XML/FESnotrun/原環境/一CRC/八反例・二完全Payload Source二physical実counterを独立照合。Source/binders/Exporter等の依存全counterは当scope外、全server接続/GC-native品質/正式受入へ拡張0。未達/自然0保持・手動除外/execunion/旧source転用0。結果2688と公開manifestにsource/branch/時刻/tool環境/command/exit/input期待actual/case/hash/coverage/障害を保存。

原506確認再演0、新正式受入/工数率加算0、正式1964PT/53scope・歴史17-190/別source register/工数null/QA051final/全F03-451/HOLD/原本保全維持。
