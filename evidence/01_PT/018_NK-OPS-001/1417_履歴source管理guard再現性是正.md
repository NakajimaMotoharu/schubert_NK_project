# 履歴source管理guard再現性是正

2026-10-21、BUG1590/YKT1343。6512はa03の三Test専用guardであり、後続Caddy Testを含むc248 HEADを拒否するのが正しい。本体guardのscopeを広げず、管理positiveだけ `a03b6153469f3478ed3b40d2c82e3f89c4d221ab` へ固定した。最初の七管理中一error/終了1はこの対象混同として保持、Production PTの失敗とはしない。

再試験command：固定PYTHONPATH `python3 -B -m unittest pg6512_finite_policy_test pg6516_caddy_identity_test`、七件/F0E0/終了0。別管理checkで6512.guard_source(HEAD)はValueError、6516.guard_source(HEAD)は成功することを実確認。現sourceはc248、当元6516 archiveのMain/Testは固定したまま。管理成功はProduction PTへ加点0。

新二群の全管理positive/negativeを確認：6512 positiveのみ修正、6516 positiveは明示差分fixtureで非該当、両起動はclean live HEADを検査、両readerは各元begin.sourceを検査。guard条件の削除/旧sourceをHEADへの転用/原結果再演0。修正commitは停止保全commitと同じ（最終checkpointに実hash記録）、当scope再試験完了、歴史全tool lineageの完了を意味しない。
