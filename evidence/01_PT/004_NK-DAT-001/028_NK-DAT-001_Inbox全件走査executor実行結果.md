# NK-DAT-001 Inbox全件走査executor実行結果

2026-09-20 最新確定: dev-foundation/source53c2f7bf8fc6bb45851cd088a78e8f9c590fc45b、正式PT-WEB-20260920-07（03:37:38～03:49:28 JST、Maven11:48/exit0）、全1495件（Protocol80/Storage82/API684/Web241/Batch367/CHR41）PASS、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review/coverage除外なし、CHR SpotBugs未設定。16collector/39scope整合・53負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＝73部分成果705PT（全1495の内数）、今回再開比+80PT/+8部分成果。PG189質問入力境界を認定、BUG211/YKT167・SSC070限定完了。PG190空回答providerは仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/Web/Logout/QA045/実NKgateは未完了。固定加重約4割（35～50%）、残量62%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

最新正式判定: PT-WEB-20260909-25/source6dd862d0、2026-09-09 12:46:41 JST完了、全918件PASS、failed/error/skipped0、5 Java moduleの4種coverage100%、静的解析0。本仕様8 PTも全PASS。evidence/inbox-run-executor/manifest.jsonの現行SHA-256は `ecdb12d3a6dd2cca013532336a84b98a5844e9de0f660b9386c380c0e97804e6`。8collector/23scopeの全hashとtrace負canary、V001～013/Current baseline不変、秘密pattern scanを確認。本scopeのcoverage/SQL分岐対応は同manifestと以下の個別結果へ追跡。鍵file読取/main/oneshot・親process・Question/通知参照/親chunk走査は未完了、BUG-014/SSC-049継続。

以下は探索時の履歴。正式未確定という記述は本sliceに限り上記で更新済み。

027/PT097～104、PG-D-130、SSC-049。探索1 /tmp/pgpt-inbox-executor-explore-1.log、2026-09-09 11:53:20 JST完了、1分38秒、exit0。新8/永続8/旧認証8/旧非認証8/DB15/Protocol5/Storage16=68件PASS、failed/error/skipped0。関連3classのline50/method8/class3/branch29/instruction225、全missed0。NullAway/Spotless PASS、SpotBugs0。正式root/証跡未確定なのでslice完了へ不算入、正式22/886件に含めない。

## 1. 独立後条件

| Test ID | 確認した結果 |
|---|---|
| 097 | 空と既完了はSUCCESS/0、候補faultは未参照・commit/close1。独立JCE Login0101の1行削除、累積1/1/0/END |
| 098 | 未知key/route2行は保持、累積2/0/2/END、WARNING/10 |
| 099 | 1001保護行を1002回の実connection（候補1001+END）で完了、run/cutoff/cursor固定、WARNING・1001保持 |
| 100 | limit30分一致/超過/時計後退はTIME_LIMIT/50。開始前はOptional空、DB0。chunk後ENDでも超過はTIME_LIMIT。limit-1成功・long自然wrap成功。1000確定後の次chunk直前期限で1000未ENDを保持、再開1001/END |
| 101 | 開始前interruptはDB0、close直後interruptはEND確認済でもINTERRUPTED。両方50、flagを消さず、test finallyだけでflag清掃 |
| 102 | 最初のDB障害は未確認Optional空。2chunk目の1001行目commit後・END接続前失敗はSTORAGE_FAILUREで最後確認1000、DB実体1001/未END。最新件数を推測せず同run再読で1001/ENDへ復帰 |
| 103 | 全null依存/run/status/Optional拒否、SUCCESS/WARNINGはENDと保護件数対応必須、failureは最後確認ENDも許容。全statusの0/10/50、enum/record不変条件 |
| 104 | time-limit表示は未確認/確認済を区別、run/cutoff/cursor/secret非表示。予期しないclock例外は伝播、close障害はDB ENDでも非成功/最後未確認、同run再開成功 |

## 2. 証跡と残件

正式run後にevidence/inbox-run-executor/manifest.json/results.xml/checksumsへsource/branch/日時/OS/tool/command/exit/Test ID/期待・実際/coverage/SSC/BUG/hashを記録し、全8collector/20scope、旧V001～013/Current baseline不変、秘密scan、相対trace/負canaryを確認する。Sanitized JUnit結果だけ保存しrawwire/context/key/dumpは格納しない。

本番key reader/main/systemd・親OS lock/実backup/正常API停止・resource終了検証は未完了。Java協調停止だけで長時間SQL/OS processの強制停止を保証せず、親完了gate/PGPT/IT/STの合格を宣言しない。
