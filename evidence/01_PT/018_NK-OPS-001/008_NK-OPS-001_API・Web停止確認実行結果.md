# NK-OPS-001 API・Web停止確認実行結果

2026-09-13 最新確定: dev-foundation/source 2abb30ff800edd3e3fe68d3f9fe73de062c6bba8、正式PT-WEB-20260913-12（08:53:53～09:09:54 JST）、全1391件（Protocol80/Storage58/API660/Web241/Batch311/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/etc・/run・/varの3 method限定静的レビューを維持しcoverage除外なし、CHR runnerのSpotBugsは未設定。15collector/38scopeの同run/source/branch/hashと38負canary成功。DB29部品266＋batch21部品225＋OPS13部品110＝63部分成果601 PT（全1391の内数）。PG168 backup両stepの原子確定16 PT、独立14列/380 JDBC fault/246 service境界・commit不明再読/130複合cleanupを認定、BUG191～194/YKT151～153完了。SSC061のDB pair範囲は完了、root生成/信頼reader/実archive/7世代・親はSSC058/062・R004へ残す。親実子制御/全cleanup接続/通常Question writer/replay/Logout RERUN001/QA045は残る。PG169/SSC062のroot manifest reader16 PTは設計先行・未算入。固定加重約4割（35～50%、456）を維持、残件460。実NK CHR/IT/ST完了とはしない。利用枠残25%で継続中、元dev-web3file保全。以下は履歴。

007/PT-OPS-STOP-001～016全件PASS。7class/18method/96line/48branchすべてmissed0。固定7property・2unit全条件、未知/重複/欠落/byte/1024+1、固定argv/環境5値、5秒wait/1025byte読取、各stdio close×主故障・全close、割込/64並行を確認した。実systemctlは未配備hostのnot-foundを拒否した読取負系であり、実root配布や停止正系ではない。

正式45の実行command・OS/JDK/tool・branch/fullsource/日時/exit・全Test ID/class/method・source/evidence hashはevidence/manifest.json、results.xmlに固定。OPS manifest SHA256=e9beb9457010cf9aae7c2477edeaabb51da0736b51c2c2270f4531bff13c2050、Batch manifest=a291618071b6b3c92401e6410f2a7b8d5c13083718b02ce91c0db1732b25b747、全体008 manifest=eaab2f525046060d5d0dbcd7d6504423c14b335be83dbf9419662e72ecfe35b8。BUG143～145/YKT113はlogs/BUG-143-145-YKT-113.mdの全4対象で再試験済み。BUG145の修正前失敗は017/logs/BUG-145-compound-close.jsonに保持。探索1のcompile失敗/正式44の未認定を成功へ書換えない。

未完了: 親の実停止/restart禁止/実backup/DB引渡し/原子publish、SSC055永続原本、実root/tmpfiles配布。009/010のrun環境fileは次工程内作業で未合格。PGPT/IT/ST完了ではない。
