# Question実API接続の前提契約PT（実装前・未実行）

Program NK-OPS-001の普通API組立／NK-MSG-001送受信・NK-DAT-001通知state。関連RD ASY/QST/NTF/MQ、UI213224231232236242、SS312321322323324331332343、SSC151～155、BUG421～423/YKT332～334。正式run24とは別の暫定変更群。未実行を成功扱いしない。

| Test ID / class.method | 目的・fixture・操作 | 独立期待値 / 異常・境界 |
|---|---|---|
| PT-JMS-QSB-A-API / SyncRequestListenerTest.questionAcceptanceUsesExistingPhysicalSyncQueues | 実Embedded Artemis、独立QSBREQ01/QSBRSP01 byteをrequest送信→listener→reply | header offsets0/8/11/19/22/23/24/60/96/113/177/181/187/193/199/208/212をliteral埋込。Q/A・4400byte、S/A・320byte、固定NK/JMS identity、persistent・TTL・local commit・元ACK。Sの旧正常維持、偽A/内部I/layout/identity不一致は未dispatch/DLQ |
| PT-JMS-QSB-A-WEB-SEND / ArtemisRequestSenderTest.questionAcceptanceSendUsesSameApprovedQueue | actual broker、同offset独立Q/A request→Production sender→Queue観測 | body byte完全一致、NKLayoutID QSBREQ01、reply-to nk.sync.reply.web、TTL5000、Persistent。LOGに偽A、QSBに偽S、QWK/internal送信、wrong kind/correlation/lengthを拒否、既存rollback/close保持 |
| PT-JMS-QSB-A-WEB-REPLY / JmsReplyDecoderTest.acceptanceReplyUsesExactRegisteredAsyncProfile | provider proxyの独立S/A320byte、metadataを変更 | immutable body/correlation、QSBRSP001、wrong kind/A layout/interaction/property/destination/null/count/expiryを拒否、S旧正常維持 |
| PT-JMS-EVENT-DELIVERY / InternalEventListener direct delivery tests | guard済みQWKをactual count1/3/4/5で届け、WebLog SAMも確認 | capしないactual count/元transport ID/Clock UTC、metadata null/unknown/空/制御/長128境界/0を拒否。Question count-lessは非成功、worker失敗rollback・最終DLQ未送信ACK0 |
| PT-QST-STATE / DatabaseMigration notification tests | V003旧state ACCEPTED fixture→append-only V024→readback、全Job stateの新insert/update | RECEIVED/PROCESSING/COMPLETED/ERROR/CANCELLED allowlist、ACCEPTED state拒否、notification_type ACCEPTED保持、本文/IDs/owner/time/version原本保持、履歴旧checksum変更0、grant不変、無効state SQL23514 |

追加業務終了試験（SSC154155）：実PostgreSQL受付全5insert＋snapshot atomicity/rollback、並行同token1件、M0/W/M1独立IDとNKREF1 AAD、SENT前応答9000/後0200、2秒総deadlineとwait中DB/lock解放、保存proof欠落／expired Inbox重複防止、最終delivery4のERROR＋immutable DLQ dispatch D・元wire W・元ACK順、各crash、取消競合、owner/ADMIN範囲、query固定50行順序、削除三点answer継承、全31processor/3consumer/outbox/full lifetime/reverse shutdown。

実行環境：Linux/JDK25.0.4/Maven3.9.12/Node24.19.0、offline M2。選択commandは全moduleに少なくとも実testを指定し、test-compile/jar:test-jar/test/SpotBugs/JaCoCoを行う。共有codec/DDL/security変更群はSource/tests/tools固定後全6clean再回帰。実行日時・対象commit・終了code・actual/assertion・coverage B/L/M/C・再試験BUG/YKT・safe manifest/hashは304結果と既存collectorへ保存。coverage100%・native/full ready・CHRは未認定のまま別gateを閉じる。raw session/context/token/keys/providerログ/DB dumpはGitへ置かない。
