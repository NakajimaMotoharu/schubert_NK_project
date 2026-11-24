# Transfer容量の状態語彙とスナップショット 実行結果

PG44238、JDK25.0.4。PT-SCN-008-C04/C05と既存6件を同じexecで8成功。失敗、エラー、skip、未実行各0。選択5型はline58/59、method20/20、class5/5、branch24/24。未到達はスナップショットの例外時解放1行。予約解放の一部の例外命令も残す。FileStoreと実公開、全451、正式判定は別工程条件。

正規SpotlessはPG44240で対象1、終了0。Google Java FormatとCheckstyle終了0。PMDの最初の生22中、新試験のNullAssignmentをBUG-3771で是正し、現生21は旧と同じ指摘箇所・規則。担当処置は継続管理。 [初回](evidence/PG44236-transfer-capacity-values-before-style/manifest.json) [最終](evidence/PG44238-transfer-capacity-values-final/manifest.json)
