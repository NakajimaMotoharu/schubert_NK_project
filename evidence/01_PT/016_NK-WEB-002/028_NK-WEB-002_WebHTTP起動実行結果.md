# NK-WEB-002 Web HTTP起動 PT実行結果

PG220、PT-SCR-109～112、QA-045/UIC-005/SSC-074。`dev-foundation`の実装中差分で、JDK25.0.4・Maven3.9.12・Linux上の実Tomcat11/Thymeleaf選択試験4件はPASS。`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -q -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node -pl src/schubert-nk-web -Dtest=WebHttpServerTest test`。Web module `verify`（同引数、`-Dtest`なし）は後述の静的解析修正後にexit0、Java line/method/class/branch coverage gate 100%、SpotBugs0。初回の選択試験は未実装時RED、初回module verifyは同期ロック静的解析2件でexit1であり、いずれも合格に算入しない。

正式全reactor run・41scope照合・保存manifest/hash・実NK CHR-A01/L01は未実施。正式run後に本欄へ対象commit、Test ID別実績、coverage、証跡path/hashを追記する。秘密値・raw tokenは保存しない。この部品はWeb HTTP compositionに限り、credential/DB/JMSのProduction結線・PGPT全体を完了としない。
