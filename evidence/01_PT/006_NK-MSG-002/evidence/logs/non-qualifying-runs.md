# 合格算入外run

以下はTDDまたは実行command調整中のrunであり、formal PASSへ算入していない。

| 区分 | 結果 | 扱い |
|---|---|---|
| BUG-007修正前DB negative | 15件中failure 1 | 障害再現。`BUG-007-reproduction.md`へ保存 |
| Response snapshot初期TDD | serialVersionUID compile gate、empty stream decode error | 未実装codeのred→green。PASS算入外 |
| Response snapshot初期coverage | branch 219/220 | 未網羅分岐を旧鍵未設定negative testで補完。PASS算入外 |
| Reactor対象指定の調整 | Protocol moduleに対象testがなくMavenが非0となった複数回 | Test未実行。PASS算入外 |
| BUG-008修正前`NKENC1` negative | 6件中failure 1/error 1 | 障害再現。`BUG-008-reproduction.md`へ保存 |
| BUG-008修正中coverage | branch 1件不足 | 37-byte envelope境界を追加。PASS算入外 |
| Inbox test初回assertion | API 78件中failure 1 | Redaction検査fixtureが一般的なerror文言と偶然一致。秘密値に固有markerを用いるようtest oracleだけを是正。PASS算入外 |
| Inbox初回coverage | line 936/956、branch 358/370 | PostgreSQL一意競合・terminal update消失の制御caseを追加し全分岐化。PASS算入外 |
| JaCoCo CLI直接実行 | `rules`引数なしで非0 | Lifecycle外の診断commandでありtest結果ではない。PASS算入外 |

| Outbox初期TDD（2026-09-05） | serialVersionUID、proxy例外、fixture表示順/PG timestamp丸め、未網羅分岐を調整 | 初期未完成testのred→green。最初の実装済みstatic違反はBUG-009へ別途起票。PASS算入外 |
| Outbox中間Run `PT-IDEM-20260905-02` | target `80d6ea0`、Protocol 69/API 88、coverage 4指標100%、SpotBugs 0 | 後続独立レビューでBUG-010～012を発見。PT-IDEM-010/011およびProgram完了のPASSへ算入しない |
| 再開初回precheck（2026-09-06） | 追加時刻testのhelper未作成でtestCompile failure | 未完成testの補完。既存NULL確認helperへ接続し、PASS算入外 |
| 実行環境precheck（2026-09-06） | sandboxがloopback socketを拒否しPostgreSQL test setup error、Web reactor未実行 | test権限を明示して制限外で再実行。製品障害ではなく環境制限。PASS算入外 |
| Web log初回TDD（2026-09-06） | Web 35件中failure 1。独立AAD field長合計が126、実ASCIIは127 | table名は20+1+14=35 byteでありfixtureの34を訂正。production AAD/期待wire値は変更しない。PASS算入外 |

最新の正式実行は`manifest.json`でtarget commitと対象Test IDを固定する。未実装・未実行・部分実施のTest IDはProgram全体のPASSへ算入しない。

| Web sender初期TDD | test identityをUUID下位bitのdecimal12/15で生成し、SS goldenのhex12/15と不一致 | 固定UUID文字列を明示して試験fixtureを是正。既存codecのrow一致検査が正常に拒否したもので、production oracle変更や製品障害ではない。旧失敗runはPASS算入外 |
| Web sender再開precheck | Protocol69/Web43成功、coverage全100%、SpotBugs0 | 部分reactorの開発確認。正式全体runと別管理し、Program完了へは算入しない |
