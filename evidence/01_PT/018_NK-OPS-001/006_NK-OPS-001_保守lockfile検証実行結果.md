# NK-OPS-001 保守lockfile検証実行結果

探索4: 2026-09-09 20:08:40 JST、Storage50＋Batch37（うち本Program新8）全87件成功、両module4coverage100%、SpotBugs未解決0/NullAway/Enforcer/Spotless PASS。`-pl src/schubert-nk-batch -am verify`、log `/tmp/pgpt-maintlock-explore-4.log`。BUG-142は35767cf2で修正前登録し、固定/run portability warning単一method/IDのレビュー済みannotationを明示（005）。正式43全体clean verify・全証跡収集が終わるまでは未認定。

005/PT-OPS-LOCK-001～008、PG-D-147/SSC-049。実装・探索試験中、正式合格は未認定。探索1は指定classが依存StorageにないためfailIfNoTests gateで停止しBatch未実行。gateは緩和せず探索2でStorage＋Batch全試験を実施、20:03:19 JSTにStorage50/Batch36成功・Batch1失敗（BUG-141の/sys固定RO oracle）。BUG-141/YKT-111を修正前登録d3ead999、独立/proc/mounts照合へ修正して新探索/正式runを行う。ProductionのRO拒否期待値は不変。正式42以前へ遡って合格に算入しない。root実配置・親unit・停止/backup/DB引渡し・IT/STは別残件。
