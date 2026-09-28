# 216 NK-OPS-001 Morning DB能力継続・限定実行結果

2026-09-28 JST、branch `dev-foundation`、source/test/spec commit `fc09517407c475fe18b2595505accb567f1718a1`。対象Test IDと独立期待値は215。Linux host UID1000、JDK25.0.4、Maven3.9.12、Node24.19.0、JaCoCo0.8.15、SpotBugs4.10.4.0。

選択48PT（MNEW/MRESUME/MCTRL/MDB）を実行し、failure/error/skipped0、Batch SpotBugs BugInstance0、exit0。同一M/A/DB/File scopeでINVALID後も専用DB `Access`が使用でき、callback離脱後は使用拒否することを手書きevent・fake owner・実DB既存caseで確認。試験開発中の2回の不合格は新event oracleの後root再確認漏れと誤patch箇所によるもので、最終合格数に算入しない。

456にsecurity/transaction資源境界の全回帰triggerを事前記録し、同一sourceでProduction6の `clean test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check` を実行。Protocol80/17suite、Storage149/21、Bootstrap175/22、API742/123、Web555/85、Batch697/83、合計**2,398PT/351suite**、failure/error/skipped0、全6 SpotBugs BugInstance0、Maven exit0。原始logはGit外 `/tmp/pgpt-pg346-six-final.log`、SHA-256 `0a546d36c9e193d013112d8afab62f0502593fec772be6104e9aef3a9020f91d`。同run/sourceのsanitized JUnit351＋coverage2＋static6＝359 fileを `evidence/provisional/PG346-morning-db-capability/` へ保存、manifest SHA-256 `d0d9ac86e37ad4987894b6cd05a338244f43d772089fb01e92638ad21d6367c9`。全manifest path/hashをcollectorで照合し、秘密pattern scan0。JUnit properties/stdout/stderr/失敗payloadはGitへ保存しない。

4指標coverage missed（branch/line/method/class）はProtocol `0/0/0/0`、Storage `0/0/0/0`、Bootstrap `37/11/4/0`、API `1/19/3/0`、Web `1/19/3/0`、Batch `13/202/82/10`。変更本体はMCTRL `0/22/10/0`、MNEW `3/13/2/0`、MRESUME `1/5/1/0`、MDB `0/4/3/0`。native正経路・外部実Unitの未被覆を除外せず、全体4指標100% gateは不合格。

本PG346に新規障害はなし。関連BUG-315/YKT-248のhandleなしUNKNOWNとhard timeout後保全、YKT-250のcomplete/GC横展開、SSC-055/094/105の全親接続は継続。実backup worker、Cleanup/permit、外部Morning main、実VM、Web/API外部起動、実NK CHR-A01/L01は未達。正式認定source `858713c0bf310ae8bf62078b0a1cedbce4e968db`、run `PT-WEB-20260925-24`、1964PT/53scope、加重中心48.3%は据置。PG/PT・IT/ST完了を宣言しない。
