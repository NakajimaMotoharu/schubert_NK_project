# 1718 MQ event counter 単体テスト仕様書

2026-10-24 BUG1691/PG-D589訂正：当初の内部baseUnit=messagesは実PrometheusでSS351正名をnk_mq_messages_total_messages_totalへ変形することをPG8207原60bdfffeで実証した。現行はbaseUnit未指定（Id=null）とし、上位の正名/型/label/増分は一切変更しない。元1719/source/旧Simple成功とPG8206失敗は歴史証跡として保持、是正後は1747/1748の新source/正常六compile/実SDK40・独立品質へ。RD/UI/SSにbaseUnit指定はなく、外部期待値を実測へ追従変更するのではなく、それに反した内部設定と内部metadata試験を是正する。

NK-OPS-001/P01809/C07/RD171 MON005/010～013/UI231233252/SS321323351/PG-D571。MqMessageMetricRecorder constructor/record/detailedMetricsRequested・Stage constructor/direction/outcome/parse/values/valueOf。one ownerのLayoutId/version1とBrokerTopology addressをconstructorで固定、DEBUG七Counter/標準詳細0。Stageは供給観測の分類だけでJMS操作を発行せず、業務result code/ACK確定や再送成功/経路認可を推測しない。

| Stage | direction | outcome |
|---|---|---|
| SEND_SUCCESS | SEND | SUCCESS |
| SEND_FAILURE | SEND | FAILURE |
| RECEIVE_SUCCESS | RECEIVE | SUCCESS |
| RECEIVE_FAILURE | RECEIVE | FAILURE |
| ACK | RECEIVE | ACK |
| RETRY | RECEIVE | RETRY |
| DLQ | SEND | DLQ |

SS351の送受信/ACK/retry/DLQ観測を上の内部七tupleへ固定する。ACKは将来の正規所有tx確認の供給値でありMessage.acknowledge()追加やJMS確定の代用ではない。layout/addressの個別namespace確認は経路の組合せの許可/送信admissionではなく、実送受信側の既guardを代替しない。任意query/user/token/context/messageID/exception本文をlabelへ受けない。全64layout×六既address×七tuple=2688固定primary Counter、型COUNTER/baseUnit未指定/label4でSDK補助meterなし。将来のhookが正当なeventを供給する責任、複数ownerのexactly-once/永続counterは未受入。

| Test ID | fixture/操作 | 独立期待値・観点 |
|---|---|---|
| MQEVENT001 | SS323全64手書literal＋SS321六address＋七tuple | 全2688 meterのname/type/label4/baseUnit未指定/初期0を完全検証・任意系列0 |
| MQEVENT002 | 全stage一回＋SEND_FAILURE三回、別layout/別address | active七系列1/失敗4、他owner全0/呼出10、借用close0 |
| MQEVENT003 | 七typed Stageと上表literal、parse/values/valueOf | direction/outcome全getter、全既知/空/小文字/未知/null拒否、values配列独立、新生成2method |
| MQEVENT004 | registry/mode/layout/address null、UNKNOWN1両mode、未知mode、STD全stage/null | 任意namespace拒否/CONFIG_INVALID/NPE、STD factory/全meter/増分0、DEBUG null後既ACK1保持 |
| MQEVENT005 | 第二Counter factory Runtime/Error | 同一Throwable・呼出2/残1/初期0/増分0/borrowed close0/caller finally close1 |
| MQEVENT006 | increment前/増分後Runtime/Error | 元identity/一回呼出/partial count保持/他六系列0、再試行・補償・close0 |
| MQEVENT007 | 64呼出前stage/owner fixture、独立countMap、二owner/別registry | finite5秒future、全七×二owner期待count、別owner DLQ1/既64不変 |
| MQEVENT008 | foreign Gauge同name/label | Counter置換拒否、元meter/値7同一保持/borrowed close0 |

期待値は上表・承認SS literal・呼出前fixture算出から作り、Production methodをexpected生成に使用しない。stage渡しの一event一incrementだけで実retry/duplicate抑止をしない。新8＋必要既API154を当162/20、7912ordinary/7916正常六compile別snapshot→7914独立40Java/実34＋metadata1/CRC/四100→7918全1783（当API35/歴史Batch65-Web14）→7920全129delta-114追加physical→7922生成既52＋新2=54/raw理由→7924公開scan、1719結果へsource/run/OS-JDK-tool/実日時/branch/command/exit/input/独立期待値/実際/coverage/関連BUG/hashを保存する。

group1941/開始3-5-9pp上限10/fresh9残91/reset1793382075/PG7910receipt。実DB/MQ/clock/ACK/送信/再送/DLQ/Root/VM/service/配置0-HOLD、元-v4-v5/旧markerlast27区間/共有累積・専有N-T/工数null/90再基底化0、正式1964/53/原190新受入0/QA051final/PTALT0/whole451-native-CHR未受入。個別catalogの網羅を実MQ処理/全PGPTの完了にしない。

BUG-3882／YKT-2997。MQEVENT007の整数期待・8worker／64件・元期限を維持。workerの有限終了の失敗を一次例外に付随させ、fixtureが所有する二registryは逆順で閉鎖。現版3件の終了は[PG45498](evidence/PG45498-current-duration-and-message-fixture-owners/manifest.json)。実監視は別。
