# 1716 MQ processing duration metric 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171 MON005/006/010～013/UI231233252/SS321323351/PG-D570。MqProcessingDurationMetricRecorder constructor/record/detailedMetricsRequested・Outcome.parse/values/valueOf。one ownerを承認済みLayoutId/version1に固定し、flowは同LayoutDefinition.interactionKindのSYNCHRONOUS/ASYNC_ACCEPTANCE/INTERNAL、outcomeは供給観測SUCCESS/FAILURE二値。Flowを引数の任意文字列やdecoded payloadから作らず、SQL/user/token/path/exception等をlabelへ入れない。SS323のQSBREQ01/QSBRSP01=A、QWKREQ01/WLGEVT01=I、他60=Sを独立literal表で検証し、実Root/JMS/ACK/業務resultを推測しない。

DEBUGはlayout毎の二Summary/seconds/publishPercentileHistogram＋p95 .95、観測bucket .001/.01/.1/1/1.5秒（合否/alert/SLOや既時間budgetを変更しない）。SDK小数秒量子化を避けるdouble histogram選択とSDK補助Gauge各6を全量確認。STD詳細登録/record0だが未登録layout/null/負nsを受理しない。全64を作成してもflow×任意layoutの直積を作らず、128primary＋768補助=896meterの固定namespaceに留まる。別instanceが同layout/registryなら同じSDK系列であり、実event exactly-onceや集計owner唯一性は本部品の受入外。

| Test ID | 目的/事前fixture・操作 | 独立期待値 |
|---|---|---|
| MQTIME001 | SS323全64手書literal・flow対応、二Outcome | 128primary Summary/768補助Gaugeを全量検証、fixed label3/base seconds/初期0/histogram五bucket/p95要求/任意namespace0 |
| MQTIME002 | 固定0/1ns/.5s/1.5sを各Outcome、別registry MAX二回 | count4/sum2.000000001/max1.5/CDF2,2,2,3,4、MAXsum1.8446744073709553E10 finite・別Outcome不変 |
| MQTIME003 | Outcome parser/生成factory・未知/小文字/空/null、未知LayoutId両mode | typed literal二値/values配列分離/valueOf全既知・未知・null、UnsupportedLayoutException/任意namespace登録0 |
| MQTIME004 | constructor null/未知mode、nullOutcome・負-1/MIN・MAX両mode | CONFIG_INVALID/NPE/異常伝播、STD詳細meter/record0、DEBUG正当二増分 |
| MQTIME005 | 第二summary factory Runtime/Error | 同一Throwable・呼出2/primary1＋補助6/record0/借用close0、caller finally close1 |
| MQTIME006 | record前/増分後Runtime/Error | 同一Throwable/一回呼出・partial count-sum保持/補償・再試行/close0 |
| MQTIME007 | 64呼出前fixtureのlayout/Outcome/ns/count/sum/max、二layout・別registry | finite5秒future、独立sum tolerance1e-12/max/count、別owner .25s/既64不変 |
| MQTIME008 | foreign Counter同一name/labels | Summary置換拒否・元meter/値7同一保持/借用close0 |

旧INBOXMETの独立SS323 literal vectorを試験素材として再利用し、Production LayoutRegistryの出力からexpectedを生成しない。使用するLayoutRegistry/Definition/InteractionKindは既176class純粋依存の同byteを先行検証済み、再導入/SQL/ネットワーク/実MQ/時計/VM/Root等0。新8＋必要既API146を当154/19、7892ordinary＋7896正常六compile（別snapshot）→7894独立38Java/実32＋metadata1/CRC/四100→7898全1781（API33/歴史Batch65-Web14）→7900全127delta-112追加physical→7902生成既50＋新Outcome2=52/raw全理由→7904公開scan・1717結果へsource/run/環境/時刻/command/exit/input/golden/実際/coverage/BUG/hashを結合する。

group1939、開始3/5/9pp上限10/fresh9残91/reset1793382075/PG7890fresh receipt。元/v4/v5・旧markerlast27区間/共有累積/専有N-T/工数null/元90再基底化0、正式1964/53/原190新受入0/QA051final/PTALT0/whole451-native-CHR・全actualHOLDを維持。実broker/API budget/consumer hook/exporter/p95品質は未受入で、供給duration観測だけを実装・試験する。

BUG-3882／YKT-2997。MQTIME007の整数期待・8worker／64件・元期限を維持。workerの有限終了の失敗を一次例外に付随させ、fixtureが所有する二registryは逆順で閉鎖。現版3件の終了は[PG45498](evidence/PG45498-current-duration-and-message-fixture-owners/manifest.json)。実監視は別。
