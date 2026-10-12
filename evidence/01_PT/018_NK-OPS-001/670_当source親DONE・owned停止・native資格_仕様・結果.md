# 当source親DONE・owned停止・native資格

NK-OPS-001 / SS311/341/343/353、SSC190/191/198/268/269/270/271、QA047、BUG1106/1131、YKT875/899。Production4d6bcbddb417b76d27e52d5d9640752c300edccf、VM releasePG1544/BOMe36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c、boot3d69。Java25.0.4/Jacoco0.8.15/ASM9.10.1/Linux7.0.0-34/Python3.14、native分析は隔離LAN serverの同source PG1532固定target、通常PTを再実行せず既資格byteをSHA照合。

| Test ID | 独立期待・事前条件 | 実操作・結果 |
|---|---|---|
| PT-OPS-ROOT-1577-001 | 元run/cutoff/activation、PID1 boot/INV/Job/UID全field・原本DONE、元1800秒内。GC zeroを成功根拠にしない | 1573外部resume一回→同RootAPI/Web ready/Caddy TLS/login200→1577別二読0。1539.994702秒、原本outcome0/DONE end05:02:52.617413Z |
| PT-OPS-SEAL-1578-001 | 全24DB/32設定/187署名/全原本Backup/credential/runtime/四actor/元旧保全を三読、意味的oracleと全sealを区別 | 1578全seal0、1582別直前seal同SHA0、starts/stops/reload/writes0 |
| PT-OPS-STOP-1581-001 | current四PID/INV/ticks/cgroupを同M-A/RO管理DB/advisory/十Refへ束縛。八段同世代、vendor/native TERMと全kernel、全原値・正常scope | 1580 Werror/実OriginalTuple18・argv・label constructor0、独立data negative3/static0、1581immutable stage0→一回reverse stop0、83.725859秒。四explicit、完了oneshot再stop0 |
| PT-OPS-POST-1583-001 | 新stop complete/原本DONE/PID1/当source署名/24DB/32設定/原本Backup/credential/旧保全/runtime/kernel/peer/advisory/flockを独立再照合 | 新1583全post0、全十kernel0/全actorgone/全管理資源0/全新Ref正常。host lookup全hash欠落拒否・run/source/seal負例2 |
| PT-OPS-NATIVE-1586-001 | Backup当PID1 d479/Job51019開始完了＋正常stop、元Root内時刻。旧六native archive保持、旧Inspector二本を非採用 | 旧1584actual1をBUG1131として保全。新1586 actual0/独立新旧・GC-only/全field/timeout/null2、当八stream、原値変更0 |
| PT-OPS-NATIVE-1587-001 | 各実stream single session/time、current1532全六host exec/XML/JAR SHA、全同class CRC、module-local XML独立値。Production methodからexpected生成0 | server1587 actual0、8stream/各single-session0/classByteMismatch0、六module局所/host/union・独立XML一致。旧native imported0、source/VM操作0 |

原本DONE SHA f5f91aa05e698986bc0bce2cfe11b51733294c3c78d13b7352bfc27d5e8329bb。全seal SHA52faff7f880f73f6020ac40d7aa1d8fe170e0e3ed6dfd7f10fd7fbddd8c4f9a9、1582 payload4ab493a9ebc7217f02eacb6e906c9f2e55bd4c1fa49e5cf98146e3e1c66b4235。stop operator d4d20f864e72c1d94555667e1101136cd4313f2f、stop private log12c0ed7173fec115e7d36c8fbb7205a47041671cfc2a3667fe0932059f4e39fa。post operatorba11abfe6fe45b781078175508fb041de1520861/actual0/stderr空。native catalogpayload583dd1b22482bb3bccf9b45124e8cab611695ce0d8a4e708a5ecb226b3060125、server manifest654d7f5935ed19e82a12f7d24bdeb75ff3f92274b0152677ddeecec4f138d6cd。私有rawはwork/pgpt-runs/PG379の同run slots及びguest/serverの対応private領域、公開は安全hash/数値のみ。

実command: `PYTHONPATH=tools/quality:tools/quality/vm/050_s1 python3 -B tools/quality/pg1580_current_owned_stop_compile.py`、`pg1582_current_stop_preflight.py`、`pg1581_current_owned_stop_dispatch.py stage`→`stop`（既発行・再実行禁止）、`pg1583_current_stop_independent_post.py`、`pg1586_current_native_catalog_v2.py`、`pg1587_current_native_qualification.py`。各実manifestに開始終了時刻/終了code/source/hashを保全。native工具は未commit資格中のpayload SHA/固定input全hashを記録、当sourceコード変更0、後続commitに工具byteを保全し正式へ混入0。

当sourceのcross-host＋nativeは残L1184/M219/C11/B767、native追加網羅L2600/M411/C29/B319。これは工数完成率ではなく技術counter。旧source769/旧nativeから合格値を借用しない。global四100・同source Inspector/Bootstrap・business full oracle・runtime退役・fault/replay/CHR/正式451/trace/引継ぎは未完。正式1964PT53scope/wholeleaf受入増分0、IT/ST未実施。旧Root1456 timeout143/1562 closeUNKNOWN/1584failを合格に読み替えない。
