# NK-DAT-001/P00403 純record codec追加四PT仕様

事前仕様は[4480](../018_NK-OPS-001/4480_P00403純codec不変条件・hash別名・公開enum四PT仕様.md)として製造/実行前Gitへ固定済み。本書はprogram内索引で、新しい期待値や合格基準を後付けしない。

対象MaintenanceRecords全private/public method、関連MaintenanceRetirement/BatchRun/Activation/Completion/Outcomeの計六physical・53Code。RD OPS009/DAT、UI251、SS332/343 6.13、411/451、PG-D-1170、BUG3169/YKT2638。元三whole source16件を保持し、新RAW001..004（非実体化guard・未知status hash二反例・enum順序/配列所有・公開名/null/未知）を追加。記録bytesは元16の独立手書golden、hashは31進多項式の固定vector、enum/guardは事前定義literal。

原所要見積を消化とせず、追加.2/.6/1.5 cap2。新Main一classの物理変更に対して一回whole20を実施し、元16/別pure8を合算しない。実native/DB/Root/file退役のPTへ拡張しない。入力/command/branch/commit/環境/実結果/coverage/BUG/証拠hashは当programのevidence/PG37284-record-codec20/manifest.jsonと元run/post参照へ一意に結合する。
