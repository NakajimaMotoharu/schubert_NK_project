# 正式合格へ算入しない実行

| 日時 JST / log | 状態 | 原因・対応 |
|---|---|---|
| 2026-09-07 23:02 / /tmp/pgpt-auth-password-tests.log | 失敗、合格算入0 | 新Auth testだけを-amへ指定したためProtocol testが0件。failIfNoTestsを緩和せず全reactor試験へ切替 |
| 23:03 / /tmp/pgpt-auth-password-full.log | compile失敗、合格算入0 | crypto jarのSpring Contract annotation不足。Maven通常診断では理由省略。-X生成target/javac.shを同一引数で実行しclassfile warningを特定 |
| 23:05 / /tmp/pgpt-auth-compile-detail.log、pgpt-auth-compile-debug.log、pgpt-auth-javac-direct.log | 診断のみ | gate抑止なし。Spring Security公式catalogと同じcore7.0.9を明示追加して解消。raw debug logはGitへ格納しない |
| 23:08 / /tmp/pgpt-auth-password-full02.log | 269件precheck成功、正式証跡とは別 | Password6件と既存263件、全coverage100%。未commit sourceのため正式target commitを持つ後続runへ置換 |
| 23:11 / /tmp/pgpt-auth-policy-full03.log | 273件precheck成功、正式証跡とは別 | failure policy4件追加、全coverage100%。SQL/session機能は未完成 |

新規機能の初回TDD・依存構築段階の失敗であり、既存実装の仕様違反を成功へ置換したものではない。Failed/skipped/not-runを合格件数へ含めない。
