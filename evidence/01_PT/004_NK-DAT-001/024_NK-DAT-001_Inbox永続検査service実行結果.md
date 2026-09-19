# NK-DAT-001 Inbox永続検査service実行結果

2026-09-20 最新確定: dev-foundation/source 0ca3aa9588fa480ccf4b3e4ff06561f627365e66、正式PT-WEB-20260919-02（09-19 23:58:54～09-20 00:14:59 JST）、全1455件（Protocol80/Storage74/API660/Web241/Batch359/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/etc・/run・/varの3 method限定静的レビューを維持しcoverage除外なし、CHR runnerのSpotBugsは未設定。15collector/38scopeの同run/source/branch/hashと46負canary成功。DB29部品266＋batch24部品273＋OPS15部品126＝68部分成果665 PT（全1455の内数）。PG175～177のroot manifest新規公開・directory公開・bundle耐久化/元inode照合を認定し、今回9月19日再開比+40 PT/+3部分成果。BUG199～204/YKT158～160/SSC064～066完了。BUG195/YKT154/SSC063のSQL等、実dump・tar・age/7世代・親実子制御/全cleanup接続/通常Question writer/replay/Logout RERUN001/QA045は残る。固定加重約4割（35～50%、456）を維持。実NK CHR/IT/ST完了とはしない。利用枠残91%で継続、元dev-web3file保全。PG178は仕様のみで未認定。以下は履歴。

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
