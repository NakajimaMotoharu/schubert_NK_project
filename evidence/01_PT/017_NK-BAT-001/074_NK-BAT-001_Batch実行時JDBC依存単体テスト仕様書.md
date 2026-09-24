# NK-BAT-001 Batch実行時JDBC依存 PT仕様

PG239/BUG-234/YKT-186。対象`src/schubert-nk-batch/pom.xml`と独立Batch processのruntime依存。関連RD OPS-001～012/SYS-004、UI251～253、SS311/341/342/343。PT-BAT-283の実装は`BatchRuntimeDependencyTest#bat283RuntimePostgresDriverAndScopeCanaries`。実Batch launcher/credential/DB loginは別gate。

| Test ID | 目的・事前条件/fixture・入力/操作 | 独立期待値と算出根拠 |
|---|---|---|
| PT-BAT-283 | 公開POMを読取り、PostgreSQL JDBC依存を検索。scopeをtest/compile/system/欠落、versionを旧値、宣言を重複/欠落へ一箇所変異して拒否を確認 | SS341/342はBatchを独立Java processとして扱う。PostgreSQL JDBC42.7.13を本番runtimeに1件だけ置く。test classpathやAPI runtimeからの偶然の継承は合格にしない。Maven `build-classpath -DincludeScope=runtime`のjar件数1を別途実測する |

正常/境界/異常はscope/version/宣言件数の正負変異で固定し、null/並行/再送はPOM定数の試験対象外（本PTの入力にnull・共有可変状態・broker操作なし）。`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-batch -Dtest=BatchRuntimeDependencyTest test`で選択PT、固定source全reactorとJava6 coverage/静的・全scope/hash/負canaryを正式判定する。OS/JDK/Maven/branch/commit/exit/実値/coverage/BUG・YKT・hashは075とmanifestへ記載。classpath全文・資格情報・DB URLは保存しない。
