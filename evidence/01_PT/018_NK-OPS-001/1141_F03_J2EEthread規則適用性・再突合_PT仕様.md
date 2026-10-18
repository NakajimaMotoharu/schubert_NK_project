# F03 DoNotUseThreads 適用性確認（PG5554、PG-D435）

Source a19、PMD7.28.0実installed jar/rule XML、承認origin/main SS311/343、411/451を正とする。raw baselineはPG5506/bf739a63（Source296）で変更しない。fresh PG5550の固定source/targetへ書込み0、VM/DB/Unit操作0。

- F03-CTX001: rule名が一意、実message/descriptionがJ2EE管理前提を明示、jar/entry/単独rule hashとpriority3を保存。前提の異なる一般Thread安全性ruleを同じ処分にしない。
- F03-CTX002: 全六artifactをJAR/正規module IDで照合、API/Web/Morning own entryと実systemd launcher、origin/main承認designの固定hash、MainのManagedExecutor/EJB等不使用を確認。JARだけの判定を禁止し、WAR/EJB/ManagedExecutor/foreignartifactの独立否定fixtureを必須にする。Spring Servlet使用とJ2EE-managed executor契約を分ける。
- F03-CTX003: 原239行すべてにfindingId/現sourceSHA/妥当span/sourceSpanSHAを一意に結合、全239Raw warningを残す。旧13reviewを現Source全レビューへ複写しない。除外glob/抑制/priority変更0、thread safety/ownership/全coverage/F03/正式合格0。
- F03-CTX004: 当Source fresh六Jar/source診断が完了した後にのみ、新rawの同rule行集合とrulehash/sourceSHA/path/span等を厳密再突合。行欠落/追加/変異を数の一致だけで通さず原因分類する。元239の前提レビューを当新診断実行の代用にしない。

独立fixture二（正規jar/foreign/war/ejb/ManagedExecutor拒否＋実rule/六module/三own Unit/三entry）が成功、actualレビュー出力は未生成。実command `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg5554_thread_rule_applicability.py`。原raw/evidenceは保持、safe JSON以外を公開せず実結果/hashを1142へ追補する。群1282 .5/1/3pp固定、旧計画額や239件を工数完成率へ変換0。
