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
