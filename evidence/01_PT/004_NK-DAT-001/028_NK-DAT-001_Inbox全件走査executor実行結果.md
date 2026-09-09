# NK-DAT-001 Inbox全件走査executor実行結果

最新正式判定: PT-WEB-20260909-30/source15cb454a、2026-09-09 14:30:10～14:36:41 JST、dev-foundation、exit0、全967件・6 Java module全4種coverage100%・静的解析0。当scope全Test ID成功、evidence/inbox-run-executor/manifest.json SHA-256 `7e9dc3dc17862a8ad2141000099f91df381be448366c16a428dce0628d151d75`。全27scope同時点性/hash/参照と017の1件・019の4件負canary成功。DB19部品160件＋batch repository17件確定。BUG-109～111/YKT-096/097再試験完了。BUG-104/SSC-051のSQL永続走査・親repository読取は成功、全件走査service/OS/main/backup gate/7参照/全Program完了は残件。本slice合格と工程全体の合格は区別する。以下は旧正式・探索履歴。

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
