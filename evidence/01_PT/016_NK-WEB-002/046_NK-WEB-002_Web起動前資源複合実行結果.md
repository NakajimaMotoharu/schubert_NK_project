# NK-WEB-002 Web起動前資源複合実行結果

2026-09-25 BUG-250修正前RED: PT-SCR-136/137を含むWebDependencyReadinessTest選択6件、2 failure/0 error/0 skipped、exit1。DB/JMS両方で通常検査失敗＋所有close fatalを公開proxyから独立注入し、期待元Error identity、実`WebStartupException`を再現。初回選択試行はtest switch式の構文誤りによるコンパイル失敗でPT結果へ算入しない。915へ修正前起票、YKT-154へ紐付け。`evidence/output/BUG-250-red.txt`は秘密・raw stackなしの要約。正式全reactor/coverage/manifest/hash未実施で不認定。

2026-09-25 PG270暫定GREEN: DB/JMSの所有closeを各々明示分離し、通常＋fatal/通常＋通常/fatal＋fatalをPT-SCR-136/137で追加。選択`WebDependencyReadinessTest` 6/6、failure/error/skipped0。最初のWeb全532件は全試験成功したが追加branch4未網羅でcoverage gate exit1のため不認定。組合せ追加後のWeb全532件はfailure/error/skipped0・対象class instruction104/104、branch14/14、line34/34、method2/2、class1/1、SpotBugs0で合格。正式全reactor/53scope/hash待ち。実NK CHR-A01/L01/全process起動は未実施。
