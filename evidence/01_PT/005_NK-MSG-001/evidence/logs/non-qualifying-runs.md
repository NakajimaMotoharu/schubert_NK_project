# NK-MSG-001 非適格run

次のscan試行は検査script自体のoracle不備でexit 1となったため、PT-JMS-012のPASSへ算入しない。Production code、broker設定、JUnit結果は変更していない。

| 試行 | 非適格理由 | 処置 |
|---|---|---|
| scan-01 | `rg`が先頭`-----`のpatternをoptionと解釈し、NUL検査もtext mode契約に不適合 | pattern終端を明示し、NULをPerlのbyte scanへ変更 |
| scan-02 | shell quoteを含むcredential patternが分割され、`rg`がpattern断片をfile名と解釈 | quoteを含まない同等のcredential assignment patternへ変更 |
| scan-03 | SpotBugs正常出力の空要素`<Error></Error>`をerror有りと誤判定 | `BugInstance`または非空`Error`だけを不合格とするoracleへ変更 |

合格runは`PT-JMS-20260904-01`であり、`secret-scan.txt`のexit code 0と全counter 0を正本とする。
