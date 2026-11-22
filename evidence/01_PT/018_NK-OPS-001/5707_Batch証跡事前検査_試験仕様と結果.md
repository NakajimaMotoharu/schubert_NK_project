# Batch証跡事前検査の試験仕様と結果

NK-OPS-001、WBS-G08、SS354、451 §1、BUG-3605/3606、YKT-2836。対象は018 `collect` と020 `read_batch_reports` / `--preflight`。旧認定profileのBatch JUnit総数550、既suite／Test ID、正式53 scopeは既契約に従う。先行検査はXMLと目録だけを読み、別候補の書込を始める前に入力不一致を検知する。

| Test ID | 操作 | 独立期待値と結果 |
|---|---|---|
| PT-OPS-G08-PF001 | 一時領域へ550 testcaseのXMLを用意。件数属性、失敗・エラー・skip、rerun、欠落を変える | 549/過大/不整合と非成功を拒否。正常型は次のsuite/方法照合へ渡る |
| PT-OPS-G08-PF002 | 正式収集の呼出境界を代替実行で観測し、最初から53呼出の各箇所で終了異常を返す | 020 `--preflight` が先頭。失敗した呼出の次は起動しない。先頭失敗時にwriter呼出0 |
| PT-OPS-G08-PF003 | 実CLIを自己所有の一時ディレクトリから実行。別sourceの履歴件数を独立した1,466 testcase合成XMLで与える | 旧profileを変更せず終了1、元一ファイルのSHA-256一致、出力増加0 |

7工具test成功と証跡PG42714を確認。PG6930の別source 4,222件中Batch 1,466件／205 suiteは版差の根拠。現候補の目録の確定・全体正式実行・他のscope失敗時の格納条件は継続する。実サービス、Batch本体、製品試験の追加実行0。
