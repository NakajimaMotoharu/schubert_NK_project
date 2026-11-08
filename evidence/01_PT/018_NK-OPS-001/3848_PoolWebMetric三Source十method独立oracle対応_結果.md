# Pool/WebMetric三Source十method独立oracle対応 結果

仕様3847/scope637。Main7aed不変更、元23312二case/23396選択21は確認再演0。PG24102公開Source/metadata確認exit0、10method・23固有case・59assertion snippetを現23972/Source別23982/承認SS342343351へ対応。

|Source|method|固有の元Test ID|独立期待の範囲|
|---|---|---|---|
|ApiJdbcPool|<init> ()V|OPS-POOL-OWN-001|public stateless factory construction|
|ApiJdbcPool|open (Ljavax/sql/DataSource;)Lcom/zaxxer/hikari/HikariDataSource;|OPS-POOL-OWN-001|null/explicit limits/fail-fast, pool-owned connections close while caller DataSource retained|
|WebJdbcPool|<init> ()V|OPS-POOL-OWN-002|public stateless factory construction|
|WebJdbcPool|open (Ljavax/sql/DataSource;)Lcom/zaxxer/hikari/HikariDataSource;|OPS-POOL-OWN-002|null/explicit limits/fail-fast, pool-owned connections close while caller DataSource retained|
|WebServiceMetricBinding|prepareContext (Ljava/lang/String;Ljava/util/function/Supplier;Ljava/util/function/Supplier;Ljava/lang/Runnable;)Ldev/codex/schubert/nk/web/monitoring/WebMetricContext;|WEBSERVICE002,WEBSERVICE003,WEBSERVICE004,WEBSERVICE007,WEBSERVICE008,WEBSERVICE010,WEBSERVICE011,WEBSERVICE012,WEBSERVICE013,WEBSERVICE021|resource-free ownership capture and lazy suppliers|
|WebServiceMetricBinding|<init> (Lcom/zaxxer/hikari/HikariPoolMXBean;Lcom/zaxxer/hikari/HikariConfigMXBean;Lio/micrometer/core/instrument/MeterRegistry;Ljava/lang/String;Ljava/lang/Runnable;)V|WEBSERVICE001,WEBSERVICE004,WEBSERVICE005,WEBSERVICE006,WEBSERVICE007,WEBSERVICE008,WEBSERVICE012,WEBSERVICE013,WEBSERVICE014,WEBSERVICE015,WEBSERVICE016,WEBSERVICE017,WEBSERVICE018,WEBSERVICE019,WEBSERVICE020,WEBSERVICE021,WEBSERVICE022|borrowed DB metadata/retained recorder and terminal invariants|
|WebServiceMetricBinding|refresh ()V|WEBSERVICE004,WEBSERVICE005,WEBSERVICE006,WEBSERVICE007,WEBSERVICE008,WEBSERVICE012,WEBSERVICE014,WEBSERVICE021|read-only DB observation only; no HTTP success replay|
|WebServiceMetricBinding|createHttpObserver ()Ldev/codex/schubert/nk/web/monitoring/HttpMetricValve;|WEBSERVICE005,WEBSERVICE006,WEBSERVICE007,WEBSERVICE008,WEBSERVICE012,WEBSERVICE013,WEBSERVICE015,WEBSERVICE016,WEBSERVICE019,WEBSERVICE021|fresh pipeline-owned observer sharing recorder|
|WebServiceMetricBinding|withHttpObserver (Ljava/util/Map;)Ljava/util/Map;|WEBSERVICE015,WEBSERVICE016,WEBSERVICE017,WEBSERVICE018,WEBSERVICE019,WEBSERVICE020,WEBSERVICE021,WEBSERVICE022|structural immutable typed copy; reject null/type/duplicate/existing observer/provider failures|
|WebServiceMetricBinding|lambda$prepareContext$0 (Ljava/util/function/Supplier;Ljava/util/function/Supplier;Ljava/lang/String;Ljava/lang/Runnable;Lio/micrometer/core/instrument/MeterRegistry;)Ldev/codex/schubert/nk/web/monitoring/WebServiceMetricBinding;|WEBSERVICE004,WEBSERVICE007,WEBSERVICE008,WEBSERVICE010,WEBSERVICE011,WEBSERVICE012,WEBSERVICE013,WEBSERVICE021|ordered lazy pool/config acquisition and original failures|

ApiPoolはOPS-POOL-OWN001のみ、WebPoolは002のみへ対応。元二case全体を両プログラムへ二重計上せず、2Source/4methodと固有二caseを区別。API8/2・Web2/1、connection3000/validation2000/init1、二世代のpool/返却connection/owned worker終端と借用DataSource非close、null返却sourceのconstructor失敗を元証拠から追跡した。

WebMetricはWEBSERVICE001～008/010～022の21だけ。factoryはsupplier取得前ownerを返し、STANDARDは詳細取得0、DEBUGは順序とgetter render・250ms独立値、terminal重複/別request・有限並行、原Error/Runtime identity、immutable dependency copy/null/type/primitive/duplicate/provider失敗を明示。009はNOT_EXECUTED_HOLDのまま、全22未受入。WebDbPoolMetricObservationTestは補助Fixture compile-onlyで0case、この21へ加算していない。

元のSDK内部thread/GC/management/unstarted Tomcat metadataやown registry活動は実DB/HTTP/native/Rootではない。今回SDK callbackすら実行0、compile/JVM/Unit/backend0。四counterは元run-levelのSource別で、caseごとのprobe測定や全callee/451受入へ転用0。source/class SHA・descriptor/独立期待/Test ID・case/SS正本pin/未観測はmethod-oracle-relations.json参照。

新BUG0、unique517/候補114/pending12/whole93/正式1964PT53scope/newleaf0/工数null/G07未分類3313+22actualSecretCountnull/全HOLD維持。当12Source対象は10Source/46元測定methodまで明示対応、残2Source/21method。PGPT全体の完成率ではない。

command python3 -B evidence/01_PT/018_NK-OPS-001/input/639_pool_webmetric_method_oracle_review.py、日時 2026-11-08T16:13:49.293548+09:00、manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG24102-pool-webmetric-ten-method-review-v1/manifest.json` SHA256 `dbb227600dfdb745d02c52a6b3ffc3e961149a6ecdc41e2cd0f08330a9cff978`。Source固定/pushはPG24104 publisher参照。
