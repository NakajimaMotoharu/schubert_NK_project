# PG2654 新source普通親・停止・native独立受入

対象 NK-OPS-001/NK-BAT-001/NK-WEB-002。RD OPS-009～017/BAK/AVL、UI251～253、SS341～343/352、品質451。Production `04207efc3ad78bca75942153a90c70985064c988` / release `0.1.0-PG2654` / BOM `552c5e25591483ee2c9aa95c6b8170f37e3390b14bd08ed88bfc0c4870002a37`。operator `6fa57f4ae9fe42d76ca7760b7b89eb16b6017b83`、branch dev-foundation。既存Linux VM boot b2d6、JDK25.0.4/Maven3.9.12/PostgreSQL18/Artemis2.56、LAN試験環境は既構築記録を継承。秘密/原本/dump/raw sessionは私有領域だけ。

## 独立期待値・実操作

SSの30分、承認済WARNING10、同run/cutoff/activation、普通四peer generation/identity/socket/info、署名187artifact、全24表SQL後条件/32設定項目、停止逆順/資源解放を固定期待値とする。Production自身からexpectedを生成しない。Current A01固定baselineは016/105を参照。

親run `77601cf8-0ade-40fd-813f-c81d5210845e`、activation `26250063-8755-43b6-9ac7-f76d5eee7257`、Root396053/t6390214/Job88073/Invocation f024366fbe4a4e91b0dc64ecd6c76366、cutoff `2026-10-14T06:56:07.778154Z`。実DONE `07:24:35.698243Z`、1747.729761秒、WARNING10。pid1/journal/done原値と二読を照合。UnitはGC済みのため現在ExecMainStatus0を業務code0へ読み替えない。旧runの終端を新成果へ流用しない。

実commandは `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<既存pyflakes-runtime> python3 -B tools/quality/<下記program>.py`。一回起動2684v2、observer2682、binding2686、before2698は保存済み成功を参照し再発行0。

|Test ID / program|実時間UTC / 終了code|独立結果|
|---|---|---|
|PG2700 operation_current_terminal|07:26:31～32 / 0|真正parent/root/pid1 DONE、同世代、WARNING10、1800秒以内|
|PG2702 operation_current_rows|07:27:17～31 / 0|全24/独立SQL後条件、新匿名Log224/session223/SENT224の一対一、Backup2/SKIPPED7/保護WARNING1|
|PG2704 operation_current_full_seal|07:28:05～49 / 0|四owned live、32/187/24、原本SHA/当before/真正terminal、SQL oracle照合|
|PG2706 operation_current_parent_projection|同source / 0|親18項目とseal参照を独立照合。先行呼出しは排他gateでguest dispatch前拒否、保存event0717。full終了後のみ実行|
|PG2710 operation_owned_compile|07:29:30～31 / 0|全15sourceのcompile/oracle/label/original ABI、guest変更0|
|PG2712 operation_owned_dispatch stage|07:29:47～49 / 0|新工具の一回stage、Source不変|
|PG2712 operation_owned_dispatch stop|07:30:03～07:32:18 / 0|正規四owned stop、親二source18項目/全体prequal、起動0、旧failed正常化0|
|PG2716 operation_owned_post|07:32:49～57 / 0|全24二読不変、十Unit/kernel/actor空、client/advisory/flock0、187byte、八terminal receipt、native二読stable|
|PG2718 operation_native_catalog|07:33:22～24 / 0|当十point/九streamの資料、旧28exec保全のみ、Backup pid1世代/inspector同process二point|
|PG2722 operation_native_qualification|同source / 0|全1643Main/物理七差（意味六/debug一・NativeIo含む）、新九stream CRC/session mismatch0、旧native輸入0|
|PG2724 operation_backup_content|07:33:34～43 / 0|当run canonical manifest/実三archive SHA/二DB handle-count-byte/八config entry、15139991bytes、pg_restore list0。Backup/restore/prune再発行0|

公開receipt hashは `evidence/provisional/PG2654-current-chain/manifest.json`。私有原値は work/pgpt-runs/PG379 の各同名slotへ保持。全実終了code0。工具fixture・排他拒否・observerをProduction PT件数へ加点しない。

## 範囲・残件

PG2694/2695の同Test source全3666PT/541suite/1643Main/static六module0と、当新nativeの資格を接続。hostに対するnative追加測定はline2882/method465/class28/branch327、当union残line788/method156/class9/branch542。四100は未達。旧a79/0fd nativeは合算しない。

BUG1246/YKT1012のdefault BOM是正は b208d7dfc、全五省略producer/全consumerの独立14fixtureと当実終端/全24/seal/owned/post/native/Backupで対象再試験を閉じる。対象外/是正表は818・台帳を参照。これは工具障害の完了で、全leaf/PGPT/IT/STの完了ではない。

WBS N05/N12/N13、P017-12.01～.03、P018-06、P016-25.02、K01.01のcriteria/終了依存はevent0716へ分割対応。全leafの受入delta0、工数完成率null、正式1964試験/53領域不変更。QA051 finalL01保留。YKT988の実Browser全四formは未受入：IABの既guest URL `https://10.0.2.15:55160` はnavigate timeout、フォーム操作0/証明書回避0。既CHR-A01限定PASSとは区別する。残owner/factory/CHR/四100/451/trace/引継ぎへ継続する。
