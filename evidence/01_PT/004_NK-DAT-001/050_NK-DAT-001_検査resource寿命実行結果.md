# NK-DAT-001 検査resource寿命 実行結果

049/PT-DB-INBOX-209～220、SS343 §6.7/SSC-049/PG-D-143。実装・探索中、正式未合格。正式source/run/証跡hashは全体回帰と全collector成功後のみ記録する。main/unit/親OS/実backup gateを含まない。

## 探索履歴（正式合格に算入しない）

2026-09-09/JDK25.0.4+7/Maven3.9.12/PG18.6、dev-foundationの未commit source。`/tmp/pgpt-inspector-application-explore-N.log`はlocal診断だけでrawログをGitへ転記しない。

| 探索 | 結果 |
|---|---|
| 1 | 18:01:23 JST終了1、22.426秒、新12件中11成功/1 error。開始割込が先行password IOで設定例外になったためBUG134/YKT105を修正前登録、SS343 §6.7補足 |
| 2 | 18:04:38 JST終了0、53.950秒、新12＋既存Process12/executor8/DB接続7＝API39件PASS、failure/error/skipped0。開始割込IO0・読取途中割込の実FileChannel失敗/closeも確認。依存Protocol5/Storage7は別集計 |
| 3 | 18:06:50 JST終了0、14.303秒、新12件全PASS、failure/error/skipped0。存在しない隔離DBへの実接続失敗も追加しSTORAGE_FAILURE/全root解放/進捗0を確認 |

対象2classは探索coverageのline/method/class/branchすべてmissed0（Settings18/3/1/12、Application21/3/1/2）。正式全体回帰と32scope/10collectorの照合前には合格認定しない。017の1件と019の10件の独立負canaryは成功、Java件数へ加算しない。
