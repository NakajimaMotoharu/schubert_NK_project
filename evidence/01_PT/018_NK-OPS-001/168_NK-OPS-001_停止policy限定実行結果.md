# 168 親固定停止policy：限定実行結果

2026-09-28 JST、SSC101/SS341§4–5/342§4、Program NK-OPS-001。Java class `MaintenanceUnitStopPolicy.requireSafe`/`NativeSource.read` と非起動Caddy drop-in。関連 RD SYS002/004/OPS009、UI251/253、SS341/342/343、PT-OPS-MPOL001～008。これは停止clientを呼ばない必要条件であり、8 Unit停止・実業務起動の受入ではない。

| Test ID | 入力/独立期待 | 実測 |
|---|---|---|
| MPOL001～007 | SS101の固定8完全名、Id/LoadState/KillMode/SendSIGKILLの各1回ASCII/LF。欠落/重複/未知/512境界/null/全制御byte、Caddy package `yes`、未知例外/割込/64並行、固定systemctl query/全stdio close。Production結果でexpectedを生成しない | `PG318-stop-policy-GREEN-2` の Storage8/Bootstrap8/Batch7＝23PT、F/E/S0、SpotBugs/NullAway0。変更実classのinstruction/line/method/class/branch missed0。初回format gateでBatch未実行、次runはbranch1未網羅で正式不採用。最後の独立 `good+x` 反例を追加した同source `07:41:59` 実行でbranch28/28 |
| MPOL008 / NATIVE030 | 真正root Morning/M+A中、package Caddy既定`SendSIGKILL=yes` は拒否。NK drop-in非起動配備・daemon-reload後、同Production判定が`no`を受理し、Caddy PIDは同じ | reject/accept両probe `ExecMainStatus=0`、Caddy active PID1090のまま、Morning停止後inactive/PID0/leaf不存在。実効`TimeoutStopUSec=30s`、`systemd-analyze verify caddy.service` exit0（既存xfs unrelated warning）。Git外raw exec/原本3SHA不変は `PG318-native030/manifest.json` |

実行command/環境/branch/基点8ad421d6d＋dirty source/test・sourcehash/日付・終了code・sanitized JUnit/coverage/static XML は各provisional manifestに固定。`PG318-stop-policy-GREEN` はbranch1未達の別履歴で、`GREEN-2`だけ限定4指標0missed。collectorは22追加PTではなくPG317新15＋PG318新7を登録し、Batch予定538、独立canary105件全PASS。ネイティブ2runと同byteの限定host execを合成したcoverageは同class4指標未実行0だが、clean無し累積execであり451正式全scope認定へ加算しない。Raw journalのInvocationID、credentials、session/tokenはGitに格納しない。

未認定: Caddyを実際に停止するclient、残6実Unitの配置・実効policy、全8終端、Artemis clean journal、M→同原本resume→A→INVALID/backup/permit、Web/API外部起動、実NK CHR。8 Unit未配備やCaddy policy修正だけを親停止完了へ読み替えない。
