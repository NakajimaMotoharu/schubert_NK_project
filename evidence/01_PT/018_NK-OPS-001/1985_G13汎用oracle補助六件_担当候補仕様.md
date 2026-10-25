# G13汎用oracle補助六件・担当候補仕様

2026-10-26/群2238/主作業G13.07、開始.5/2/5pp cap10保持。PG-D673。source8ba82083、現在1795path/登録1787/未確定8。先行1935と1936/1937・現在source同byteを確認し、既23methodの対応/既成功JDK読取は再演しない。新成果は、Production型を持たない6補助自身のoracle保守担当候補を明示すること。

|既存補助（src以下の完全pathは後続manifest）|独立oracle補助の責務|consumer既担当（全て保持・再配賦0）|
|---|---|---|
|api/application/admin/UserCommandFaults|public Connection/Statement/ResultSetの決定的fault/列置換/更新前hook|P01001/P01002|
|api/application/log/LogJdbcFaults|同上、typed getObject/wasNull/空・重複行の観測|P00601/P01004|
|api/persistence/UserQueryFaults|public JDBC故障・列/行境界/close件数・禁止projectionの独立assertion|P01001/P01004|
|batch/cleanup/ServiceJdbcProbe|public JDBC/TX/cleanup段階のfault/順序・回数/owner check観測|P01707/P01712|
|bootstrap/api/maintenance/MaintenanceJdbcProbe|public borrowed JDBCの故障/close・commit・savepoint・row観測|P00402/P00404/P01901|
|bootstrap/CallerMonitorProbe|caller monitor保持中の独立帰還・worker例外/有限joinのoracle|P01706/P01803/P01804/P01806|

この六exact pathだけをWBS-G03の主担当/costOwner候補とする（NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED）。業務PGの代行ではなく補助自身の独立oracle保守責任。consumer数や多数決、旧changeOwnerを根拠にしない。原941 logicalがあれば原owner/costが常に優先する。六sourceが@Test/Production importを持たないこと、全project内同名typeの一意性、consumerの同package又は明示完全名と既canonical owner/source hashを確認し、関連担当を全て保持する。actualAllocatedPp=null/additionalSharedCostPp0、元費用の配替え0。

BorrowedJdbcFatal329Test/TargetBusinessControllerTestは業務Mainを直接呼ぶ横断Testであり対象外、file primaryをUNKNOWNのまま保持。1937の23method/26family/34関係を新規trace成果や実PTへ再計上しない。8source全てが旧64446と現8baで同byteであることをGit sourceで確認済み、反射/JDBC/DB/Thread/target compile-load-init/JUnit/probe/HTTP/VM/Root/鍵/permit/intent等実行0。既補助の安全な実行許可を新たに認定する作業ではない。

受入は六exact proposal/原logical優先/近傍・別path・二横断Testの不受理、全consumer/原owner保持、旧962row・原941943/予算/受入不変、同sourceの6補助候補だけ追加したregistryと独立postまで。目標は登録1793/1795・未確定2であり、G03/G13/全WBS/正式受入の完了ではない。Source/Production/Main/Test/上位仕様変更0、追加品質/計測/工具と元計画消化を分離する。新たな品質工具自身のunittestは製品PTへ加算しない。
