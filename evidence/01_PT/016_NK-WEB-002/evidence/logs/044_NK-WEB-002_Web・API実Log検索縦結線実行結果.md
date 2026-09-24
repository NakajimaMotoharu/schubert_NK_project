# NK-WEB-002 Web・API実Log検索縦結線実行結果

PG257 / PT-SCR-135選択段階: `WebLogApplicationRuntimeTest` 8/8、failure/error/skipped0。隔離PG18/実Artemis/TomcatのProduction Web/API親を同時起動し、ADMINのHTTP Login、CSRF/cookie rotation、合成Logの`/logs?action=PTSCR135`200・DOM1行/action/message literal、API LGS Inbox1行を確認。初回選択試行はSpotless書式違反で試験未実行、修正後8/8成功。正式全reactor/coverage/53scope/hash前につき認定しない。実NK CHR-L01/A01、Game-context実handler、全process入口は別gate。

2026-09-24 正式限定認定: `PT-WEB-20260924-55`、source `87263eb9b`、Maven `clean verify` exit0（20:30:34 JST終了）。全1859PT（CHR41/Protocol80/Storage82/API732/Web523/Batch401）、failure/error/skipped0。Production対象moduleのinstruction/line/method/class/branch missed0、SpotBugs0、負canary102/102、53scope保存manifest/hash照合PASS。PT-SCR-135のADMIN HTTP→Broker→API Log照会→DOM1行/Inbox1行だけ限定認定する。実行日時/OS/JDK/tool/command/input/expected/actual/coverage/BUG/SSCは本Program `evidence/manifest.json`とroot `008_NK-SCN-001/evidence/manifest.json`へ記録。実NK CHR-L01/A01、Game-context実handler、全process入口、PGPT全体は未完了。
