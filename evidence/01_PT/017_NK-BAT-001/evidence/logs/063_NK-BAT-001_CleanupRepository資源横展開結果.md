# NK-BAT-001 CleanupRepository資源横展開結果

正式認定: PT-WEB-20260920-01/source5f813145c442e2b80df28d0ede5d1a9e4b9b55ad/dev-foundation、2026-09-20 00:50:23～01:06:30 JST（Maven終了01:06:29、16:05/exit0）。全1455 PT・failed/error/skipped0、6 Java全4coverage100%、Production5静的解析未解決0、固定path3method限定review・coverage除外なし。38scope/46負canary成功。PG178～180の497複合とCleanup4 NULL、既存SQL/不正投影/所有/rollbackを再確認。Batch95class/578method/3515line/1843branch、全missed0。BUG205/YKT161完了、BUG195/206・YKT154/162・SSC063の残Repositoryは継続。新JUnit/部品加算0、実NK CHR/親全体/PGPT/IT/STは未完了。実行環境・入力期待実際・source/test/hashは017/evidence/manifest.json、raw log SHA256=936f1e675b26c8a023d4a61b08d27b6ad9c836af984fe252d77db777c132999a。以下の未認定表記は探索履歴。

探索log SHA256: red=`aa2dc16bd8f80f30b20ecf1a9a61cdbc29f60cf2f5de7ee1892503323a63bc1c`、green=`90f2ae4ca86b38bee0fb93c32a1f427f6d46771ac82498b544ce93471689cc7a`。原logは/tmp、正式manifestは単一clean verifyの同sourceから生成する。

PG180/SSC063/BUG195・206/YKT154・162、062/BAT012。正式未認定。

修正後 `/tmp/pgpt-pg180-green.log`、00:48:53 JST/40.332秒/exit0。Storage8＋Batch45（Cleanup17/Log12/readonly16）の53 PT成功、failed/error/skipped0。新136複合/元4反例/4 resource NULL契約、PG178225＋PG179136複合の回帰も成功。変更CleanupRepositoryは1class/8method/94line/34branchの全missed0、NullAway/Enforcer/Spotless/SpotBugs成功。全取得live0/正確close回数/借用接続不変更/caller rollback後のLog・進捗0を確認。新JUnit/部品加算0。正式全reactor/同source38scopeは次runで確認し、他Repository候補は未完了を維持する。

修正前 `/tmp/pgpt-pg180-red.log`、2026-09-20 00:44:52 JST/10.504秒/exit1。Storage8成功、対象BAT012の1JUnit内4反例が失敗。execute/readLogProgress各々でprovider IAE単独・同一IllegalState本体/closeがBatchRepositoryExceptionへ置換された。progress fixtureは同transactionで実cleanupを先行して行を用意済み。Production source76cfa6c7/仕様23a73aaf、test追加のみ。再現commandは062の選択を `ResourceScopeTest,CleanupRepositoryTest#jdbcFailuresRemainRedacted`、goal=testへ限定した。

失敗を合格へ含めず、4scope/136複合と既存17PT・caller rollback後条件を次に確認する。他Repository残件と全体PGPT/IT/STは未完了。
