# 移行の三並行値試験の一次原因保全

WBS-P019-03.02/2、F03、BUG-3935、YKT-2997、SS331・333・343・354。対象は合成音声12列、メディア17列、entry-placementの既試験三件（PT-MIG-AUDIOROW015、PT-MIG-MEDIAROW018、PT-MIG-PLACE012）。元仕様033／039／015の固定文字列と手書きbyte期待、lookupの独立位置、返却arrayの破壊検査を残す。

各8 worker、64合成入力を5秒以内に取得し、所有側の終了上限は10秒。既MigrationFixtureWorkersの独立試験で最初の失敗・終了失敗を保つ挙動を参照する。対象は通常選択三件と当正規Bootstrapの局所生カウンタ。残りの試験と既回帰を反復しない。実原本・SQLite/PostgreSQL・COPY取引・ファイル走査・移行権限は保留。
