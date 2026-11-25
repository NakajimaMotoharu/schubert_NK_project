# NK-MIG-001 移行の有限worker

SS343・354、WBS-P019-03.03/2・F03/2-2-b、BUG-3843・YKT-2997。組立、五投影、Transfer、TargetPublisher、Coordinator、Verifierの有限worker8箇所を検査する。従来134件は各元XMLの試験名・独立期待値・入力順・待機期限で照合する。

PT-BOOT-MIG-ASSEMBLY025では、試験の検査で固定の AssertionError を発生させ、JDK代理 ExecutorService の終了待ちを false とする。元の例外インスタンス、固定の補助診断1件、shutdownNowと期限付き待機が各1回であることを確認する。製品の結果を期待値に使用しない。

カバレッジは単一execと7物理を照合する。実DB・COPY・実ファイルを伴う受入条件は別に管理する。
