# 2497 BrokerJournal 現whole12通常PT仕様

2026-10-29、PG-D814予定、主F03・canonical担当費参照Query=P00404/Evidence=P01710/追加費0。START2876/開始1/3/6pp cap10、freshused26残74/reset1793774153。source17ab52b25、保存671a0fd194f85cce1091af1a0e094efb29c11804/push44288真正0/remote一致。既normal13596/静的13599同source参照・確認再演0。

## 既whole全範囲とPT_DEFAULT

Query全275行/五method、Evidence全322行/七method・Main Evidence345行/既InspectorUnitProbe372（ResourceScope/ProcessResource/StopGate含む）を確認。Query Startは全て自分のChild fake Processとbyte-array streamsのみ、command journalctlはfakeへ渡すliteralで実行しない。全getters/wait/exit/alive/destroyはoverride済み、自己所有virtual drainだけ生成。固定100ms遅延対50ms budget、read5s対1s・drainFinished5s、正常131072byte/2s、専用JVM180sで有界化。real timeを使う試験であり固定Clock試験と偽らず、失敗/flakyを成功に算入しない。

Evidenceは手書きJSONのconsume/contentSha256/anchor/consumeClosedHistory/consumeStoppedだけ。実inspect/inspectStopped/Root guard/Live owner/NativeReader.forTargetを呼ばない。全boot/invocation/cursor/time/messageは固定合成値・実journal読取なし。SHA-256は独立標準計算、provider欠落観点は専用自己所有child JVMのSecurity registryだけを変更しfinallyで全順序復元/assert・abc既知vector確認、@Isolatedで他caseと隔離。実OS process/journal/systemctl/busctl/Unit/MQ/DB/VM/Root/permit/鍵/私有ログ/Graph9へ到達0、元HOLDwhole抽出0。

## 期待値・観点

SS321§13/341/343・SSC125/131/132/919、OPS009/UI251、既BROKERQUERY/BROKERSTART003・bj2478001..004/ISSBROKERSTOP001。Query五は開始/完了waitの元budget、drain cancelと全stream一回close、正常大容量の独立J配列、size17対limit16・exit7・timeout/interrupt・invalidlimit、合成IO/runtime/Error/close失敗のidentityと固定理由。finish latch/割込消去まで後条件を確認する。

Evidence七はvendor2.56の手書きAMQ221013/221007/221001と停止221002、same boot/invocation/time/cursor・strict JSON・重複/未知field・非法UTF8/空/末尾LF/最大65536・4MiB/過去時刻/別brokerを拒否。canonicalはTestのTreeMap/hexからNKJOURNAL1 ROW文字列を独立生成しJDK SHA-256、raw digestも独立計算する。Productionmethodでexpected生成0。Anchor/Summaryのredacted文字列・constructorは元記録2348も参照するが、当runへ過去counterを加算しない。

現Test SHA Query935ce8af…/Evidence73ec7a8b…は13400前a26a9b38…/5ae664be…からliteral1/5変更済み。元293/613/781/2348などの旧成功は保存し転用0、新ID0/既十二methodだけ必要通常PT。raw電文/実log/credentialは公開せず、元値なしXML・case・counter/hashのみ。

実command=`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg13692_broker_journal_whole_twelve_pt.py`、fixed SDK/六jar/新SLOT・whole二class/COUNTS5+7/四期待12/説明をbind前guard。独立13694は元XML/一意十二case/FES0/全source/SDK/exec/session/CRCを照合し、Evidence/InspectorUnitProbe完全二source unit（実行七物理＋自然interface metadata二）をcounter測定。実inspectやdefault/native methodsの未実行を隠さず、既知未測定・missを除外/到達不能扱い/旧exec合算で100へ変換しない。通常PT完了とcoverage未達/全体451未完を分ける。正式1964/53/17-190/工数null/QA051final/全actualHOLD/全保全物を維持。
