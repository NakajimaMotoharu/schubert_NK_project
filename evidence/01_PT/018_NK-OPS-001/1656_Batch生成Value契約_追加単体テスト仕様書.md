# 1656 Batch監視生成value契約 追加単体テスト仕様書

NK-OPS-001/P01809/C07/451§4/SS341351、BUG1662/YKT1413/group1879。既743/169PTの全Main43byteが当固定Jarと一致し、record七/enum十二のsource/constructor-clinitと既Testを確認した。新fixtureはJDK immutable値・public生成factory/recordとメモリ内AlertLifecycle.Eventだけ、DB/FileStore/MemoryMXBean/実観測/Root/VM/keys/配備等操作0。Production/harness/依存版不変更、Test-onlyで不足したgenerated契約を補う。

対象はenum12×(values,valueOf)=24method、record7×(equals,hashCode,toString)=21＋全15accessor、計60生成method。全手書きconstructor/validation/観測logicも既inventory実42＋metadata一から削除せず、標準filterのplumbing契約を独立通常実行/byte metadata/reviewで明示、四counter分子へ60を加算0/custom exclusion0。

| Test ID | 対象 | 目的・入力・独立期待値 |
|---|---|---|
| GENB001 | AlertLifecycle Condition/Service/Severity/CauseClearance | SS351と固定literal/typed constant対、全値valueOf、未知/null拒否、values配列変更後の新配列不変 |
| GENB002 | BatchMetricContract Step/Status | SS341十step/四terminalの固定vectorと同enum生成contract |
| GENB003 | MetricContract/Kind | SS351 catalogに対応する固定26constant/三kind・全factory/null/未知/copy |
| GENB004 | MonitoringModePolicy/DetailService、ContinuousWindow.State、Transfer.Suffix | 固定2/4/3/2constant・全factory/null/未知/copy |
| GENB005 | ObservationContext | clearance/at/elapsed各差、self/同値/null/他型、全accessor。EPOCH/Duration.ZERO hash0・JDK Enum identityと31-foldから独立hash算出、固定全field toString |
| GENB006 | 五Evaluation record（Filesystem/JVM/DB/Sync/Transfer） | true/false・Optional.empty/nonempty/同一・別Eventで全component equality、両accessor、boolean hash1231・空Optional0/非空EventのJDK identityから独立31-fold、固定全field文字列。Eventは純メモリfixtureでObject equals/hash/toString非overrideをsource確認、production record hash/toStringをexpected生成に使用0 |
| GENB007 | TransferMetricRecorder.Counts | files3/bytes5・各一差/null/他型/同一、全accessor/hash98・MAX/MAX hash0・固定safe primitive toString |

enum expectedはTest内の独立literal→typed constant対でありvalues/valueOfからexpectedを作らない。record expectedもJDK25 ObjectMethodsの31-foldとplatform Boolean/Enum/Object identity・EPOCH/ZEROの公知hashから独立算出、当型methodをexpectedへ使わない。private reflection/到達不能偽装/除外0。Event生成はfixture setupでありrecord oracleではなく、真正原因撤去/観測/実gate許可を作らない。

新7＋必要既169=当source176PT24suite/Batch49Java/実42＋metadata1予定。元PG7420/7422以降ordinary verify/XML/FES0/正確source/session/CRC/四100/静的raw28理由同byte/全六Main-Test正常compile/全1738Mainbyte・source traceへ環境/command/time/exit/BUG/hashを保存する。SourceはTest一追加だけ、API72/Web23は歴史byte参照のみ・当sourcecounter/PTへ合算0。元4222/common44の確認再演0。

開始見積3/5/9pp上限10・元/v4/v5固定、追加発見品質是正を元PG進捗へ計上しない。正式1964/53・原190新受入0/工数null/QA051final/PTALT0/全体451/native/CHR不変更。YKT1413他候補の照合は依然OPEN、候補数から未試験/欠陥/工数を推定0。通常区切り/PMO返信待ち停止0。
