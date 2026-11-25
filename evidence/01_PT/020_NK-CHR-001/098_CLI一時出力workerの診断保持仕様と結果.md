# PT-CHR-OUTWORKER001 CLI一時出力workerの診断保持

SS354／355、NK-CHR-001、WBS-P020-01.01、BUG-3845／YKT-2997。入力は自己所有tempの出力と合成Executor。既存の並行試験の二待機各5秒、worker終了の上限10秒、latch解放→取消→待機の順序を維持する。追加試験では先に用意したAssertionErrorを本体から発生させ、代理の待機結果をfalseとする。同一の一次インスタンス、二次の固定診断1件、各操作1回を確認する。

固定試験source `bb649f77c024b6ce785a32cbd498036f181e1eff`、比較工具版 `4f69b6a033f8ffeee6c61352962a51116f112291`。既6と追加1は全成功、失敗・エラー・スキップ0。正規SpotlessとCheckstyleが終了0。SpotBugs生16の種別構成は元と一致。PMD生20→24、終了所有1が消え、試験専用workerとJDK代理に関する指摘が残る。元結果を保持し品質担当の適用判定は別。単一execでwriteJson二methodを測定し、二つ目に未測定1行と1分岐を残す。現実行環境や実NKの確認には算入しない。

[元コマンド、JUnitと原静的診断](evidence/PG45312-current-cli-worker-diagnostic-and-output-scope/manifest.json)
