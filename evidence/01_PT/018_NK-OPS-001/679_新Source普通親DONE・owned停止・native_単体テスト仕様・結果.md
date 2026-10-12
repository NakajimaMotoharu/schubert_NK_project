# 679 NK-OPS-001 新Source ordinary親・正常停止・native（PG/PT限定証跡）

対象：MorningProcessMain／ApiProcessMain・ApiProcessLifetime／WebProcessMain、各実起動Unit・Root ownership／readiness／normal owned stop。SS341/343/353/354、SSC274/275、QA047、UIログイン画面・DIF001。Source Main2741c4546afad6c1e8b6efbd53dfb58144edf7bb、Test1683dd9f6de00e71d2317d9af3cd50400a37bf4e、全6 snapshot0044e7d8d1ce46040ec4e8092f63902bd7b32512。正式1964PT/53scopeを変更しない。

前提：signed187/currentPG1638/BOM195e0668…/schema028/history29、同boot3d69。PG1697 noargs/INVALID/元全原値・旧native14保全資格、PG1699外部起動は一回だけ。JDK25.0.4/Maven3.9.12/PostgreSQL18.6/Artemis2.56、LAN隔離VM、host/LANの固定依存を用いる。PG1633/1636の3596PT/532suite/1643Main/静的6module0を再実行せず、当source/JAR/coverage byteを資格して使用した。

| Test ID | 入力・操作／独立期待値 | 実結果・証跡 |
|---|---|---|
| PT-OPS-LIVE-1700-001 | 実startのPID/Invocation/Job/start、署名current、現在active/run/beginを二読。noargs・Root1800秒、旧manifest schema/別source/欠落/null/別identity拒否 | 実readonly0、PID302199/Job106924/run02e941b9/cutoff14:19:28.968927Z/activation40da389f。初回旧schema KeyErrorはSSH前失敗・BUG1155で保持、修正50f908後の独立fixture及びactual0だけを合格対象 |
| PT-OPS-DONE-1701-001 | Production methodではなくPID1のboot/UNIT/Invocation/start-job完了・successとNKRUN/NKACT/NKDONE literalを照合、元30分内。同field foreign/null/期限外/失敗/欠落拒否。現在GCを完了根拠にしない | actual0、真正DONE14:45:34.509749Z/endMonotonic68542820690/1601.536175秒、元budget1800秒。別raw journal二読は私有保全 |
| PT-OPS-SQL-1702-001 | 起動前ef9d全24表を入力、DDL後条件から旧行保持・同日skip8・Backup成功2、件数/attempt/時刻/一対一を独立計算。batch DONE上限とlive Web観測上限を分離 | actual0、旧行保持、Backup2/skip8、匿名Log/session/送達outbox各222。32設定/187署名/元credential・proof・runtimeも三captureで資格。Backup bundle byte/保持は別未完 |
| PT-OPS-STOP-1705-001 | 当完了source/四actorの実PID-Invocation-ticks-argvを独立観測、全seal6703d328…に固定。Werror及びargument/label/original independent oracle、別1706全seal同hash、immutable stage後だけCaddy→Web→API→Artemisのowned正常停止。一回予約、期限/逆順、追加guestSSH0 | compiler0、1706actual0/同hash、stage0、stop0。14:49:46.189761～14:51:19.188013UTC/92.998252秒。preflight作成前のstage試行はhost必要file拒否・予約/guest発行前であり成功に加算しない |
| PT-OPS-POST-1707-001 | 旧PID/子/DB client/advisory/FLOCK消失、新Ref正常、全24行・32設定・187署名/原本Backup/runtime、八terminal receipt及び四explicit stopを別読取する | actual0、全十Unit kernel empty/allActorGone/全client-advisory-flock0、rows不変、native18物理file二読不変。afterSHA3d5c74e1cb01ffd8969c1e5d7b7054957bac64e5b6a07288c1508bc165490362 |
| PT-OPS-NATIVE-1709-001 | 旧4d6の14stream全byteを私有保全し新結果へ取り込まない。当Root/Backup PID1と同API/Web世代・actual時間window、exec session、3596同sourceの6JAR/class CRC/XMLを独立照合。old-source/CRC/時刻/件数差は拒否 | 1708actual0/新8stream/旧history10除外、1709actual0/CRC不一致0。native qualifiedserverSHA74a6484b49d8c503a5e3454a62c85486af856d644cfcbf2a654e008f0014f728 |

実行：`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<fixed pyflakes runtime> python3 -B tools/quality/pg17xx_*.py`（対象1700/1701/1702/1704/1706/1705 stage及びstop/1707/1708/1709）。1705 stopはhost `management_gate(private/current-management-critical.lock)`内で一回。全command/order/source/開始終了/exit/log hashは対応manifestを参照。工具独立testはunittestの対象1700/01/02/03/08/09、生成全Pythonの静的0、Java Werror/oracle0。工具testをProduction coverageへ加算しない。

Coverage：6host exec間union＋当Source native8の残はLINE904/METHOD171/CLASS9/BRANCH716。module-local host残3772/626/37/1085と全host union残3771/625/37/1085は別測定、native gainは後者から2867/454/28/369。四100は未達、除外/人工到達/旧source stream加算なし。QA051 final L01、Inspector/Bootstrap/fault・再送、CHR/DIF、Backup byte/保持、四100・静的/秘密/trace・正式451・引継ぎは別未完。

公開manifest：[679_manifest.json](evidence/output/679_manifest.json)、SHA256 b0cdf5f6b052606cdb55d3cb2108c05fad956382041c3993b4ca4115a1990c5d。11actual記録のpath/hashを一意対応。credential、raw token/session/cookie、master/DB dump、署名秘密key、raw journalはGitへコピー0。private実物はWorkPG379及びguest preservationに保持。BUG1155/YKT923・SSC274275のlimited結果を記録し、旧1153/1154/143/UNKNOWNを成功化しない。状態=当sameSource ordinary/native限定検証済み、formalAccepted=false/wholeleafdelta0/ITST未実施。
