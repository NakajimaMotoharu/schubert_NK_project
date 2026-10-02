# 通知一覧HTTP実行結果

2026-10-03、PG-D347/348/016059。選択v1はWeb51PT/FES0だが既存CSRF返却値静的1件でexit1/Batch未実行、成功fixtureのfilter/date/receipt不整合もBUG560へ先行起票して合格算入0。BUG561へ同class bytes一致・静的単独再現exit1を保存し、抑制せずID変更後条件と独立故障testを追加した。

v2は07:51:16 JST終了/1:48/exit0、Protocol8/Storage8/Bootstrap7/API30/Web56/Batch4＝113PT/15suite、F/E/S各0、SpotBugs6module0、strict compile/format成功。新Notification10・既存CSRF4＋追加CSRF054・API実DB query/再送・User18・wire8・0102・Root関連を選択。Notification4class/CSRF repositoryのline/method/class/branch全未網羅0（他範囲は累積execのため正式coverageへ算入しない）。

SourceはHEAD02beb735b＋WIP、各実file hash・command・環境・終了code・日時・対象suiteを`evidence/provisional/PG437-notification-selected-v2/manifest.json`へ保存、SHA256 `bc4139cd5f3cc91cbc657e9f04116cda626567fa555cc26dd0666a89d5690d1b`。原logはGit外WorkPG379/pg437-notification-selected-v2.log、JUnitはproperties/stdout/stderr/provider診断を除いて保存。BUG560561/YKT404405は同Source全回帰待ち、Current baseline不変更、QA047048049/native fullReady/取消/CHR/正式認定不更新。
