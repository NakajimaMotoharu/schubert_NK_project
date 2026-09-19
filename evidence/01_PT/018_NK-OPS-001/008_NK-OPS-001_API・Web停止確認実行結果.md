# NK-OPS-001 API・Web停止確認実行結果

2026-09-20 最新確定: dev-foundation/source 21cf373541fc7d0d7e131f79ebc9d67db3c44d41、正式PT-WEB-20260920-02（01:27:40～01:43:47 JST、Maven16:06/exit0）、全1455件（Protocol80/Storage74/API660/Web241/Batch359/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定path3method限定静的レビュー・coverage除外なし、CHR runnerのSpotBugsは未設定。15collector/38scopeの同run/source/branch/hashと46負canary成功。DB29部品266＋Batch24部品273＋OPS15部品126＝68部分成果665 PT（全1455の内数）。今回9月19日再開比+40 PT/+3部分成果、PG178～183のSQL資源905複合（先行497＋今回408）と新NULL境界は既存Test ID内の品質修正で部品/件数増算0。BUG207/YKT163完了、BUG195/206・YKT154/162・SSC063は他境界の契約分類を重点確認へ切り分け継続。PG184/SSC067のbackup検証確定callerは仕様のみで未実装。実archive/7世代/親実子制御/全cleanup/通常Question/Web/Logout/QA045/実NK互換gateは未完了、固定加重約4割（35～50%、456）を維持。利用枠残79%で継続、元dev-web3file保全、IT/ST完了ではない。以下は履歴。

007/PT-OPS-STOP-001～016全件PASS。7class/18method/96line/48branchすべてmissed0。固定7property・2unit全条件、未知/重複/欠落/byte/1024+1、固定argv/環境5値、5秒wait/1025byte読取、各stdio close×主故障・全close、割込/64並行を確認した。実systemctlは未配備hostのnot-foundを拒否した読取負系であり、実root配布や停止正系ではない。

正式45の実行command・OS/JDK/tool・branch/fullsource/日時/exit・全Test ID/class/method・source/evidence hashはevidence/manifest.json、results.xmlに固定。OPS manifest SHA256=e9beb9457010cf9aae7c2477edeaabb51da0736b51c2c2270f4531bff13c2050、Batch manifest=a291618071b6b3c92401e6410f2a7b8d5c13083718b02ce91c0db1732b25b747、全体008 manifest=eaab2f525046060d5d0dbcd7d6504423c14b335be83dbf9419662e72ecfe35b8。BUG143～145/YKT113はlogs/BUG-143-145-YKT-113.mdの全4対象で再試験済み。BUG145の修正前失敗は017/logs/BUG-145-compound-close.jsonに保持。探索1のcompile失敗/正式44の未認定を成功へ書換えない。

未完了: 親の実停止/restart禁止/実backup/DB引渡し/原子publish、SSC055永続原本、実root/tmpfiles配布。009/010のrun環境fileは次工程内作業で未合格。PGPT/IT/ST完了ではない。
