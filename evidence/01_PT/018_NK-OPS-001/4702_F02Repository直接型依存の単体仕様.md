# F02 API Repositoryの直接型依存

NK-OPS-001／PG-D516／WBS-F02-a。RD SYS-011、UI211・241、SS311 §3・§10、SS352。BUG-3390／YKT-2724。対象は ModuleDependencyAudit の Repository 分類と直接依存。実行元の canonical SS311 と tool／fixture SHA は manifest に記録する。

| Test ID | 手書き入力 | 独立期待値 |
|---|---|---|
| PT-F02-REPO-TYPE-001 | persistenceの公開field | Repositoryからapplication.TypedService 1辺 |
| PT-F02-REPO-TYPE-002 | 戻り値に上位型を持つRepository | 同1辺 |
| PT-F02-REPO-TYPE-003 | 引数に上位型を持つRepository | 同1辺 |
| PT-F02-REPO-TYPE-004 | Listの型引数だけに上位型を持つRepository | 同1辺 |
| PT-F02-REPO-TYPE-005 | 二次元配列に上位型を持つRepository | 要素型へ正規化した同1辺 |
| PT-F02-REPO-TYPE-006 | throwsに上位例外を持つRepository | application.TypedFailure 1辺 |
| PT-F02-REPO-TYPE-007 | monitoring.persistenceのconstructor引数に上位型 | application.TypedService 1辺 |
| PT-F02-REPO-TYPE-008 | 上位型のstatic method直接呼出し | 同1辺 |
| PT-F02-REPO-TYPE-009 | 通常の非Repositoryに同じfield | 当規則の指摘0 |
| PT-F02-REPO-TYPE-010 | Repositoryに下位domain型のfield | 当規則の指摘0 |

JDK 25と既定ArchUnit。fixtureのみを六ordinary jarへ収める。厳密集合比較を行い、元8禁止のうち実際に出た種類と許容2を独立算出する。負例を含むため実audit終了期待1、fixture判定終了は期待一致で0。固定source、compile終了、全物理数と取込数、入力・出力hash、元の55対照との一致をmanifestへ保存する。製品class、業務データ、サービスを起動しない。当証跡は製品PTとcoverageに加算しない。

実行はリポジトリルートで `python3 -B evidence/01_PT/018_NK-OPS-001/input/5384_f02_repository_type_dependencies.py before|after`。PG40584／PG40586。nullと例外はfixtureの型宣言範囲のみを対象とし、並行や再送は対象の直接型依存規則を変えない。
