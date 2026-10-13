# Backup保持判定追加境界（PG2120、未実行）

Program NK-BAT-001/BackupArtifactVerifier.sameDirectoryInode・inspectRetention・retentionSizesAgree、BAK/BKO/UI251/SS341343、WBS-P017-05（485主担当、0558のP018-01表記は所属訂正/費用移転なし）。公開synthetic archiveの固定Golden manifest/サイズ/hashとPOSIX値の独立oracleで検証し、実Original/Backup/DBには書込0。

PT-BAK-2120-001は固定五identity一項ずつdrift=false/内容size-times-links変化のみtrue/null invariant拒否。002は四fileそれぞれsize+1→Optional.empty/保全、003は四fileそれぞれ非regular→empty、raw負size/異device/ino0はUNAVAILABLE（削除許可としない）。004は三archive同長digest不一致→empty、前後全fixturebyte不変・FD回収を検証。期待値をProduction methodから生成0、反射/OS authority偽造/無意味assert/除外0。正常retainは既MorningBackupRetentionTest/VerifierTestと合わせて実施。

群0558凍結.3/1/3共有pp。必要fixture/関連test/source/command/exit/XML/coverage/hashを新runへ保存するまで未実行。並行/再送・restore/prune実経路・native受入は別条件、fixture成功を実DB/Original削除完了へ換算しない。新source全回帰/正式451/CHR/四100は後続。
