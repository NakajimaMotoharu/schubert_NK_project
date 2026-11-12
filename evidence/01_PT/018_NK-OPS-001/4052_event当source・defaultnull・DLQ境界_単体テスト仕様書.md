# event当source接続とnull・DLQ境界の通常PT

NK-MSG-001。RD MQ003/006..010、UI231/232、SS312/321/322/323、411/451。Production Main236ffddc83不変更。対象TransactedEventListener／InternalEventProcessor／InboundTransactions／DeliveryMetadata／DLQ writer・sender・metadata／Guardの全14physicalとProtocol176。

| Test ID | 対象・fixture／操作 | 独立期待値と根拠 |
|---|---|---|
| PT-JMS-TXP001..009 原9 | EventTransactionPortTest全原method、literal QWK320byte／WLG2336byte | 原SS offset入力・process/commit/rollback/callback順・恒久隔離・UNKNOWNのassertを保持。旧結果を当sourceへ移さず同runで必要再資格 |
| PT-JMS-TXP010 新1 | 2route×2entry×2getter×IAE/NPEの16入力。元getterが返さず投例外 | provider故障はwire不正ではない。元instance・body不変・DLQ mutation/send/commitなし、rollback一回。observedはattempted→rollback→confirmed、legacyはrollbackだけ |
| PT-JMS-TXP011 新1 | default portへ(event=null/delivery=null/両null)、次に明示literal objectの正常入力 | null三入力はSAM未実行、正常は元event同一instanceをSAMへ一回。期待はcount/identityでproduction codecから生成しない |
| PT-JMS-DLQ-WRITER-BOUND 新1 | Writer transport128（内側ASCII space/上限tilde）×code長1/32の4正常、0x1f/0x7fの近傍2異常 | 128文字transportとcodeをtrimせず保持、body[0,32,255] exact、境界外は送出propertyを作らずIAE。literal値が独立oracle |
| PT-JMS-INPORT001..006／EVENT-DELIVERY原2／Writer原3／DLQ001..008／Guard全8 | 全classの借用JMS Proxy、null/欠落/empty/未知/境界/例外 | 既whole fixtureを再利用し同種guarded/untrusted試験を新規製造しない。元独立expectedを保持 |
| Protocol130 | 当byteの共通codec全class | 閉包全counter検証の必要共有、原golden保持・旧exec合算なし |

計169件、新定義3。新規入力はprovider16、default null3/identity1、writer正常4/異常2。対比sourceは旧23478 target/Test同一・依存Guard一件変更で、再実行は当sourceの必要な接続検証として扱う。原A3の再完成や元190新規受入へ加算しない。

26577製造で原Event9/Writer3の全token逆変換一致。26578はJava25/ErrorProne2.50.0/NullAway0.14.1 fresh限定compile0。14physical中13はnormal同byte、意図した変更Guard一件は先行current26508の当byteと一致。26580全14ClassStats SpotBugs0/missing0/error0。whole6 fixtureのPMD raw30はborrowed Proxy context／standalone interface loader／専有null対応map／Proxy identityで個別に非該当、CS/適用/未分類/処理error0。

Preflight26582 SHA `902bc2c3c375bc75f707caa8596384ac361e0fc6a60e5ddfb2c1c663c6cb21f3`。予定commandは `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1272_event_normal_qualifier.py run <固定commit>`。PG26584／独立PG26586へ実日時・OS/JDK/tool・branch/source・command/exit・入力/期待/実際・全190physical/当CRC・line/method/class/branch・XMLhashを保存する。作成時green/coverageは未実行。

全fixtureはJMS API ProxyとArtemis宛先の値だけで実serviceを起動せず、actual held四classを読み/compile/loadしない。unsafe embedded whole fixtureからmethodを選択しない。実DB/鍵/Root/VM/native/配備/intentへ進まない。C04/F02F03/四owner/全451・正式1964/53は未完、IT/ST完了は宣言しない。
