# NK-WEB-002 Web起動前資源複合実行結果

2026-09-25 BUG-250修正前RED: PT-SCR-136/137を含むWebDependencyReadinessTest選択6件、2 failure/0 error/0 skipped、exit1。DB/JMS両方で通常検査失敗＋所有close fatalを公開proxyから独立注入し、期待元Error identity、実`WebStartupException`を再現。初回選択試行はtest switch式の構文誤りによるコンパイル失敗でPT結果へ算入しない。915へ修正前起票、YKT-154へ紐付け。`evidence/output/BUG-250-red.txt`は秘密・raw stackなしの要約。正式全reactor/coverage/manifest/hash未実施で不認定。
