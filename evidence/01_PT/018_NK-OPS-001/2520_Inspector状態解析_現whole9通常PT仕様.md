# 2520 Inspector状態解析 現whole9通常PT仕様

2026-10-29、PG-D825予定、source17ab52b25/normal13596/静的13599、保存929e6de6752cc1764a4783104bed1339b1186efa/push35000真正0/remote一致。開始0.5/2/4cap10、主F03/canonicalP00404担当費はtrace13776で先行確認・参照のみ追加0、fresh値/STARTはevent2901。原予算/全995旧runtime/正式/QA051final/全HOLD不変更。

## PT_DEFAULTと全到達範囲

既InspectorUnitSnapshotTest全495行/九methodとMain416全body（先行2505で確認した同source、現在Target全enum/constructorも照合）、StopGateException/Failureを確認。手書373byte ASCIIの18field goldenとfake UUID/数値/文字列だけをparseし、quiescent/running/receipt/failedRootGeneration等の純粋predicateを呼ぶ。rootrec002も手組stateの値判定だけでRoot復旧・停止・Unit/ownershipを実証しない。MainにはSystemctl/Reader/native/Root callback・credentialはない。

Testはsource管理された `src/schubert-nk-batch/src/test/resources/inspector/unit-golden.txt` のみを新fresh-test-classes/inspector/unit-golden.txtへ同hashコピーしてclassloaderで読む。373byte/SHA2170fc2e71a4ba50519bc2f123d0bf75fcc46adab033645b7b68b5c513c345f6はTest内literalと独立に固定済み。strictGoldenは**自己所有SLOTのCWD/target/inspector-unit-traces/PT-OPS-UNIT-001-state.txt**だけへ3行scalarを書く（quiescent=true/receipt=10/sameInvocationReceipt=none）。repo/本番path/私有rawへ書かない。traceの元host終了manifestにはhash fieldがないため、独立postで初めてhash記録する限界を明示し、元終端前後にcapture済みと偽らない。

自己pool8/64memory taskとFuture10秒のみ、元Executor TWRの局所無期限と外host180秒を区別。実Unit/systemctl/Root復旧/VM/DB/MQ/Backup/鍵/FD/permit/Graph9/保持原本操作0、同じheld検証の別caller再演/whole一部抽出0。Test SHA8867d836…は13400のliteral整理後で当whole未資格、先行1922/2324等の責任/Map理由は当PT資格ではない。ApiNativeCodecsTestは実PublicCredential reader FD/鍵close依存がありwholeHOLD、一部mockだけの抽出はしない（同候補のTest全読了とはしない）。

NK-OPS001/OPS009/UI251/SS3417.4/343・SSC060、既UNIT001..008/018/021・ROOTREC002。新ID0、以下のloop/vectorをcase数へ加算しない。

|既method|独立期待・入力/操作|
|---|---|
|strictGolden|373byte/固定SHA・全18field、Backup10は成功receiptなし/0のみ、running pid/Invocation文字列の一致・範囲、同世代重複receiptなし、redacted表示、上記scalar出力。|
|propertyInventory|各18fieldの欠落/重複/未知・改行/区切り拒否、順序逆は同値、固定Unit属性・token64境界。|
|byteBoundaries|各位置byte0/CR/128拒否、長さ0/1/2047/2048/2049/65536・末尾LF/追加空行/tab/DELを拒否。|
|scalarBounds|U32/U64・leading0/符号/小数/上限、code0..6/status0..255・UUID32lowerhex/非0、期待literalからreceipt可否。|
|quiescentStates|手書3組inactive/dead・active/exited・failed/failedのみ、pid/control/job非0はfalse、RemainAfterExitはデータ属性の範囲。|
|freshReceipt|異なる固定Invocation/同Invocation、state/result/clock0・逆転/U64境界、codeとstatusのliteral期待。|
|immutabilityAndNull|input消去後copy不変、差分matches false、null契約/redaction。|
|concurrentSnapshots|自己64入力でstatus0/10交互、固定期待とquiescent、他stateへ共有漏れなし。|
|rootrec002KnownThirty…|MORNING/API/WEBの手書status30 failed stateとGC/cold partialの全差分を値判定し、成功receiptへ誤認しない。実recoveryの起動/所有/停止資格ではない。|

expectedをProduction parser/formatterで生成0、固定SS値・手書入力差分・固定SHA・集合が独立oracle。実command=`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg13804_inspector_snapshot_whole_nine_pt.py`、JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15/正常六jar/empty ENV、新Map一箇所由来9。13806は原XML/全源・fixture二path/SDK・単一exec CRC・完全一source unit（Snapshot/Target二physical）を独立確認、missは保持。既定filter不変更/手動除外/旧exec合算0、当data testを実native/Root/正式資格へ換算しない。結果/command/UTC/OS/tool/input/期待actual/XML/counter/hashは2521と専用manifestへ保存し通常区切りで停止しない。
