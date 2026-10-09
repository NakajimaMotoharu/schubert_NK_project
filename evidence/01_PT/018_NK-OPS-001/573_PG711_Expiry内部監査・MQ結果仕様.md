# PG711 Expiry内部監査/MQ結果の独立PT

NK-BAT-001/OPS009/DAT009/UI251/SS341§9/343/354/SSC111119、PG-D404/WBS-P017-08着手前費.5/1.5/3.5pp。旧current9bd/PG682は保全、新候補main CleanupExpiryExecutionだけと内部抽象port/固定native匿名adapterが変更される。coreはpackage-private借用DB/MQ結果のtransaction処理だけ、実context/credential/locator/sessionstart-close/ゼロ化/元deadline/publicentryを元defaultに残す。新公開admission/override/緩和/除外0。候補hostと旧nativeをmainbyte資格なしで合算しない。

PT-OPS-EXP711001～011：成功0/実purge失敗WARNING10 afterNULL/健康critical又はdeclared failureFAILED30/欠落4依存を操作前拒否/owner期限切れ初期・purge直後/未知例外透過/同day既存SKIP正常・criticalとpurge0/独立stage-column又はterminal-column drift拒否。実isolatedPG18.6/DDL/Flyway/ROLEschubert_batch/advisory71419602、固有run711…/固定cutoff2026-09-30T00Z/started01Z/ended02Z、独立MQ観測before3/選択2/byte300推定200/実削除2-after1。cutoff9/23epoch1790121600000はOSdateで独立確認、期待はliteralSQL status・counts・after NULL・reason・列値、Productionmethodで生成0。

正常ではstage commitを別adminconnectionからpurge時に確認、health後にterminal commit/readbackして初めて0/10/30。Guardは合成データ契約だけでnative所有を認定しない。異常でもborrowed connectionをcoreが閉じず、callerのtry-closeとfixture停止が責務、未知はRUNNING stage保持しterminal捏造0。二driftはhost隔離DBだけの単一列故障注入、VM/currentへ書込0・DDL変更0。skipは二全原値JSON不変、実session/Root原本別保全。

command `python3 -B tools/quality/vm/050_s1/pg711_selected.py`、JDK25.0.4/Maven3.9.12/offlineM2/spotless/静的/coverage。新onlyW/pg711-expiry-core-v1でExpiryResultContractTest、CleanupExpiryExecutionTest、ExpiryOwnerTestの三suite、実source/exit/XML/FES/hash/未変更5module・batch変更1outer追加2innerを独立collectorへ照合。旧exec/reports/static保全、現在未実行・全体回帰/新candidate署名配備/native/工程正式未受入。未検証候補を旧正式PT24/1964/53へ加算0。
