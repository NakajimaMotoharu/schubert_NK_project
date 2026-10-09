# Inspector残異常系の独立追加PT仕様

## 実測結果（2026-10-10、PG919限定成功）

source ca0e03feeae55d7c32663ab32894cdf596f8ba8a/branchdev-foundation、actual0/66PT/8suite/FES0/staticbatch0、全343main class byteは当PG915/4ebfと一致。四追加caseすべて期待拒否/原byte/一回owned退役/実deadlineTIMEOUT・全stream/子後条件を明示assertで通過。Files131L26M1C38B、Publisher134L25M1C46B全100%。NativeReader125/129L・20M1C24B（branch100）、実OS呼出し四行は未網羅、除外0/実VM未実行/正式未受入。公開 `evidence/provisional/PG919-inspector-host-v1/manifest.json` はsource/time/command/OS/tool/freshXML・JAR/exec/coverage/static/loghashを保存。別testsource同main-byteの限定診断であり、PG915全体sourceの3550へ66を足さず、新sourceの全体合格にも使わない。

Program NK-DAT-001/NK-OPS-001、主担当WBS-P004-04、DAT-001～011/OPS-009・UI212/251・SS341§7.4/343§6.11/352、開始main候補4ebf/VM e016別、PG915全3550/523資格は保持。開始前event0241: 既B-HOST .5/1.5/3.5週次共有ppの継続・二重費用0、N/T不明を推定0。期待値はSSのfixed namespace/同owner退役/query所定期限と手書きfixture・非変異/解放後条件から定義しProductionで生成しない。

| Test ID | class/method・入力/操作 | 独立期待値/後条件 |
|---|---|---|
| PT-INSPECTOR-919001 | InspectorEnvironmentFiles.executeOwned/Retirement.retire、固定run/envを所有したcallerが別threadへretirement callbackを渡し一回実行要求、その後caller自身で一回退役 | 別thread要求はStorageIoException・元env bytes保持/unlink0。同owner退役だけ成功/unlink1、全資源解放。callback渡しは観測port試験で実VM権限ではない |
| PT-INSPECTOR-919002 | InspectorEnvironmentPublisher.requireFresh、独立temp固定名前空間に既env/別UUID.part/他roleの無関係なentry（fixed env/UUID.partではない） | 固定対象env/partは拒否・原byte保全。対象外entryをInspector原本と誤認/削除/再利用せずscope-only freshness判定、非変異と全解放確認（全namespace/親起動許可の代替ではない） |
| PT-INSPECTOR-919003 | NativeReader.executeStreaming、query開始までに実budgetを使い切るprovider、又はwait後に所定budgetを超える正常完了provider | いずれもTIMEOUT、全stdin/stdout/stderr一回close/所有子解放、早い/遅いreceiptをsuccessへ読み替えない。実monotonic期限を越すbounded fixtureでwallclock等の人工注入なし |
| PT-INSPECTOR-919004 | executeStreaming、完了子だがstdout readerが所定期限を超えるprovider | TIMEOUT、drain cancel/interruption/全stream close/子解放、unknownを成功化0。fixtureは期限より十分長いdelayと終端を持ち、負荷遅延が成功へ反転しない。失敗/flakyは合格加算0 |

正常/他境界/null/unknown/再送は関連既Files/Publisher/BrokerJournalQuery/Probe suiteも一括選択。同行競合は別thread能力の拒否と解除後結果で検証、秘密/本番files/managerの変異なし。実行command・固定source・OS/JDK/Maven・終了code・freshXML/coverage/static/hashは実測後追記。初期未実行/coverage未認定/関連BUGなし（既処理の仕様違反が出たら修正前起票）。追加testのみの成功を全体4ebf又は新正式認定へ流用せず、主class byte一致と診断に限定する。
