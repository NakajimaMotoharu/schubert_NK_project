# BatchHistory診断の静的検査と通常試験

NK-OPS-001／NK-BAT-001、WBS-F03/2-2-b、P004-05/2に費用0で参照、SS332／341／351、451 §5、YKT-2863。PG42930、2026-11-23 JST、試験 `22757b3411869c6d765f722b7b63219b3dee98d0`。元BatchStepValuesとBatchRunAuditPortのprivate History実体化を外した。PT-BAT-HISTORY-STATIC001で現classfileの `toString` が固定literalを読み、そのまま返す二命令（ldc／areturn）と確認。フィールド読み・UUID／時刻参照なし、実行しない。元の公開優先表・借用Jdbc proxy境界は維持。

| 通常範囲 | 結果 |
| --- | --- |
| BatchStepValues | 既8件全成功、日境界・null・値・並行・公開診断。 |
| BatchRunAuditPort | 既13件全成功、合成JDK Proxyのみ。固定SQL文字列、bind順・値、null、例外・close・履歴所有と境界。 |
| 静的History | 1件証明。動的21へ加算しない。 |

F/E/S・対象未実行0。最初のcompileは既許可のMaintenanceActivationを明示依存へ含めておらず終了1、JUnit未起動。現v2は明示依存を補い、Batch/Bootstrap/Storage正規JARの実使用type closureと、実DB/Driver・外部・保留なしを起動前に再確認した。

現同一exec八物理の生行371/374、method73/78、class8/8、branch221/243。Historyの診断と未測定条件を静的証明からcoverageへ置換しない。旧反射・coverageの合算、実DB等0。F03・P004-05の正式受入とYKT-2863は継続。

公開 `evidence/01_PT/018_NK-OPS-001/evidence/PG42930-batch-history-without-private-reflection-v2/manifest.json` SHA-256 `b9d93d678058e282f64335fe8ae5974b96f94a6c67e607a1b939dec3aaa8adf7`。原JUnit、対象CRC／hash、コマンドと漏れた分岐は元証跡へ追跡。
