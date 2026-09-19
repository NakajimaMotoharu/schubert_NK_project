# NK-DAT-001 Inbox永続検査service実行結果

2026-09-20 最新確定: 正式PT-WEB-20260920-23/source749fbae69b7098119af8020f9fe04893e01aca65、08:43:29～08:55:24 JST/Maven11:53/exit0、全1645PT（Protocol80/Storage82/API689/Web386/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。JS1file全line/function/branch100%、18collector/41scope整合・72負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web16/145＝90部分成果855PT（全1645の内数）、今回再開比+230PT/+25部分成果。PG207 Animationメニュー/一覧HTTP12PTを限定認定、BUG222/YKT178完了。PG208/209 Music階層表示は仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web・本文controller-file/readiness/Logout/QA045/実NKgateは未完了。Animation2画面/3route接続を根拠にWeb33～48%へ更新、固定加重39.85～51.35%（中心45.6%≒46%、約40～51%）。残量21%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

## 1. 判定

最新正式判定: PT-WEB-20260909-25/source6dd862d0、2026-09-09 12:46:41 JST完了、全918件PASS、failed/error/skipped0、5 Java moduleの4種coverage100%、静的解析0。本仕様8 PTも全PASS。evidence/inbox-progress-service/manifest.jsonの現行SHA-256は `a7f614966930235ed1ace3dfda0fd1c5bff44df71739e3d6e4b8fc0f041e7c11`。8collector/23scopeの全hashとtrace負canary、V001～013/Current baseline不変、秘密pattern scanを確認。本scopeのcoverage/SQL分岐対応は同manifestと以下の個別結果へ追跡。鍵file読取/main/oneshot・親process・Question/通知参照/親chunk走査は未完了、BUG-014/SSC-049継続。

以下は探索時の履歴。正式未確定/Java接続未完了という旧記述は、上記対象sliceに限り更新済み。process/親接続の残件は維持する。

探索2（2026-09-09 11:14:56 JST完了）: 新Java8/永続SQL8/旧認証8/旧非認証8/DB15/Protocol5/Storage16=68件PASS、failed/error/skipped0。関連8classのline193/method25/class8/branch102/instruction1099、全missed0、NullAway/Spotless PASS・SpotBugs0。正式root gate/証跡は未確定なのでslice完了へ算入しない。QA-046/SSC-049、PG-D-128、023/PT081～088。

InboxCleanupの共通private所有transactionを既存2経路と永続経路で使用する。InspectionProgress/LoadedProgressを追加し、private Work interfaceには実行bytecode/counterがない（除外設定は追加していない）。module全体のcoverage gateは維持。processの実起動/親lock・実backup/key wiring、残参照/全cleanup監査は未完了。BUG-014/YKT-012を閉じない。

## 2. 試験結果の追跡

| ID | 独立後条件 |
|---|---|
| 081 | Login保存error/query/User作成/SCN Fを削除4、unknown key/unknown routeを保護2、累積6・cursor6・END true。残ID5/6だけ、User/Scenario/backup前後不変 |
| 082 | max1で2回中断して累積1→2、次END、既完了ではcandidate fault selector未参照。空runのEND、1,001不正行は最初max1000で累積1000/complete=false、再開1001/END=true、全行保持 |
| 083 | constructorのnull/負count/差分不一致/cursor形態/Long.MAX_VALUEをoverflowなく検証。public run null/max0・1001・int両端拒否。open/record両方の必須SQL列NULLとrun/cutoff/count/xact不正でrollback、progress未作成・Inbox1保持 |
| 084 | open/record各prepare/bind/query/getter/result/statement closeと空/重複rowを実match確認して注入。commit0/rollback1/close1/SAVEPOINT0、削除とprogress共に未commitで復元 |
| 085 | commit前はInbox1/progress0、commit後・close故障はInbox0/累積1未END。いずれも例外を返し、同run再読で最後累積1/END。失敗を一律未削除と断定しない |
| 086 | User/Inbox/backupと既存progressのNOWAIT55P03、成功commit/close各1、途中commit/SAVEPOINT0。open/record/healthでaborted SQLを注入し正常結果を返さず全rollback |
| 087 | 33/33/34完了waveの100呼出し。許容競合は各taskで実観測55P03だけ、全close1/SAVEPOINT0、削除1/保護1/累積2/ENDを確認 |
| 088 | 同run別cutoff/別run未backupを拒否、保存済み結果のID/cutoff/raw context非表示。鍵close後は保護1/ENDであり削除成功にしない |

独立UI TSV/手組auth wireとJCE圧縮AES envelopeを使い、count/SQL行残存はliteralで照合する。Production snapshot writer/encoder/集計をexpectedへ流用しない。正常getterの期待はliteral値・SQL保存値でも検証する。

## 3. 正式証跡

evidence/inbox-progress-service/manifest.json/results.xml/checksumsへ対象source/branch/日時/OS・JDK・DB・driver/tool/command/exit/各Test ID/input・expected・actual/coverage/BUG/SSC/hashを正式root後に記録する。全8collector/18scopeのhash/相対trace、Current baseline・V001～012不変、秘密pattern scanを確認する。wire/key/session/token/ciphertext/DB dumpは格納しない。PG/PTのみ、実NK CHR/IT/ST未実施。
