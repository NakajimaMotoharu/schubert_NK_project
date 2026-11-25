# 1693 MQ供給圧力metric 単体テスト仕様書

2026-10-24実測追補：初回d8df/7644は真正114/14、7646はL414/M82/C23/B199全miss0・SB/CS0だがPMD新duplicate literal1（全14）でBUG1670/YKT1421起票、当qualityは未受入。元計画の実22/physical93/全1762はnested Snapshot一型の計上漏れで、実23/physical94/全1763へ技術測定見積を訂正（工数成果/受入増とはしない）。SS literal/期待値・8caseは不変更、Main固定label定数化後の7658/7660/7662/7664/7666/7668で同sourceを再資格する。初回成功/未実行draftを変更後の成功へ転用しない。

NK-OPS-001/P01809/C07/RD171 MON/UI252/SS351§6・8/SS321§4～5/PG-D559/group1911。MqPressureMetricRecorder constructor/record/missing/snapshot/detailedMetricsRequestedとSnapshot全method。actual broker/management/JMS/送受信/再送/Queue browse/control/DB/Rootは行わず、供給済の現在snapshotを表示する内部部品。

SS321のliteral6addressと対応6queueをlabelに、SS351のqueue_messages/queue_bytes二gauge（queue label）とaddress_memory_bytes/address_paged_bytes/paging_active/page_files四gauge（address label）をDEBUGだけ計36series事前登録。初期/欠測はNaN、真0と区別。STANDARDは登録/保持0。観測は一destination単位のimmutable snapshotでpublication、metric scrape全6fieldの横断atomic性や実source/timeを保証しない。件数/byte/memory/paged/filesは独立非負longで、異なる集計/制御値の同一化・容量比/最大値clamp・flagからbyte捏造をしない。booleanは既知true/falseだけ、unknownはwhole sample欠落とする。

| Test ID / method先頭 | 入力・操作/独立期待値 |
|---|---|
| MQPRESS001 / mqPress001 | SS321の手書6address/queue×SS351手書6metricの計36、型Gauge/label keyとpair完全一致、初期全NaN/各snapshot empty/登録36/close0 |
| MQPRESS002 / mqPress002 | 全destinationで1/2/3/4/true/5を異なる6値として確認、全0/false→0、MAX longはsnapshot原値保持・SDK double9.223372036854776E18/flag1、系列不変 |
| MQPRESS003 / mqPress003 | 全destination既値→sync requestだけmissingで6NaN、他5不変/旧snapshot不変、再missing/真0回復 |
| MQPRESS004 / mqPress004 | STANDARD全destination record/missing/snapshot保持0、null registry/mode・空/小文字/未知mode拒否。五longの各位置-1/MIN負を独立拒否 |
| MQPRESS005 / mqPress005 | 第2Gauge factory Runtime/Error同一伝播、残1/登録2/close0。foreign Counter同seriesは置換せず同一/値7/close0、caller finally close1 |
| MQPRESS006 / mqPress006 | 64callerのsample publicationは供給snapshotのいずれか、別ownerの7/8/9/10/false/11不変、別destinationはunknown、登録36ずつ不変。scrape横断atomic性を主張しない |
| MQPRESS007 / mqPress007 | DEBUG/STDのnull destination/sample/record/missing/snapshotを境界拒否、旧受入snapshot/close0保持 |
| MQPRESS008 / mqPress008 | record generated9method：同一/同値/対称/null/他型/全6field一差、Long xor-fold/Boolean1231・1237/31foldからhash30607576/30607762、1<<32 hash同値かつequals非同値、固定textと全accessor |

expectedは上位表literal/明示算術・JDK primitive hash規約から独立、Production判定/hashで期待生成0。BrokerTopology.requireAddressはtyped入力形成だけ。pure initializerは既標準6 literal/JDK String結合だけ、PG7625の全protocol入力/176class束縛に含む。PT harness/Production POM/品質/依存pinは前群から不変更、新実行と正常六compileのprotocol全176byteを再結合する。

元製造新8＋必要既106を当sourceで普通114/14suite・28Java/実22＋metadata1予定。旧106/Batch237/Web27や依存Protocolのcoverageを合算0。新Snapshot生成9＋既32は当ordinary/actual byte/javap/既JDK-filter証拠で別確認し、四counterへ合成/除外追加0。全1762Main/106source/93追加physical予定、旧104source不変2新。7644host/7646独立/7648正常六compile/7650全Jar/7652trace/7654review/7656公開scan、1694結果へ実hash/command/OS/JDK/日時/branch/source/actual exit/XML/CRC/四100/静的/BUGを結合する。

開始2/4/8pp上限10。fresh表示は使用0/残100/reset1793382075で、直前27/73/reset1793306748とmarkerが異なる。実reset・消費0・新たな90pp予算を推定せず、旧窓開始0/最後27と今回新観測を分離し区間消費null、券消費/追加課金/モデル変更0。原-v4-v5/旧cursor不変更。正式1964/53・原190新受入0・工数null・QA051final/PTALT0・whole451/native/CHR/全actualHOLD維持。

BUG-3881／YKT-2997。MQPRESS006の元の固定期待、8worker、64件、10秒、registry個別所有を保持。期限付き終了を共用し、二次失敗は一次を覆わない。現版の真正5件は[PG45494](evidence/PG45494-current-five-api-metric-fixture-owners/manifest.json)。実環境と正規全451は別。
