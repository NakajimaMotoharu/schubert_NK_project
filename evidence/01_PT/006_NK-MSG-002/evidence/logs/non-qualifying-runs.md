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

最新Formal runはtarget commit `0f1b381`のclean verifyだけで実装済み範囲を判定し、failure/error/skipped/flaky/disabledを0としている。PT-IDEM-009～015は未実装・未実行でありPASSへ算入していない。
