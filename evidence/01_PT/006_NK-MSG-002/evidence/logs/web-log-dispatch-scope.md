# Web log送信・dispatcher中間gate

正式Run `PT-IDEM-20260907-01`、target `aceac18af8490b421d84ab3a93ea17d49fc679cb`。
2026-09-07 00:02:17～00:03:52 JST、Ubuntu26.04.1/kernel7.0.0-31、JDK25.0.4/Maven3.9.12。
Source commit開始時worktree clean、終了code0。全251件（Protocol69/API93/Web48/CHR41）、失敗/skip0、全Java coverage100%、SpotBugs0。

## 実装・試験結果

PT-IDEM-012の対応は仕様書第4節のmethod表と`TEST-dev.codex.schubert.nk.web.logging.WebLogMessageSenderTest.xml`（4件）、`WebLogDispatcherTest.xml`（5件）へ一意に結ぶ。

| 入力/操作 | 独立期待値 | 実際値 |
|---|---|---|
| 正常固定電文、同row2回送信 | 2,336-byte一致、persistent/TTL0、message/correlation/layout/version一致、送達1 | 一致、1 |
| 改ざんciphertext/identity、無効key | 平文非返却、JMS取得0 | 0 |
| JMS mode/write/send/commit/rollback/close/open失敗 | 未確認を成功扱いしない、owned buffer消去、rollback/suppressed契約 | 全経路一致 |
| duplicate typed/cause/linked/循環/類似文字列 | typedだけ確認、循環停止、文字列false | 一致 |
| claim後JMS取得時、別DB connectionでNOWAIT lock | commit済leaseが可視、lock取得成功 | 成功 |
| 送信失敗まで3秒、jitter+10% | next=開始+4.100秒、+4.099秒は未取得 | 一致 |
| retry送信中さらに3秒 | sent=開始+7.100秒、SENT/lease/error clear | 一致 |
| JMS確定後mark用DB接続08006 | PENDING/旧lease保持。10秒一致は0、10秒+1μsで再送SENT、送達1 | 一致 |
| send成功/失敗中にowner変更 | 古いownerのSENT/ERROR更新0、lost=1、新owner保持 | 一致 |
| DB setup/claim/commit/rollback/close/mark失敗 | 例外伝播、close/rollback、mark rollback後PENDING/attempt0 | 一致 |
| null dependency/worker/connection、limit/Report境界 | 明示拒否、overflowで不正合計を受理しない | 一致 |

## BUG・横展開

- BUG-013: 修正前台帳commit `e3211a5`、修正`aceac18`。型別catchへ分離し、暗号/JMS分類の両実DB経路を再試験。全reactor SpotBugs0で完了。
- YKT-009: 既存adapter判定は`outbox-and-web-log-scope.md`、追加Web senderは復号完全decode後のみJMS取得。dispatcherの不正保存rowはERROR/JMS0。全対象修正/非該当と再試験を完了。
- YKT-010: APIの全段階jitter/Clock非回帰、Web repositoryの全段階境界とdispatcher結果時計を実DB再試験。初回送信はdue=enqueue時、jitterはmarkFailureのみ。全対象完了。
- YKT-011: multi-catch/型分類候補24行を確認し、対象Webだけを修正。他候補はBUG-013再現証跡へ非該当根拠を記録。全module静的解析を再試験。
- YKT-007/008はauth/session/revokeの未実装暗号用途があるため未完了。

## 合格に含めない範囲

API ingestのsource_message_id UK、broker cache miss時の最終DB冪等性、HTTP結果を変更しないlocal JSON/投影producer、cleanup/stress、全体NullAway/format、実HTTP NK比較は残る。CHR41件は基盤の単体試験であり実NK画面比較ではない。IT/ST完了は宣言しない。

JUnit証跡はsystem properties/stdout/stderrを除去。固定電文・ciphertext・key・session/token・DB dump・credentialは収集しない。hashはmanifest/checksumsへ記録。
