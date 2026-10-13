# Backup保持判定追加境界（PG2120、未実行）

## PG2120actual0

sourceSnapshot6cec9afd313344074893cee4874f4e92155b41b6/payloadSHA551aaa8e062117d6aead51780e1c425903ea02d18f046e5555821cc0159f59b1、servermanifestSHAdb72e4ba24c863c994668838a77873101dac759783b54a72748c994d5f39ecfe。三suite31PT（新境界4/Verifier17/Retention10）全FES0/staticbatch0/format/compile-NullAway成功・sourcebyte不変。副作用なし/FD回収/保持判定の独立oracleを実施。command=`python3 -B tools/quality/pg2120_backup_retention_selected.py`/既PYTHONPATH、W/pg2120-caddy-metadata-selected-v1/manifest.safe.json/server runs/PG2120-selected-v1。Verifier限定classは残L9/M1/B17・全counter100でない。依存compile-onlyのPT加算0、VM/原本/実Backupへの操作0、正式未受入。

文書番号は既存075との重複を避け687へ確定。TestID/run/sourceの対応は不変更、旧試験資料を上書きしていない。

Program NK-BAT-001/BackupArtifactVerifier.sameDirectoryInode・inspectRetention・retentionSizesAgree、BAK/BKO/UI251/SS341343、WBS-P017-05（485主担当、0558のP018-01表記は所属訂正/費用移転なし）。公開synthetic archiveの固定Golden manifest/サイズ/hashとPOSIX値の独立oracleで検証し、実Original/Backup/DBには書込0。

PT-BAK-2120-001は固定五identity一項ずつdrift=false/内容size-times-links変化のみtrue/null invariant拒否。002は四fileそれぞれsize+1→Optional.empty/保全、003は四fileそれぞれ非regular→empty、raw負size/異device/ino0はUNAVAILABLE（削除許可としない）。004は三archive同長digest不一致→empty、前後全fixturebyte不変・FD回収を検証。期待値をProduction methodから生成0、反射/OS authority偽造/無意味assert/除外0。正常retainは既MorningBackupRetentionTest/VerifierTestと合わせて実施。

群0558凍結.3/1/3共有pp。必要fixture/関連test/source/command/exit/XML/coverage/hashを新runへ保存するまで未実行。並行/再送・restore/prune実経路・native受入は別条件、fixture成功を実DB/Original削除完了へ換算しない。新source全回帰/正式451/CHR/四100は後続。
