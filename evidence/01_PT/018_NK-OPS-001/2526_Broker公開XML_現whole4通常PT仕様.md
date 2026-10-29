# 2526 Broker公開XML 現whole4通常PT仕様

2026-10-29、PG-D828予定、主F03/既source担当費参照C04/追加0。event2908で開始0.5/1/2cap10・fresh利用枠を凍結。normal13832/source0061d178c/静的13838を再利用し、元build/成功全回帰の確認再演0。現Testは13400のliteral整理後で当whole未資格、896/1524等の旧parse成功は歴史参照のまま保全する。

## PT_DEFAULTとscope

ArtemisBrokerConfigurationTest全242行と固定公開broker.xml全体を確認した。BeforeAllは一つの公開fileをFiles.newInputStreamで開き、固定Artemis2.56.0 FileConfigurationParser.parseMainConfigへ渡してTWRで閉じるだけ。ActiveMQ server/embedded brokerを構築・起動せず、接続/socket/JMS/実権限/queue操作/DB/VM/Root/native/credential/鍵を扱わない。XMLにDOCTYPE/ENTITY/置換property/外部include/broker connection extensionはない。CORE acceptor URIも設定文字列のparseだけ、実bindしない。vendor版とjarは元SDKhashに固定。旧C04の独立oracle/893以降の受入境界を引き継ぎ、実Broker接続/認証/IT性能の資格へ拡張しない。

入力 `src/deployment/artemis/etc/broker.xml` SHA161cbc5fc57ae38e4d75f45e8c752a781732aa3bf6c93c6d7ce8eb1cdaae1820、Test SHA8f3158a7b9ffe84312e4ac902e3d850ae9963b270302818fc737f1e6c1dfe1d9。broker.templateはnew own JVMのlauncherでnormal13832の凍結公開snapshotへ固定し、前後byteと元source全inputを照合する。実環境のconfigを読まない。全wholeを実行し、実embedded/maintenance系HOLDの一部を抽出しない。

RD MQ001..013/040..045・UI231・SS321§2～5/10・QA041042/SSC075076、NK-MSG001/NK-OPS001/C04。896の一意alias PT-CFG3390-A～D（下記class#method）を継承、新Test ID0。

|Test ID/既method|独立期待（SS literalから転記、Production値でexpected生成0）|
|---|---|
|A/globalBrokerAndJournalSettingsMatchTheIndependentOracle|NIO/persist/datasync/24global、global512MiB/50000、graceful60秒、journal10MiB/min4/pool20/compact30%/10、disk90%/5秒、ID20000。|
|B/topologyAndTransportAreClosedToTheApprovedSet|六Address/Queueの閉集合・ANYCAST/durable、CORE acceptor一つ127.0.0.1:61616。追加/欠落は集合完全一致で拒否。|
|C/addressPoliciesMatchTheIndependentCapacityMatrix|六×26policyの容量matrix、DLQ/Expiry、再送1000ms/倍率5/上限30000ms/4回、PAGE/BLOCK/FAIL、auto作成削除false、metrics/timestamp true。|
|D/securityRolesMatchTheIndependentAclMatrix|十三ACLのrole/permissionの完全集合・未列挙権限なし、durable queue create/delete false、management RBAC prefix mops。これはdata matrixで実認証/権限変更ではない。|

対象はnon-executable XML一artifact、Java/JS counterはN/Aであり、Mainを除外して100にしない。null/未知/不正XMLnegativeは896の既schema/oracle別scope参照、今回は変更されたTest whole4の現資格確認だけで旧negativeを新source実施へ算入0。新negative/再送・並行・実動作は本群で実施しないと明示する。

実command=`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg13862_broker_config_whole_four_pt.py`、JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15・固定六jar/SDK・empty ENV/config、13864で原XML/全源/Jar/固定XML・空fixture map・一exec/session/metadata反例を独立照合する。終了/実際値/実時刻/branch/HEAD/hashと範囲外は2527/専用manifestへ保存する。新受入・正式1964/53・17/190・工数null・QA051final・全actualHOLDを維持し、普通区切りでは止めない。
