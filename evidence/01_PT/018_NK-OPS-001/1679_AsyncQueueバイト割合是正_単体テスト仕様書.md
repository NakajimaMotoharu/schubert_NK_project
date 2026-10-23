# 1679 Async Queueバイト割合是正 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171-MON005～013/UI252/SS351§7 footnote・SS321§5.2/BUG1665-YKT1416/PG-D552/group1897。1674/1675の件数比oracleを訂正する現行仕様。旧技術成功200/192を保存し、新sourceへ合算しない。上位設計は既にbyte単位を明記し変更不要、QA/RDF/UIC/SSCなし。

対象Main=AlertThresholds.asyncQueue(queued,usedBytes,capacityBytes)、MonitoringPolicyEngine.asyncQueue、AsyncQueueMonitor.observe/snapshot、ByteUsage/Evaluation。旧二long APIは廃止し全呼出を三次元へ改める。件数非負、使用byte非負、上限byte正。割合は使用byte×100と上限byte×70/90の正確整数比較、件数5000/9000とのOR。容量超過は既知異常でありUNKNOWNへ隠さない。

| Test ID/class.method | 入力と独立期待値 |
|---|---|
| THRESH003/013/014 / AlertThresholdsTest.threshold003AsyncCountRatioAndNoOverflow等 | 件数4999/5000/8999/9000とbyte0/上限1でN/W/W/C。件数1・byte699/700/899/900・上限1000でN/W/W/C。件数0・used=limit=MAXはC、used100/limit99もC。各負/容量0拒否、64caller |
| MONPIPE002/003/007 / MonitoringPolicyEngineTest.monPipe002等 | 既12condition/72keysへAsync三独立入力を接続し、0/700/900byte÷1000と固定levelを比較。既復旧/所有/immutable projectionを維持 |
| ASYNCBYTE001 / MonitoringPolicyEngineTest.asyncByte001EngineUsesStorageBytesIndependentOfMessageCount | count1/90byte/100→C、count9000/0byte/1→C、count4999/0byte/1→N。負byte/0容量は旧event不変で拒否 |
| ASYNCQUEUE001～008 / AsyncQueueMonitorTest.asyncQueue001等 | countとOptional ByteUsageを独立供給。count1・69/70/89/90byte÷100と699/700/899/900÷1000、7/9÷10、count0/MAX÷MAXを固定N/W/Cで比較。片側不明でも既知件数5000/9000又は既知byte70/90%はW/C、未知正常復旧0。warning5分/critical10分＋原因確認、gap/逆行/null/無効先行拒否、64caller。EvaluationのbyteUsagePresentへ名称訂正し生成6を独立同一/同値/全field差/1231・1237/JDK identity31fold/固定textで確認 |
| ASYNCBYTE002 / AsyncQueueMonitorTest.asyncByte002ByteUsageInvariantsAndGeneratedContractsHaveIndependentOracles | ByteUsage(70,100)のused/limit、hash=31×70+100=2270、固定text、self/同値/null/他型/各field差。MAXのLong hash=0x80000000・32fold int wrap0。各負/MIN/容量0拒否、生成5methodを当ordinary/byte/javapへ結合 |

expectedはSSの独立単位・固定有理数/時系列/JDK Long hashから作りProduction methodを期待生成へ使用しない。使用byteを件数から換算しない、body上限からbyte割合branchを到達不能扱いしない。全affected Main三/Test三と旧二引数検索を横展開し、FS/JVM同単位比・DB pool同単位・Transfer二次元・Expiry件数の非該当根拠も1680へ記録する。

新ordinary2＋既200の当source202PT/27suite・55Java予定、実class数/四counterは実測して1680へ記録。PG7532→7534独立CRC/session/四100/静的→7536正常六compile→7538全実Jar/SDK/architecture→7540trace→7542生成/raw review。全source/run/環境/日時/command/exit/入力/XML/output/hashは各原manifestへ。生成5を四counterへ算術加算せず、除外追加/品質緩和0。

group開始3/5/9pp上限10（fresh24/76、event1897）、元-v4-v5/元窓0/reset1793306748不変更。今回は実装・独立oracleの手戻りであり元製造新規成果や原190受入へ加算0。実broker/source/owner整合/集計/同時観測/制御/DB/Root/VM/keys/native/CHR/whole451等HOLD、正式1964/53/QA051final/PTALT0/工数null。
