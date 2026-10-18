# 隔離PT用DBと原本DBの記述訂正（BUG1440/YKT1204）

近時1080～1090、共通handoff003022/023、456/460にある「実DB操作0」「実VM/DB/Backup操作0」は**原本・PGPT VMの業務DB/Backupへの操作0**を意味する。隔離PT用DBまで操作0という意味ではなく、この追補で区分を訂正する。元manifest・source・合否・期待・hashは改変しない。

共通選択のServiceProcessResourcesTest（7method）は@BeforeAllでApiLogDatabaseFixtureを生成する。fixtureは一時directory・loopback空きportのPostgreSQL18をinitdb/startし、DDL/Flyway・synthetic credential/データ/Hikari接続で試験し、@AfterAllでfast stopする。Production原本・VM DBへの接続ではない。関連bootstrapの42suiteにも隔離DBを使う試験があり、当選択の成功は隔離fixtureの実働を含む。ここはfake DB試験だけではない。実行済みPG5322と以前のrunは、開始manifestにbinary identity観測が無いのでversion/SHAの**当時値はnull/未証明**。現在binaryを読んだ結果で遡及補完しない。

2026-10-19現在の読取probeのみ：既設`work/characterization-tools/root/usr/lib/postgresql/18/bin/postgres --version`（同rootのlib/x86_64-linux-gnu、lib/postgresql/18/libをLD_LIBRARY_PATHへ指定）は`postgres (PostgreSQL) 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1)`、SHA256 **30a38e0516ec1bde4b8ca710cf28ba51ee78bd004cabbf3107e7a52d5414a64a**。新install・server起動0、入手元/既導入は421参照。

将来のpg5148開始manifestにpg5330.captureで設定PG binary version/SHA、ServiceProcessResourcesTest選択有無、originalOrVmDatabaseActions0/historicalRunQualification=falseを保存する。missing/non18/失敗/多行観測は拒否。独立二管理試験は固定SHA abc・失敗/欠落/偽version・historical非認定を確認、実サーバ起動せず成功。既公開pg5122系は旧元manifestをallowlist化するため再生成しない。旧公開物には本訂正を対応付け、次run以降の原開始証拠を独立postで参照する。source/runtime合否の変更0、Maven再演0、全対象の訂正/将来予防を満たして当文書工具範囲のみ完了。BUG1414全体は未完。
