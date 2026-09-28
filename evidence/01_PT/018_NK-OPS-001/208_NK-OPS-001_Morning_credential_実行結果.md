# 208 NK-OPS-001 Morning固定credential配布・限定実行結果

2026-09-28 JST、branch `dev-foundation`、作業base `532904b08`、PG342。207のPT-OPS-MUNIT002/004/005を実行。修正前にMUNIT002が `expected 1, actual 0` でRED（3PT中F1、exit1）。固定`LoadCredential=db-batch:/etc/schubert-nk/credentials/db-batch`一件だけを候補Unitへ追加し、GREENは3PT F/E/S0、Batch SpotBugs BugInstance0、Maven exit0。入力Unit SHA-256 `d19b1f06fca7caf54b8061ca6e66ef4324c0db6ad5793a20870a3820357e5ec7`、test SHA-256 `39510210660293f093e638337a8852553a2ae33c4a10c0e734bd75a49e858ab4`。

`systemd-analyze verify`はhostでPostgreSQL Unit/`/usr/bin/java`が無いためexit1となり、構文判定に採用しない。同じ候補を隔離VM `/tmp/pgpt-bug316-morning.service`だけへ置き、VM verify exit0。VMは別名test-only transientのprivate `db-batch` file `0400:0:0:1`、directory `0500:0:0:2`、それぞれexit0。sourceはroot0600/単一linkのmetadataのみ照合。実secretを出力せず、既存`schubert-nk-morning-controller.service`はPG323 probeのままinactive/PID0・無変更。transientを真正Morning起動、実DB admission、R2受入に算入しない。

YKT-249の固定Unit横断検索ではCleanup `db-batch`＋request、Backup `backup-pgpass`＋request、Inspector専用3＋選択previous、Artemis hashed user、およびWeb/APIそれぞれ5材料の宣言を確認した。関連Batch Unit試験10件＋API/Inspector Unit試験12件＝22件 F/E/S0、両module SpotBugs0。他Unitの実配布/起動は別gate。Java Production sourceは変更せず、JaCoCo4指標は本Unit試験に非適用。全体coverage100%/実Morning停止・原本・A/current INVALID/backup/Cleanup/permit、Web/API起動、実NK CHR-A01/L01は未達。正式認定source `858713c0bf310ae8bf62078b0a1cedbce4e968db`/`PT-WEB-20260925-24`、1964PT/53scope・中心48.3%は据え置く。

Sanitized machine-readable evidence: `evidence/provisional/PG342-morning-credential/manifest.json`。RED/GREEN原始logはGit外 `/tmp/pgpt-bug316-{red,green}.log` のSHAのみ記録し、credential内容、raw invocation ID、password、token/sessionは保存しない。
