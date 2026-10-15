# 既受入17件の新source再認証・計測切替

2026-10-16、Program NK-OPS-001、SS311/312/313/321/354/355・451/477/487、PT-OPS-3540-001。group CURRENT_SOURCE_CRITERIA_REVALIDATION/開始0925、見積低0.3/標準0.8/高2.5共有pp（専有実費/N/T不明）。工数率や新規受入数を見積から算出しない。

現WBSの17受入はa9 sourceで履歴固定、新Production4856は別の3712/545/1643・native10点/最新9streamで資格済み。新canonical bindingにする前に、個別のcontract/scope/qualityと終了依存を再認証する。941artifactの変更はWBS-P006-02所有のOutboxJmsSender一つだけで既17所有artifactと非交差。これだけを理由に17件を自動承継せず、次をすべて記録する。

1. 各旧criterion・独立oracle/evidence/hash・要求/SS/対象全scopeを保持し、全既受入artifactと共有参照の新source byte、正本文書の変更有無/理由を照合する。
2. 当3712原XMLからProtocol全86/17、Storage全163/23、旧3356のAPI/Web/Batch consumer全suite及びC04 Broker4件を読取専用で照合し、F/E/S/flaky/rerun/not-runを合格へ算入しない。properties/stdout/parameter値を出さずcase argumentはSHA256化。新試験実行件数の加算0。
3. 旧3356比のAPI/Web四Test source差はAfterAllのnull cleanup guard一行だけかを独立byte置換で検証し、期待値/入力/assertionの変更0を確認する。Protocol/Storageと残Testのbyte不変も全件確認。以前の独立oracle是正は旧3356/3350の既受入結果を最正とし、それ以前の不正oracleへ戻さない。
4. Protocol/Storageの新source四counter missed各0、全Main/Jar・元saved/source exec・独立XML・静的六0を確認。F01は現規約/quality/Module/全七POM・mandatory topics、C04は正本RD/SS・単一設定/独立XSD/policy反例・新原XML4を別根拠で再確認する。全F03/全code品質合格とはしない。
5. 各criterion・全依存に不足があれば当該承継を保留し、旧17の履歴を維持する。合意済scope/品質/coverage期待値を変更しない。新受入leaf数の増加はこのsource revalidationでは0。
6. 全criteriaが揃った場合だけmaster/children/941inventory/current snapshotを元hashと保存した変更intentに基づき更新し、旧全binding/acceptance/evidenceを履歴保存する。受入数・scope・元/v3費用・工数null・正式1964/53・QA051final保留を維持し、strict WBS auditで検証する。文書のみの変更で全回帰を反復しない。

現source公開全六XMLはPG3532-current-native-measurement-v3/773c4296、実経路はPG3534/05800013。current-only測定の未網羅784L150M9C477Bを保持し、旧a9 native28と混ぜない。実行結果/対象commit/追加障害/各artifact hashは次追記、着手時点で新source17件再認証・WBS切替は未実施。

## 実行結果（2026-10-16）

3540（ded6b5c08）読取0：当3712元XMLのProtocol86/17・Storage163/23・API79/13・Web44/9・Batch17/3、計389件/65suiteの既成功をsource/Test hashと照合。再実行/新試験加点0、public witness **4a7883b2b6d37552514a69976ff9d5295d58893d26ada5dc32465cc21f87054b**、properties/stdout/argument実値の公開0。

3542の独立再認証=17件/51criteria成功、manifest **9631b15ae518cd53cf3d591a7a18d81d8bc8be3f020035b7dfe8516f0960cdb2**。941artifactの全旧Git blob/current4856 byteを検証、差分は未受入P006-02のOutbox一件だけ。17件の全所有artifact・P002-01共有PayloadSemanticValidatorの一意owner/費用0参照・四counter100・全依存・全旧oracle/evidence/hash・正本六文書を個別確認した。旧3356比の四TestはAfterAll null guard一行のみ、入力/期待/assertion不変更を完全byte置換で照合、他Testは同byte。F01全七POM/規約不変更、441はPG-D419の内部修正追記のみ、SS354は公開SSC285の限定補足のみで従前本文をbyte保存、F03受入ではない。C04は同設定/正本RD-SS/独立policy反例・公式XSD/Jar/原canary source/log hashと新XML4を確認。純境界3・switch純2、計5成功。

3544（3757ac729）stage0→apply0：四正本の元hash/全beforeをPG379私有へ保存、候補三文書はstrict WBS audit合格後、耐久intentを先行して481/485/486だけ置換。484費用はbyte不変更、旧17受入と旧全bindingは履歴保存、Outbox新SHAは元障害/新3712/native証拠に限定し当leaf未受入を維持。新source4856の同17/51を反映し新規受入leaf加算0、正式1964/53/工数null/QA051final保留不変更。

新技術分類はHOST_COUNTERS_CLOSED97/HOST_GAPS18/非Java7/参照1、VM_STEP_VERIFIED7（うちA01は当caseのみ・全CHRゲートではない）。旧a9段階N09のintent退役/N14のruntime退役は当4856で未確認なので歴史再確認へ戻し、Root DONEだけから完了推定0。97と以前の92等は異なる測定source/run/streamの分類比較で、製造5件や新受入5件を意味しない。全四counterの実未網羅784L150M9C477Bは別途維持。通常区切り/計測切替のため停止せず残PG/PTへ進む。
