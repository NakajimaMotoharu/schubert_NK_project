# API同期consumerの契約準備・既存event証拠の適用範囲

Production Main236ffddc83、origin/main42450b515bのSS312/321を正本として、[PG26574](evidence/PG26574-api-consumer-contract-and-event-applicability-v1/manifest.json)にowned22全sourceのhash、本文契約、TestID候補、既知の未確認事項を保存した。WBS-P005-03/1はこの対応表の準備完了のみ。/2の同source受入は未完。

| 対象 | 独立した期待・資源後条件 | 既存候補／未確認 |
|---|---|---|
| ApiSyncRequestDispatcher | SS323固定31要求の不変登録、null/未知handlerの拒否。process-readyとは別 | PT-JMS-DISPATCH-026、Temporary実class依存HOLD、whole oracle再確認未完 |
| ApiBrokerContexts | 固定3profile、password copy消去、owned factory逆順close/UNKNOWN保持 | PT-JMS024/FACT334、実credential/factory/Temporary HOLD |
| ApiMessagingRuntime／SyncRequestConsumers | 完全3group・4独立sync context、delivery別rollback qualification、fatal一回、全admission停止後close | PT-JMS016/013/RB319、Temporary・実owner HOLD。PGの本文点検済み、PT PASSは主張しない |
| Guard／Guarded | bounded bodyとcanonical metadata、provider例外の元identity、immutable copy/null | current PG26508/API全8、旧source成功の算術合算なし |
| SyncRequestListener | borrowed local transaction、検証→DB port→reply stage→JMS commit/ACK。恒久不正はDLQ、I/Oはrollback | 元whole Testはembedded brokerを起動するため非許可。純methodだけの抜粋実行をしない |
| EventListener／DeliveryMetadata／InternalEventProcessor | 固定2route、非cap actual count、時刻/ID、business→commit、default nonnull/SAM identity | Event9、Delivery2、当source guard差とdefault null negative未確認を次通常PTへ |
| InboundTransactions／CommittedFatal | attempted→rollback→confirmedの真の順序、isolate send/commit後だけterminal、未確認を成功化しない | 純InboundTransactionPort全6。Errorはouter ownerへ伝播、ACK成功としない |
| ReplySender | fixed reply FQQN/persistent/TTL、borrowed callerだけがcommit/closeを所有 | shared JmsMessageFactoryはP00504での後続点検依存 |
| DlqSender／FatalWriter／FatalMetadata | body/handle保持、10固定property、128ASCII/1..32code、TTL0/persistent、borrowed transaction | 純DLQ8/FatalWriter3全source確認。元DLQ8に既存のguarded/untrusted/null/故障があり重複製造しない |
| SqlConnectionProvider／package-info4／SyncRequestProcessor | caller-owned abstract JDBC/dispatch port、NullMarked。実DBを開かず自然Code不在を保持 | 実装なしinterfaceを無意味なruntime/assertへ変換しない |

旧PG23478（SHA `3d9b27a9d8bc04eea13b0cc81622df70070bb05089d0d712f0fd49f50041d455`）のEvent9は、target source/physicalとTestが同一だが32入力中Guard一件が当sourceで変わった。旧proof自体もwholeDependencyQualified=false。旧9を現合格や新規受入へ転用せず、変更後接続を通常PTで再資格する。

A3-08は既にcompletedIdに一件ある。4678開始で原価格を加えた誤りはBUG2667/YKT2347へ修正前起票し、開始見積り.4/1.05/2.2を残して現原owner .25/.65/1.3へ追記訂正。A3原費追加・再完成計上0。P00503/1準備の.087/.227/.455だけを原作業完了に記録し、変更依存の再資格費と新negative費は別分類で凍結した。完成率・専有実費は捏造しない。

実DB/credential/broker/VM/native/Root/held四classへのI/Oは行っていない。C04/F02/F03・四ownerのwhole oracle・実経路・全451は未受入。正式1964PT/53scope・元190新規受入0・工数nullを保持する。
