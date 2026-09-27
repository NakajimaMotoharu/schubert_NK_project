# PG312横断回帰・inventory是正（暫定）

Trigger: SS331 V023＋共用DB ResourceのDDL/security横断、D02/04/05。source1b7d1848e固定のfull6予定2161PTは02:47:32 JST exit1。Protocol80/Storage149/Bootstrap135成功・各静的/report実行済、API742中4failure（StepCleanup1/InspectionParent1/DatabaseMigration2）、API静的/report未到達、Web/Batch未実行。既存Web/Batch targetのXMLは当該run証跡ではない。

BUG285/YKT218を修正前登録。承認V023後の現行inventory23/最後V023/resource allowlistをliteral更新、旧V001..022のhash保持（V022は802e9c26a frozen sha56968e…）。historicalV021→V022 caseはtarget022を明示しexpected1/rerun0維持、現行V023/security8PTは別caseで確認。02:51:11限定75PT/static0・105canary成功、[manifest](evidence/provisional/BUG285-preflight/manifest.json)。未完は全6再回帰。

BUG286/YKT219: 旧RED metadataを次preflight開始後のactive targetから取得したdraftでAPI failure3/旧log4の不一致を検出。draftの全active-target suite hashを不採用とし、事前退避3失敗suite XML（1+1+2=4）＋旧rawloghashだけを[RED manifest](evidence/provisional/PG312-regression-RED/manifest.json)へ固定。正式run24不変、混在draftを認定へ使用なし。次fullは全採取/同source/hash/退避完了前に次test開始禁止。失敗/未実行・native gapを合格算入しない。

Environment/command/sourcehash/時間/loghashは各manifest。既存正式858713c/run24/1964/53scope/48.3%不変更。全6再回帰後、PG313 fixedroot署名済承認原本・同bytes fullBOM/schema gateへ継続。work-draft/PG313_release_approval_connection.mdに限定review根拠を保全、まだProduction設計完了ではない。
