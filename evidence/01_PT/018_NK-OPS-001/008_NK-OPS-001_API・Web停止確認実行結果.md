# NK-OPS-001 API・Web停止確認実行結果

2026-09-12 最新確定: dev-foundation/source 3eb3712e1b1827154a27fc6bcfe6c47c987e0e32、正式PT-WEB-20260912-05（23:01:26～23:09:05 JST）、全1161件（Protocol80/Storage58/API634/Web241/Batch107/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/etc・/runの2 method限定静的レビューを記録しcoverage除外なし、CHR runnerのSpotBugsは未設定。12collector/35scopeの同run/source/branch/hashと18負canary成功。DB26部品240＋batch3部品37＋OPS11部品94＝40部分成果371 PT（全1161の内数）、PG155の固定account・namespace/環境寿命16件を追加しBUG154～156/YKT120～121再試験完了。R002の環境file部品は確定したが、親実子制御/backup artifact/SSC055原本・全cleanup caller・通常Question writer/replay・Logout RERUN001・QA045は残る。既存停止照会の別障害BUG157/YKT122は先行起票・未修正で次に対応する。固定加重約4割（35～50%、456）を維持、残件は460。実NK CHR/IT/ST完了とはしない。利用枠残86%でPG/PT継続中、元dev-web3file保全。以下は履歴。

007/PT-OPS-STOP-001～016全件PASS。7class/18method/96line/48branchすべてmissed0。固定7property・2unit全条件、未知/重複/欠落/byte/1024+1、固定argv/環境5値、5秒wait/1025byte読取、各stdio close×主故障・全close、割込/64並行を確認した。実systemctlは未配備hostのnot-foundを拒否した読取負系であり、実root配布や停止正系ではない。

正式45の実行command・OS/JDK/tool・branch/fullsource/日時/exit・全Test ID/class/method・source/evidence hashはevidence/manifest.json、results.xmlに固定。OPS manifest SHA256=e9beb9457010cf9aae7c2477edeaabb51da0736b51c2c2270f4531bff13c2050、Batch manifest=a291618071b6b3c92401e6410f2a7b8d5c13083718b02ce91c0db1732b25b747、全体008 manifest=eaab2f525046060d5d0dbcd7d6504423c14b335be83dbf9419662e72ecfe35b8。BUG143～145/YKT113はlogs/BUG-143-145-YKT-113.mdの全4対象で再試験済み。BUG145の修正前失敗は017/logs/BUG-145-compound-close.jsonに保持。探索1のcompile失敗/正式44の未認定を成功へ書換えない。

未完了: 親の実停止/restart禁止/実backup/DB引渡し/原子publish、SSC055永続原本、実root/tmpfiles配布。009/010のrun環境fileは次工程内作業で未合格。PGPT/IT/ST完了ではない。
