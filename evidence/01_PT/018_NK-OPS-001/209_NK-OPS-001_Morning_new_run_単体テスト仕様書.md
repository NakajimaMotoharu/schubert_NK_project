# 209 NK-OPS-001 Morning新規run原本・連続所有・単体テスト仕様書

Program ID: NK-OPS-001/NK-BAT-001。対象: `MorningNewRunAdmission.create/execute`、`MorningControlScope.execute`。関連RD OPS-009、UI251/253、SS341§3～5・343§6.15、SSC-055/094/100～102/105、PG343。既存205の停止・A境界に、新規runの専用DB/原本所有を接続する。resumeは対象外とし、外部main、INVALID、backup/Cleanup、permitは未接続のまま非成功を維持する。

| Test ID | 事前条件・入力・操作 | 独立期待値・根拠 |
|---|---|---|
| PT-OPS-MNEW001 | 固定UTC `2026-09-28T05:00:00.123456789Z`、異なるrun/activation UUID、手書きDB/File ownerとevent列 | cutoffはUTC µs `.123456Z`。`root→DB owner→3参照不存在→original start→same-run continuation→File close→DB close→root`。callback中はDB/File両owner保持。実advisory取得・同backend所有は既存MDB試験が別検証。SS341§3/343§6.15から算出 |
| PT-OPS-MNEW002 | 3参照照会が既知IOException | original/open/stop相当callback0、DB close、元例外同一。DB不明を不存在へ変換しない |
| PT-OPS-MNEW003 | original startのdurable IOが失敗 | continuation0、File/DB両close、元例外同一。未確定原本を成功へ補完しない |
| PT-OPS-MNEW004 | originalのrun ID、activation ID、completionのいずれかが新規runと矛盾 | continuation0、固定非成功、全owner close。異なる原本や既完了runを流用しない |
| PT-OPS-MNEW005 | continuationの既知IOException | 元例外同一、File→DBのclose順。外側Mの保持はMCTRLで別確認 |
| PT-OPS-MNEW006 | 未知Runtime、null返値 | Runtime同一、null契約違反。NPEをcatchして成功扱いせず全owner close |
| PT-OPS-MNEW007 | null引数、run/activation UUID重複 | IO前拒否。重複IDを別型file名だからと許可しない |
| PT-OPS-MNEW008 | continuationを別thread/latchで保留 | 解放前はDB/File保持・future未完了。解放後にだけclose/返値 |
| PT-OPS-MNEW009 | `CLEANUP` snapshotをnative factoryへ渡す | MORNING以外は固定IOException、release/DB/fileへ進まない。SS343固定root actor |
| PT-OPS-MNEW010 | native factoryのcontext/snapshot null | IO前NPE契約、値の推測・fallbackなし |
| PT-OPS-MCTRL008 | fake原本stateをM内に置き、stop→A→fresh8→same-run workをevent記録 | 原本/DBはstop・A・workを通して保持。Aはstop後だけ取得、trusted workは同state。手書きevent oracle |
| PT-OPS-MCTRL009 | 原本側のDB参照が失敗 | stop/A/fresh/work各0、M正常close、元例外同一。post-start UNKNOWNの非復帰は別既存MPASS/MCLIENT負試験 |

これらはProduction methodをexpected生成に使わず、固定時刻、手書きevent、spy、独立状態値から算出する。`MorningDatabaseSessionTest`、`MaintenanceRunFilesTest`とともに選択59PTを実施し、null・例外・並行・原本矛盾を確認する。新規runのみのscopeなので既存保留runを勝手にresume/new作成しない。native factoryの真の成功経路、実RootReleaseApproval/private credential/DB advisory、実8Unit、current INVALID、Artemis clean journalは隔離VMで別確認し、fixture通過をR2/R3へ算入しない。

実行command、OS/JDK/Maven/branch/commit、4指標coverage・静的結果、sanitized evidence path/hash、関連障害は210/manifestに記録する。coverage除外なし。新classのnative経路未実行はline/method/branch不足として明記し、正式100%認定をしない。共通root/security境界変更のため、選択後にProduction6全回帰を同sourceで実施し、全体coverage gateは別判定する。
