# NK-DAT-001 全Inbox検査削除service実行結果

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
