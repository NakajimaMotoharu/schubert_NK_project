# 1554 Test compiler 品質補完結果

2026-10-23、BUG1647/YKT1400、C02新harnessの前提品質。修正8480106c8で監視harnessのglobal compilerArgsへ-Xlint:all/-Werrorを明示。六Production/common POMは初めからglobal指定があり非該当、root default-compileのMain NullAway/lintは不変更。source reviewで発見し修正前起票済み。

原PG7034-test-lint-supplement-v1 manifest `83db051ddf5ad1d3a73101e15cd482247d6dee8e653964872dee46ea0e94f4c3`、actual0。path `evidence/provisional/PG7034-test-lint-supplement-v1/manifest.json`、元fixturePOM/source/開始/実process/終了/logは `work/pgpt-runs/PG379/pg7034-test-lint-supplement-v1`。旧/新harness設定から独立private POMを派生し、公開の意図的raw-type合成Test sourceをtest-compileした。旧実終了0（警告をgateしない）・新実終了1/「warnings found and -Werror specified」を確認。これは必要なcompiler負canaryであり、Production PT失敗でも2件のProduction合格でもない。実Test/Main実行0、原48/4222/common44の成功再演0。

既PG7030の六module正規Test compileはglobal lint/Werrorで真正0。そこに生成された監視packageの全7 Test physical classは、元48PTに使ったclassと全byte一致（compiler生成switch helperを含む）。7034が全class inventory/hashと元compile receiptを保存した。従って既Testに実際の警告がなかった品質根拠を、実行結果と混同せず補完できた。新source/runへ旧成功を改名せず、旧欠陥harness/raw結果は保持。

新deployment-unit-pomにも同global指定を適用し、C02の実五件compile/通常PTで横展開確認を完了するまではBUG/YKTをOPENのまま保持する。NPE/業務コード/Root実操作/全体451/正式1964-53/工数nullは変更しない。実command/Java25.0.4/Maven3.9.12/元POM/派生POM/fixture/hash/各expected実exitは原manifestへ保存。
