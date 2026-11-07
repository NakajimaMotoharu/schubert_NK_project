# API/Webプール借用source・通常PT仕様書

Program NK-OPS-001/NK-DAT-001、ApiJdbcPool.open/WebJdbcPool.open、WBS source owner P00405/P01806（共有群費は一回だけ、専有配賦不明null）。RD SYS002004/DAT001/AUT002/UI212226253/SS311342343/PG271/411/451。元実PostgreSQL正常・権限・容量試験はHOLDのまま、原Test/DBfixtureをcompile/runしない。SDK受動審査23278/80/84・80class/15method・明示CP no Driver/logger providerに基づく別の既設DataSource境界PT。

OPS-POOL-OWN-001=APIの8max/2min・接続3000/validation2000/failfast1・autoCommit true/readOnly false/MBeans false・固定名を独立SS literalで確認し、同じcaller-owned memory DataSourceを二つの逐次poolが借用してもsource.closeを呼ばないこと、各poolだけが発行memory Connection/SDK workerを終了すること。nullはpool取得前に拒否。
OPS-POOL-OWN-002=Webの2max/1min・同timeout/flags・固定名について同契約、両module間の依存追加なし。

PT_DEFAULT予定：新各module一class（private memory source/Connection API proxy）だけcompile。normal22084 API/Web jar・Hikari7.1.0/slf4j-api2.0.18/JSpecify/JUnit1.13.4、driver・broker・DBfixture・logging provider・modulepath・plugins・外部javaoptions無し。元source7aed同byte、Main/config/SDKは変更・抽出なし。JDBC interface callbacksはmemory状態/既定属性/closeのみ、SQL/metadata/driver/network・実DataSource/role/readiness・VM/Root/native・四held初期化0。

各caseで hikaricp.configurationFile/slf4j.provider が無いことを値非表示booleanで先に確認。Hikari internal UUID用JDK既定SUN entropy・classpath/property readはSDK活動でありsyscall0とはしない。診断UUID/実credential/sessionを記録しない。SLF4J NOPを静的CPで確定、rawSQL/password無し。callbackは非blocking/型nonnull契約、shared状態Atomic/ConcurrentMap、未定義methodは固定messageのAssertionError。

pool/loanはTWRで逆順close。既SDK shutdownNow≠終了のため、sourceで固定したpool名・当isolated Unit JVMのSDK workerだけを観測し、stack内容を保存せず10秒同期限でjoin/生存0を独立後条件にする。guest/Linux process/Unitの状態証明とはしない。全issued memoryConnectionがclosed、borrowed DataSourceのclose0を確認後、fixture所有者がsourceを一回closeする。各Test45秒・whole owned tool180秒。中断/未終端は失敗又は未確認であり合格にしない。

期待値=SS311/342のAPI/Web各設定literalとcallee/caller所有契約、Production methodでexpected生成0。全固定source・新二件/FESabort0/XML・Main SourceFile/normalCRC/一exec-session・Code四counter（元branch0はN/Aを明示、100と捏造しない）・staticMain六零の再利用＋新Test PMD/CS・実initを独立postへ。既Test成功の再確認実行/old exec合算/実DB/backend/正式451受入へ転用0。

原見積1/3/7pp cap9。開始451unique/暫定93/partial18/原282交差73・残209を保持、二sourceの旧全名簿未整備を理由にnewSource加算を先取りしない。全体正式1964PT/53scope/新leaf0/工数null。source固定commit前はUnitを起動せず、true endを回収して原証拠へ記録後も477に従い継続。
