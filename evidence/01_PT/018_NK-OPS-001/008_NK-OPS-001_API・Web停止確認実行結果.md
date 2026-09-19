# NK-OPS-001 API・Web停止確認実行結果

2026-09-20 最新確定: 正式PT-WEB-20260920-12/source0d0abbb80e91d016f961042e9b9e09cb07b5f7a9、05:24:36～05:36:26 JST/Maven11:48/exit0、全1544PT（Protocol80/Storage82/API689/Web285/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。18collector/41scope整合・60負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web4/44＝78部分成果754PT（全1544の内数）、今回再開比+129PT/+13部分成果。PG194階層3画面16PTを限定認定、BUG213～216/YKT169～172/SSC071限定範囲完了。PG195本文モデルは仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web/Logout/QA045/実NKgateは未完了。固定加重38.25～49.75%（中心44%、約38～50%）、3画面接続で前回から+1 point。残量49%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

007/PT-OPS-STOP-001～016全件PASS。7class/18method/96line/48branchすべてmissed0。固定7property・2unit全条件、未知/重複/欠落/byte/1024+1、固定argv/環境5値、5秒wait/1025byte読取、各stdio close×主故障・全close、割込/64並行を確認した。実systemctlは未配備hostのnot-foundを拒否した読取負系であり、実root配布や停止正系ではない。

正式45の実行command・OS/JDK/tool・branch/fullsource/日時/exit・全Test ID/class/method・source/evidence hashはevidence/manifest.json、results.xmlに固定。OPS manifest SHA256=e9beb9457010cf9aae7c2477edeaabb51da0736b51c2c2270f4531bff13c2050、Batch manifest=a291618071b6b3c92401e6410f2a7b8d5c13083718b02ce91c0db1732b25b747、全体008 manifest=eaab2f525046060d5d0dbcd7d6504423c14b335be83dbf9419662e72ecfe35b8。BUG143～145/YKT113はlogs/BUG-143-145-YKT-113.mdの全4対象で再試験済み。BUG145の修正前失敗は017/logs/BUG-145-compound-close.jsonに保持。探索1のcompile失敗/正式44の未認定を成功へ書換えない。

未完了: 親の実停止/restart禁止/実backup/DB引渡し/原子publish、SSC055永続原本、実root/tmpfiles配布。009/010のrun環境fileは次工程内作業で未合格。PGPT/IT/ST完了ではない。
