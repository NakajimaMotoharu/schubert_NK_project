# DBプール借用source・SDK適用審査仕様

Program NK-OPS-001/NK-DAT-001、ApiJdbcPool/WebJdbcPool.openの既設DataSource境界、RD SYS002004/DAT001、UI212253/226、SS311/342343・PG271。原ApiJdbcPoolTest/WebJdbcPoolTestはBeforeAllでPostgreSQL・原DBfixture・role権限queryを使うため実行しない。一般の「POOL」という名称から実行免除を広げず、今回も実DB/role/socket/admission/VM/Root/native/driver/四heldclass実初期化はHOLD。

予定=Main source/pomのHikari7.1.0現jarを固定し、受動javapでHikariDataSource/HikariPool/PoolBase/PoolEntry/UtilityElf/ConcurrentBag等の実呼出・静的初期化・thread/close経路を確認する。実JavaProduct初期化・DataSource.getConnection/provider/SQLはこの審査では呼ばない。SDKのpassive compiler/tool JVMだけ許可。jar/normalSource/pom/currentMain input hash、command/exit・stdout hash/呼出根拠を保存する。

検討する独立通常PTは既設DataSource interfaceへ自己所有のmemory-only Connectionを供給し、初期化を含む実Hikariの借用source非close・そのpoolのconnection/worker解放を確認するもの。元実PostgreSQL正常/権限/容量試験のfixture置換・再演としては扱わず、actual DB readiness/role/正式451へ換算しない。安全な完全graph/所有・cleanup/SDK logger classpathが明示できた後だけ別のPT着手判定・source固定を行い、未証明の段階ではPool.openも原/新Testも実行しない。

OPS-POOL-SDK-001=現pom7.1.0/jar pin/通常Main同hashとdefaultsource分岐、002=provided DataSourceから実driver/socket/provider経路へ逸脱しない条件、003=JVM内所有thread/Connectionの取得・失敗・終了/borrowed DataSource寿命、004=新独立Unitの限定可否と未証明事項。判定不能はHOLD、SDK review完了をPT-PASS/coverage/source資格/全体完了へ加算0。

見積0.5/2/5pp cap7、追加F03適用審査。451unique(Java347+HTML97+CSS7)、暫定source93/原282交差73rem209・partial18rem62、pending Address/Role差分null、正式1964PT/53scope/新leaf0/工数null・全HOLD維持。元source/runs/stash原本保持、保護二Test二tool IO0。実環境稼働を推測せず、通常区切りでは停止しない。
