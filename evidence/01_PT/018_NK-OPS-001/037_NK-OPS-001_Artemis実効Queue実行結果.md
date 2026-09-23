# NK-OPS-001 Artemis実効Queue PT実行結果

PG223、PT-OPS-MQ-001～004。2026-09-24 JST、JDK25.0.4/Maven3.9.12/Linux、`dev-foundation`未commit差分で選択4件は最終exit0、failed/error/skipped0。command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -q -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-batch -Dtest=ArtemisReadinessClientTest clean test jacoco:report`。実隔離Artemis/Coreで6組の実効Query、Queue欠落の拒否、独立属性変異、null/provider故障・借用資源・32並行を確認。選択runの対象2classはline/method/class/branch missed0。ただし他Batch classはこの選択runでは未実行。

正式source/run、全module4coverage・静的解析・41scope/hashは未実施であり、この選択試験のみを合格算入しない。journal load error、disk、ACL、address settings、閾値等のSS321 §13残件、Production credential/親起動/実NK CHR/IT/STは未完了。
