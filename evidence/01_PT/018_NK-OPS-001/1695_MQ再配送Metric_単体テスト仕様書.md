# 1695 MQ再配送metric 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171/UI252/SS351§6・8/SS321§4・6/PG-D560/group1914。MqRedeliveryMetricRecorder constructor/recordDelivery/detailedMetricsRequested。供給されたdelivery-countの計数だけで、JMS message/propertyの読取、受信/ACK/rollback/retry/待機/backoff計測・DLQ操作は行わない。

SS321の最大4は初回＋再配送3回。初回count1を再配送として計上せず、2/3/4だけを独立counterとして計数する。SS321の手書6queue×2/3/4の18seriesをDEBUGで事前登録、metric名はSS351のnk_mq_redeliveries_total、labelはqueueとdelivery_countだけ。STDは登録/保持/増分0だがnull/範囲外を正常化しない。count以外のmessage/session/actor ID・エラー文面を保持せず、複数の供給観測を重複業務実行と判断しない。実JMSXDeliveryCountの真正性・owner・supplier二重観測防止は外側未受入。

| Test ID / method先頭 | 操作・独立期待値 |
|---|---|
| MQREDEL001 / mqRedel001 | SS321手書6queue×literal2/3/4の18、Counter型/metric名/label key・全pair/初期0/登録18/close0 |
| MQREDEL002 / mqRedel002 | 全queueの初回1は増分0、各2/3/4一回で18系列全1、async2追加で2/計19増分、系列不変 |
| MQREDEL003 / mqRedel003 | STD全queue×1..4でも登録/保持/増分0 |
| MQREDEL004 / mqRedel004 | null registry/mode/destination、未知/空/小文字modeはCONFIG_INVALID、count MIN/-1/0/5/MAX拒否、両modeの既状態不変 |
| MQREDEL005 / mqRedel005 | factory第2Runtime/Errorの同一identity/呼出2/残1/初期0/close0、caller finally close1 |
| MQREDEL006 / mqRedel006 | increment前後×Runtime/Error、同一例外/呼出1/実count0又は1、format/retry/補償/close0 |
| MQREDEL007 / mqRedel007 | 同async3へ64caller→64、別owner web4→1/相互0、18系列ずつ不変 |
| MQREDEL008 / mqRedel008 | foreign Gauge同名pairを置換せず例外、同一meter/value7/close0/増分0 |

expectedは上位literalと初回/再配送区分・明示算術で独立作成、Production methodから期待生成0。新generated型なし、既Snapshot等41生成methodの当ordinary/byte契約を維持する。元製造新8＋必要既114を当122/15suite・30Java/実24＋metadata1予定で再資格し、旧source114/Batch237/Web27/Protocol依存を合算しない。全1764Main/108source/95追加physical・旧106src不変2新予定、7674host/7676独立/7678正常六compile/7680全Jar/7682trace/7684review/7686公開scan、1696結果へ実hash/OS-JDK-tool/日時/branch/source/command/actual exit/XML/CRC/四counter/static/BUGを結合する。

当群開始2/4/8pp上限10/fresh1/99/reset1793382075。旧marker1793306748/last27との不明区間・共有累積null、元90予算を再基底化せず、原-v4-v5・usagecursor維持/専有N-T/工数null。導入/install/DB/JMS/broker/Root/VM/key/配備等操作0、全actualHOLD・正式1964/53/原190新受入0・QA051final/PTALT0/whole451-native-CHR未受入不変更。

BUG-3881／YKT-2997。MQREDEL007の元の固定期待、8worker、64件、10秒、registry個別所有を保持。期限付き終了を共用し、二次失敗は一次を覆わない。現版の真正5件は[PG45494](evidence/PG45494-current-five-api-metric-fixture-owners/manifest.json)。実環境と正規全451は別。
