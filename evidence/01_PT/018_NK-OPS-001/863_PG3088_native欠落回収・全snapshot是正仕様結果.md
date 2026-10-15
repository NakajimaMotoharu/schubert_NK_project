# 863 native欠落のUNKNOWN回収と全11項目snapshot是正

NK-OPS-001/WBS-N14、SS343/353/451/SSC230259260274276277、BUG1266/YKT1032（1265/1031の共通有限postも継続）。0800同群0.5/1.5/4ppを維持、元/v3/正式1964-53を変更しない。

## 失敗と独立診断

3082 ABI六phase0/3084stage0後、一回3084/exec18382は00:56:39.651663～01:05:35.931457Z、actual143/REFERENCE_SCOPE UNKNOWN/sourceQualifiedfalse・prepare/reloadfalse。新既存parent guardは成功、before.private.jsonを保存した後main189の全key同値を拒否。独立読取で、現原raw92c953eaと当beforeの差はnative dict一件欠落だけ、全rows/原Backup/原本/runtimeは一致。元snapshotからnativeを除外する対応はしない。範囲は工具のcapture_data schemaであり、当a9 Mainや新3691全体合格へ失敗を混ぜない。

3088 actual0でhost119896/t2601236/argv9d39566e/gate FD4・inode9337730をfresh認証。guest Java210904/t2505343/argv986f027b/親210902/101FD・子210935、3090 actual0でchildt2505531/argvd8fccb6d/4FDを確認。backend210933・同peer/DB advisory、M/Aと/run祖先FD31/90、runtimeは元root+parent二entryだけ、failedSAVはbefore.private.jsonとrefs log5d9d0387の二件。3104等の新操作を並べない。

3092 v1はhost header組立前の純検査拒否で空local slotだけ残りguest発行0、再利用せずv2。3092/exec49644 v2 actual0・01:02:23.848045～32.324795Z、全24/187/原Backup/native16と当101/4FD二読・samepeer/二lock・原runtime不変、proof c8d47730a691e0812537e58bc7ec209a9ac3a99b15ac007ec64b178c43a5665d。欠落した旧beforeは原因確認だけであり合格snapshotへ加工しない。

1e6b233d3固定3094/exec36532 actual0・01:04:49.130913～01:05:36.218565Z。同接続fresh proof ff3f8f596ea54834065d12af0aba3b2455afa65e011ef149697b146c7cefc6e9を再作成後、child→Javaへpidfd TERM各一回、両actor/backend/advisory/flock/bus消滅、旧host gate自然解放/同inodequeued承継0。別3096/exec6768 actual0・01:06:13.085508～21.551363Z、payload8dd70ec2、全24原値二読/署名187/Backup/native16安定/全十Unit-kernel・actor/client-advisory-flock0。旧3084は143/UNKNOWNのまま、SAV/raw/hashを保持する。

## 全snapshotの是正

3100/3102/3104/3106を新-onlyとする。returned capture_dataの唯一の10項目returnをASTで特定し、sealed実tree関数による`/run/schubert-nk/pt-coverage`のnative metadata/全file SHAを第11項目へ追加する。初期/中間/終了を毎回実採取し、従来の全key・全値厳密比較をそのまま維持する。before原値を削除/既execを読み替え/観測値をexpectedに差し替えない。既存parent-only writer/Clock5/元inode保持/一entry・一reload/全正常scopeの既条件を維持する。

純二試験actual0: 修正前10keyにnativeなしを独立再現。明示11key oracle、独立4root tree fixtureから正規返却を照合し、native実getter呼出しを確認、file SHA変化の拒否相当（厳密不一致）とnative読取例外の非正常化を確認。全20source/dispatch/post namespace・全24/metadata/source/current/byte条件を完成graphで確認。検査途中のfixture共有参照はdeep-copyに是正し、新工具未完成の失敗を合格へ算入しない。

原証跡はPG379/対応private manifest/guest保全域、rawDB/native exec/session/cookie/token/鍵はGit非格納。新六ABI/有限prepare/独立postとBrowser全case準備は未実行。Rootはまだ起動しない。新3691/3056/3058は別groupとして正常完了し、残659L133M5C483B・四100未達を維持する。
