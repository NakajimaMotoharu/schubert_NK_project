# NK-BAT-001 CleanupRepository資源横展開結果

探索log SHA256: red=`aa2dc16bd8f80f30b20ecf1a9a61cdbc29f60cf2f5de7ee1892503323a63bc1c`、green=`90f2ae4ca86b38bee0fb93c32a1f427f6d46771ac82498b544ce93471689cc7a`。原logは/tmp、正式manifestは単一clean verifyの同sourceから生成する。

PG180/SSC063/BUG195・206/YKT154・162、062/BAT012。正式未認定。

修正後 `/tmp/pgpt-pg180-green.log`、00:48:53 JST/40.332秒/exit0。Storage8＋Batch45（Cleanup17/Log12/readonly16）の53 PT成功、failed/error/skipped0。新136複合/元4反例/4 resource NULL契約、PG178225＋PG179136複合の回帰も成功。変更CleanupRepositoryは1class/8method/94line/34branchの全missed0、NullAway/Enforcer/Spotless/SpotBugs成功。全取得live0/正確close回数/借用接続不変更/caller rollback後のLog・進捗0を確認。新JUnit/部品加算0。正式全reactor/同source38scopeは次runで確認し、他Repository候補は未完了を維持する。

修正前 `/tmp/pgpt-pg180-red.log`、2026-09-20 00:44:52 JST/10.504秒/exit1。Storage8成功、対象BAT012の1JUnit内4反例が失敗。execute/readLogProgress各々でprovider IAE単独・同一IllegalState本体/closeがBatchRepositoryExceptionへ置換された。progress fixtureは同transactionで実cleanupを先行して行を用意済み。Production source76cfa6c7/仕様23a73aaf、test追加のみ。再現commandは062の選択を `ResourceScopeTest,CleanupRepositoryTest#jdbcFailuresRemainRedacted`、goal=testへ限定した。

失敗を合格へ含めず、4scope/136複合と既存17PT・caller rollback後条件を次に確認する。他Repository残件と全体PGPT/IT/STは未完了。
