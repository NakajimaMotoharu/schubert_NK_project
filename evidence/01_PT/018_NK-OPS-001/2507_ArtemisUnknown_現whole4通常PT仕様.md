# 2507 ArtemisUnknown 現whole4通常PT仕様

SSC-461追補。既MQUNKNOWN003がメモリ内で `count` 直後の既知／未知失敗を用意し、`observe` と `purgeObserved` の二口で後続処理を拒否する。旧whole4を当sourceで再資格した。元fixtureは同一、実broker・実削除は実行対象外。PG40350〜354に対象source、コマンド、独立結果、部分coverageを保存した。

2026-10-29、PG-D819予定、source17ab52b25/normal13596/静的13599、save3b42b0c4031903aebd5f1e9900d82216dc9e4cbb/push26465真正0/remote一致。開始0.5/2/4pp cap10・fresh共有28残72/reset1793774153、主F03/canonical担当費WBS-P017-10参照のみ追加親予算0。全体正式/17-190/工数null/QA051final/実操作HOLD不変更。

## 着手前判定 PT_DEFAULT

既ArtemisUnknownBoundaryTest244行/全四method、Main Readiness89/Management324/AddressSettings125/Acceptor117/Role216/QueuePressure109/StartupObservation177/ExpiryPurge176と三例外/BatchRunの全body・初期化を確認。Testの全ClientSession/ClientMessageはthrow-only JDK Proxyで、Reader・Consumer・Function・Expiry Operationsは自分のlambda/カウンタ/fail-only。broker接続/credentialsを作らない。default管理readのqueryは新専用JVMの空ThreadLocal→checkParentDeadlineはownerなし→proxy.session.startが即throw、ClientRequestor生成やsession factoryに達しない。MaintenanceOwnerFrame.Guardは型参照だけでwithParentDeadline/owner methodを呼ばず、当held契約の別caller再演0。

ManagementHelper.putOperationInvocationの固定2.56.0 bytecodeは第1message.putStringPropertyでproxyがthrow、それ以降JSON/bodyも到達しない。static初期化は固定SimpleString定数だけ。doManagement/ServerLocatorは呼ばない。Expiryは明示Operations.countでthrow、bytes/selected/removeのfail sentinelは呼ばれない。六stage assemblyはmemory callbackだけ、既知Topology例外だけ固定Management例外へ変換。Throwable cause/suppressed graph探索/Root/API-Web Graph9へ到達0。実broker/queue作成/削除/Unit/VM/DB/原本Backup/鍵/native/permit操作0、既held wholeからのmethod抽出0。

旧1239/1922は型理由/責任資料で当current PT成功を推定しない。Test SHA0388f993…は8a518b253前70452dcd…から固定literal二定数・六使用を同値整理後で当whole未資格。normal13596の全sourceと固定依存Jarを再照合する。旧成功の確認再演/別source exec合算0。

NK-OPS-001/MQ001002009010・SYS004/OPS009、UI231/251/253、SS321/341/342/343、BUG381/YKT301。既PT-OPS-MQUNKNOWN001..004、SS343の未知は同一instanceで再送出し通常失敗へ正規化しない期待を固定する。

|Test ID|独立期待・正常/異常・境界|
|---|---|
|MQUNKNOWN001|同一IllegalStateException/NPE instanceを八read経路と四encoderからそのままthrow。session呼出しはaddressQueryとstartの二回だけとliteral2 assert。新NPEをcatchして正常業務化せず、未知を再送出する防御契約のTest入力。|
|MQUNKNOWN002|六各位置でunknownを投げ、後続callbackを実行せず同一instance、回数selected+1。既知Readiness例外はManagementへ変換し後続fail未到達。|
|MQUNKNOWN003|固定Run/cutoff・手組みObservation、fake countでunknownは同一NPE、既知providerはExpiry例外。observe/purge双方でremove/bytes等のfailが未到達。実purge権限や削除を試さない。|
|MQUNKNOWN004|同一AssertionErrorを管理readと四encoderが同一instanceで伝播、checked正常化へ落とさない。|

expectedは同一手組み例外object/assertSameとliteral回数・独立fail sentinel、Production出力からexpectedを生成0。新ID/JUnit method0。null category/unknown/fatal/knownの境界を対象、正常broker/実再送/実並行・許可発行は対象外/別未完program。新共有reporterはMap一箇所から4を導出し、工具自己fixtureはclasspathに入れない。

## 実行と測定

`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg13740_artemis_unknown_whole_four_pt.py`。新only SLOT、JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15、normal六jar/empty ENV。13742は元XML/全源/extra Java/Jar/元exec/単一session/CRCを独立確認し再実行0。完全ReadinessClient及び三例外の四source unitを測定し、missを保持する。他七client/ネスト/正常broker全体のcoverageを100としない。測定scopeを業務全体の合格へ変換せず、残coverageは明示する。既定filter以外の除外追加0、正式/全451へ加算0。
