# NK-DAT-001 Inbox永続検査service実行結果

2026-09-09 最新確定: dev-foundation/source20af737d、正式PT-WEB-20260909-42（19:47:16～19:54:18 JST）、全1075件（Protocol80/Storage50/API634/Web241/Batch29/CHR41）PASS、failed/error/skipped0。6 Java moduleのline/method/class/branch100%、Production5 moduleのSpotBugs0/NullAway・Enforcer・Spotless PASS（CHR runnerのSpotBugsは未設定）。12collector・35証跡scopeの同run/source/branch/hash/参照、017の1件・019の14件負canary成功。DB26部品240 PT＋batch2部品29 PT＋OPS2部品16 PT＝30部分成果285件確定。PG-D-146の実Linux flock8 PT（実コマンド双方向競合、32並行、FD/例外回収、inode差替え）を追加し、BUG140/YKT110を再試験完了。正式41はbranch1不足で不合格・後続3module未実行として保存。親root lockfile検証PG-D-147はSS/PT仕様のみ未合格。親inactive/実backup/DB引渡し/root設定publish・全cleanup監査・通常Question writer/replay・RERUN-001は残る。BUG-014/UIC-006/SSC-049/052継続、加重見積約4割（35～50%、456）、試験件数だけで加点しない。週間残18%。元dev-web Scenario3fileは保全・不算入、CHR41はrunner PTであり実NK互換gateではない。以下は履歴。

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
