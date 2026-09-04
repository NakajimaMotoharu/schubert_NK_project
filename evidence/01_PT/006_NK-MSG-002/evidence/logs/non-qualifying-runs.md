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

Formal runはtarget commit `50d0a91`のclean verifyだけで判定し、failure/error/skipped/flaky/disabled/not-runを0としている。
