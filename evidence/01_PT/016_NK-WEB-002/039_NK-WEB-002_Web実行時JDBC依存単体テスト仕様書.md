# NK-WEB-002 Web実行時JDBC依存 PT仕様

PG238/BUG-233/YKT-186。対象 `src/schubert-nk-web/pom.xml`のPostgreSQL JDBC runtime dependencyとWeb単独実行classpath。関連RD AUT-002・DAT-001・SYS-004、UI212/225/251、SS311/313/342 §4/343 §5.2/6。実JDBC credential/DB接続は別PT・実NK gate。

| Test ID | 事前条件・入力/操作 | 独立期待値 |
|---|---|---|
| PT-SCR-132 | Web module POMをXMLとして解析し、`org.postgresql:postgresql`のscope/version/重複を検査。test/compile/system/missing/重複scopeへ1項目変異 | SS342のWeb独立processと343の技術DB接続に必要なPostgreSQL JDBC 42.7.13はproduction `runtime` scopeで1件だけ。test-onlyへの退行、scope欠落、二重宣言は拒否。Web test classpathに存在するだけでは合格にしない |

加えてMaven3.9.12の `org.apache.maven.plugins:maven-dependency-plugin:3.9.0:build-classpath -DincludeScope=runtime` で生成したWeb runtime classpathへ `postgresql-42.7.13.jar`が1件含まれることを独立実測し、同条件のAPI/Batch/CHRをYKT-186で横展開分類する。PT command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-web -Dtest=WebRuntimeDependencyTest test`。固定sourceの全reactor、Web Java 4coverage、NullAway/SpotBugs0、全scope/hash/負canaryを後続gateで確認。POMに秘密値を置かず、classpath全文・credential・DB URLは証跡へ保存しない。日時、OS/JDK/Maven、branch/commit、input/独立期待値/actual、exit、BUG/YKT、evidence path/hashを040とmanifestへ記録。実Web main/credential/DB/JMS起動やCHR-L01は本testの合格に算入しない。
