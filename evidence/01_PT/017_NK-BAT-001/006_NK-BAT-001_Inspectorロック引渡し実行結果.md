# NK-BAT-001 Inspectorロック引渡し実行結果

005/PT-BAT-030～037、PG-D-150。実装済み、探索2（2026-09-09 21:22:51 JST）はStorage50/Batch65、計115件・4coverage100%・静的解析成功。新8件は親→子transaction→親の実ロック、再入/別namespace/競合、全JDBC位置/null資源/結果破損/close・割込・親状態を確認。探索1は静的指摘1件で不合格（BUG146/YKT114、先行702b64ac）。正式47の全体回帰・証跡同時点性待ちであり未確定。正式46以前へ追加8件を遡って算入しない。親OS lock/実子起動/backup/固定run原本/設定publishは本部品で完了にしない。
