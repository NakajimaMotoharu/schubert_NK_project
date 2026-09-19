# NK-OPS-001 PostgreSQL配備設定実行結果

PG187/SSC069、033・PGCFG001～008。選択8PT成功、正式全reactor前。新8PT/OPS1部分成果は未加算。

初回redは02:51:37/1.496秒/exit1、upstream Protocolで選択test無しにより停止、API未実行。failIfNoTestsを緩和せずFieldCodecTest/ResourceScopeTestを選択へ追加。SHA256 c17589009411109fe96bde636157257f7336f17c1ec19cddce2b1982227ba020。

red2は02:52:11/12.787秒/exit1、8PT中2failure。BUG208: web_session statement_timeoutがNULL（期待1500ms）。BUG209: native wal_compression pglzに設定表記onを期待したoracle誤り。SHA256 802e35562c560b50139856165efa0614d9d22678c79599cbcd04532754d2885c。

greenは02:53:22/14.412秒/exit1、8PT中1failure。6role18timeout修正後PGCFG005成功、native log_connectionsのstring onを意味上の展開listと誤認したBUG209横展開。SHA256 8819c3e754302d9c6ea1233bc5add8875fd004d9e507e8b50e42070010f0fd6c。

green2は2026-09-20 02:54:07 JST/13.829秒/exit0、PGCFG8PT全成功、failed/error/skipped0、依存module選択も成功。全32設定native値、HBA16規則・native catalog、role20timeout、異常設定・HBAと原状復元を確認。SHA256 3fa43bcc3ed006309cff69be1ef6002392b32cc33f59f94cf85d7472b2dbbfea。source b9eb74cc/d7a16e17＋当変更、dev-foundation。

command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am spotless:apply test -Dtest=FieldCodecTest,ResourceScopeTest,PostgresDeploymentTest`。Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12/PG18.6/JDBC42.7.13/Flyway13.4.0。tool追加なし。

選択試験は全coverage認定に使用しない。正式source固定・全clean verify/全静的解析/38scope/負canaryとmanifest収集後にBUG208/209・YKT164/165・SSC069を判定する。証跡は公開設定/native成功metadata・sanitized JUnitのみ、raw DB log/credential/DB dumpなし。actual host/認証通信/全secret gate/IT/ST未完了。
