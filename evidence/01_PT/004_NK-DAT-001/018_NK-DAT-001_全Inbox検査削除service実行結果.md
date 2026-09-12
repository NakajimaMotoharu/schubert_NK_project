# NK-DAT-001 全Inbox検査削除service実行結果

2026-09-13 最新確定: dev-foundation/source e919ac03a008355dbc6afa51c8c94c51845a01b2、正式PT-WEB-20260912-07（23:51:38～23:59:15 JST）、全1169件（Protocol80/Storage58/API634/Web241/Batch115/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/etc・/runの2 method限定静的レビューを記録しcoverage除外なし、CHR runnerのSpotBugsは未設定。12collector/35scopeの同run/source/branch/hashと19負canary成功。DB26部品240＋batch4部品45＋OPS11部品94＝41部分成果379 PT（全1169の内数）。PG156のimmutable run/activation/completion型・canonical byte・独立literal実出力8件を認定、新規BUGなし。R002環境file範囲は確定、親実子制御/backup artifact/SSC055原本file store・全cleanup caller・通常Question writer/replay・Logout RERUN001・QA045は残る。PG157の永続record IOは事前登録のみで未合格。固定加重約4割（35～50%、456）を維持、残件は460。実NK CHR/IT/ST完了とはしない。利用枠残82%でPG/PT継続中、元dev-web3file保全。以下は履歴。

最新正式判定: PT-WEB-20260909-25/source6dd862d0、2026-09-09 12:46:41 JST完了、全918件PASS、failed/error/skipped0、5 Java moduleの4種coverage100%、静的解析0。本仕様8 PTも全PASS。evidence/full-inbox-cleanup/manifest.jsonの現行SHA-256は `09a720c7ee1ea6b21931685371c2de1fc97274b0913bd5e9903c7d7db318ffc3`。8collector/23scopeの全hashとtrace負canary、V001～013/Current baseline不変、秘密pattern scanを確認。本scopeのcoverage/SQL分岐対応は同manifestと以下の個別結果へ追跡。鍵file読取/main/oneshot・親process・Question/通知参照/親chunk走査は未完了、BUG-014/SSC-049継続。

以下は初回・探索・旧正式runの履歴。旧hashは証跡commit d98961c6等の該当履歴を参照し、現行manifestのhashと混同しない。未確定という旧記述は本段落の対象sliceに限って更新済み。

## 1. 現在の判定

探索2（2026-09-09 10:18:37 JST）: 新8件＋認証8＋非認証参照8＋V010 SQL8＋DB15＋Protocol5＋Storage16=68件PASS、failed/error/skipped0。共通InboxCleanupとCandidate/Run/Step/Outcome/Exceptionの6class合計line139/method14/class6/branch66/instruction747、全missed0。NullAway/Spotless成功、SpotBugs0。正式全reactor証跡は未確定のためslice完了とは扱わない。

旧AuthenticationInboxCleanupのtransactionを複製せずInboxCleanupへ改称し、V010の全候補と24routeへ接続した。PT033～040認証回帰は維持（011に明記した非認証変造rowのEND→PROTECTEDだけ変更）。PT057～064が新非認証部分。Question/通知7応答は削除せず保護。全run持続状態/oneshot/V006置換は未実施でBUG-014を閉じない。

## 2. Test IDの確認内容

| ID | 実行・独立後条件 |
|---|---|
| 057 | 22route×成功/保存ERROR、ULK0200、SCN Fの46正常削除、各1消失/次END/参照table不変。独立TSV wire＋JCEを先行構造assertしてからDBへ保存 |
| 058 | User型/id/version/後続更新/missing、Scenario型/id/game/日付/missing、unknown key/暗号破損は保護1行。過去成功後の合法更新は許容 |
| 059 | query/User別のversion/対応layout/HMAC version/欠落snapshot、token有無4組、constructor新引数null、未期限/PROCESSING対象外 |
| 060 | UUID順unknown→不正→User→queryをPROTECTED/PROTECTED/DELETED/DELETEDで処理、cursor/残2件を別SQLでassert、再走も保護2件を列挙してEND |
| 061 | query/User/SCNのDELETE/commit/close故障、User/SCNの参照読取り非aborted falseとaborted health失敗を区別。未commit削除rollback、commit/close後不明は再走END、固定例外にcause/suppressedなし |
| 062 | 3候補に100試行、33/33/34の完了waveで進行保証し、全future回収・3件だけ一意削除・残0。各close1/SAVEPOINT0、予定競合は観測した55P03だけ、08006/未観測の負canary |
| 063 | 専用roleのUser/SCN参照、DELETE直前の実row/backup NOWAIT55P03とpassword42501、途中commit0・最終commit1/close1。snapshot current/previous/closed鍵を確認 |
| 064 | query24h/User168hの±1µs、7未実装応答の保護、100回空走査、結果redaction、全業務参照前後一致 |

## 3. 障害・横展開

BUG-089/YKT-080: 旧認証PT037のselector2名をV010共通SQLへ変更し、public JDBC probeにselectedStatements実match数を追加。認証の3selector×fault/row-mode、新PT061のdelete/refを確認。V008/009直接SQL PTは旧contractなので改称しない。collectorは改称後Production InboxCleanupと既存AuthenticationInboxCleanupTestを別名で対応付ける。

BUG-090/YKT-081: 最初の勝者commit前に他99試行が競合終了するscheduleでは一括100回だけで3削除を保証できない。3waveの全futureを各回収して次waveを始める方式へ是正し、時刻/sleepなしで必要な進行を保証。旧認証1候補100試行は1勝者で必要件数を満たし非該当、純read並行も結果一致で同種競合なし。成功した探索runだけでflaky不存在と断定しない。

## 4. 正式証跡

正式runでroot clean verify/全PT/4種coverage100%/静的解析/旧V001～010不変/Current baseline不変/秘密scan/traceを確認し、evidence/full-inbox-cleanup/manifest.json・results.xml・checksumsへsource/branch/日時/環境/command/exit/期待根拠/actual/BUG/SSC/hashを確定する。credential/wire/token/session/DB dumpは保存しない。PG/PTのみ、実NK CHR/IT/STは未実施。
