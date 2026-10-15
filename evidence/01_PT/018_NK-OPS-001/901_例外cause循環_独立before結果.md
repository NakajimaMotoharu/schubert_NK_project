# PT-OPS-CAUSE3404-001 独立before結果

仕様899/BUG1299/YKT1065。当a9の原3372API Jar、独立Java標準graphと同package通常呼出し。PG3404-v1はclasspath guardが元reactor Jarをrepo外として拒否し、Java compile/呼出し前終了。新工具の初期未実装TDDとして元slot保全、Production失敗・再現成功には算入しない。source内の既元reactor Main Jarを真正run copyと同byte確認して置換し、不要なbootstrap tests Jarはsource/既知名を認証して不採用、任意classpath解禁0。new-only v2/exec8092 actual0、strict Java25compile0。

| case | 独立期待 | 元実際 |
|---|---|---|
| acyclic | false・有限 | false/exit0 |
| direct | true・有限 | true/exit0 |
| cause-cycle | false・有限 | ENTER後3秒未帰還、own TERM143/reap |
| mixed-cycle | false・有限 | ENTER後3秒未帰還、own TERM143/reap |
| alternate-edge | true・有限 | false/exit0（見落とし） |
| reachable-through-cycle | true・有限 | ENTER後3秒未帰還、own TERM143/reap |
| suppressed-only | false・有限 | false/exit0 |
| message-only | false・有限 | false/exit0 |

8子全回収、TERM不能/force kill0。非終了は実API method進入後だけ認定、疑似timeoutとしない。143は負系canaryの所有回収であってRoot正常化・PGPT合格ではない。公開manifest SHA256 **19e87e1c5054abe5e68fff3bdced72b8d4cfd0cc8c0713ce5b550f48aa47c98b**、元Jar/class/canary/source/wholeのhash・ケース実時間/結果/終了codeを同manifestへ格納。private `pg3404-outbox-cause-before-v1/v2` の元payload/log保持。期待値はfixture型/edgeのliteral、Production戻り値から生成0。Broker/DB/VM操作0、credentials/data/秘密出力0、新Production PT加点0。原因は複数node訪問管理なし＋linked優先でcause edgeを捨てること。修正/公開send owner後条件/YKT全対象/新source品質は未完。
