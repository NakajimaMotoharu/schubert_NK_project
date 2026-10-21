# fatal通知PTのcompile失敗とimport是正

1371/START324003、SS312313342354/SSC324、BUG1577/YKT1332。元PG6376/source a688d637cd63f24988d3a8906b50cfefc6aef24c は2026-10-21T05:32:30.821527Z～05:34:04.610994Z、元session58948真正終了1。testCompileがassertSame未解決で停止。先行6件/4suiteのXMLだけ存在、残16件/4suiteは未実行。22合格・六static成功・coverage測定とは認定しない。元job終了済み、PG6376再起動/6378資格実行なし。

原manifest `/home/mini/codex/project1/work/pgpt-runs/PG379/pg6376-web-fatal-callback-selected-v1/manifest.safe.json` SHA256 `e838d132db45048ab56342f4910aaba15dec23ae188b67768453e573c25f6711`、archive `d370e591c6ac22ff2473e34d41e5a592d2e1bb4a58a1fa2c69fbcf1ba89eb507`。不成功・未実行を保持する。

## 修正と再試験仕様

Production Main/全期待値/既Testbodyは固定。RuntimeTestへのstatic import一行のみ是正。PG6382は旧元失敗のhash/source/exitを照合し、全src差分がその一行だけか拒否guardする。新only private namespaceでjavac --release25 -proc:noneによるsyntax/import先行検査を行う。qualified54の原XMLからclasspathだけ読み、生成classを正規PTへ流用しない。これは正規null/static/compile gateの緩和やPTではない。終了非0ならPTを発行しない。先行check後、正規Maven/六module staticを変更せず、1371の同一22/8 oracleを実行する。

PT_DEFAULT継承：自己所有tempPG/loopback HTTP/合成fixture/JMS proxyのみ。実VM/業務DB/Root/current/intent/permit等HOLDには依存せず、新操作なし。sourceをclean commitしてから `python3 -B tools/quality/pg6382_web_fatal_callback_retry.py` を一回発行し、元終端までMain/Test固定。真正0後だけ `python3 -B tools/quality/pg6384_web_fatal_callback_retry_qualification.py` で元851Main/1667class/六Jar/XML/実四counter/静的を照合する。対象source・実command・時刻・OS/JDK・input/expected/actual・exit/hashは新begin/manifestと原XMLへ保存する。

新工具四定義試験0（初回はdraftのunused importを検出、工具のみ是正）。Production PT加点0。PG6380は6384成功hash未固定の未公開draft、動的実証/拒否PT代替の認定ではない。必要同source全体は新Test変更群を集約して一campaignで実施する。

event1561開始見積 .25/.75/2pp、startup群.5/2/6pp、原見積/v4は不変更・非加算。compile失敗は手戻り、専有費/実N/T/工数率はnull。正式1964/53、17/190、QA051 final、PTALT不明代替0、全保全/HOLD維持。通常単位で停止しない。
