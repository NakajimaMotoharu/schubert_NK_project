# 1536 CHR gate工具契約・親範囲 個別受入matrix

2026-10-23、群1788、P020-01.03の参考.5/1.34/3pp/共有上限10pp。source3c70db393。子02は492で同source受入済み。全GateContractValidator/結果record・GateCliのreport/source/preflight/昇格/JSON原子性とTest/helper、正本SS355/264と固定contract/schema/requirements/browserを全文点検した。実装修正不要。子01/02と同じ原44の共有品質を使用し、成功確認の再実行をしない。

## G01～G06の工具契約と独立oracle

| gate工具契約 | 明示した独立期待値・Test class/method群 | 原受入証拠 |
|---|---|---|
| G01 build/schema/catalog/browser | GateContractTestの七method：24固定ID/唯一N01 NK_ONLY、DIF001～016連番/狭scope、Source59/Documents18/Master59627/Scenario99661/Video20/Music129、Chromium1187/ja-JP/JST、forwarded header、binary canary、二完全fixture正常。NegativeTestのcontract/schema/catalog/browser/secondary viewport/requirementsのmethod群で誤version/型/順序/重複/欠落/未知group等を拒否 | 当七＋該当負methodの元XML、固定fixture fullhash、実build/format/compile0 |
| G02 完全run/非PASS拒否 | NegativeTestのrun-artifacts、missing-directory、七parameter status、composite、requirement matrix。FAIL/FAILED/FLAKY/SKIP/SKIPPED/DISABLED/NOT_RUNを個別拒否、case/status/key/null/screenshot hash/supplemental evidence必須、N01 metadataだけを既契約で区別 | 同source全17 negative invocation（skip credit0）、Current/NKの実case実行ではない |
| G03 反復・inventory | GateCliTest.repeatComparison...とNegativeTest.reports/composite。28artifact両集合/内容完全一致、missing/extra/change/異inventoryはFAIL | 当元method、独立literal28とdiff集合を明示assert |
| G04 source/baseline/review | GateCliTest.verifySource.../baselinePromotion...、NegativeTest.baseline/reports/actual-commit。UTF8 path順SHA規則、source/master件数/hash、全baseline tree/環境/commit/review必須。legacy843de94 anchorは既元識別だけに限定 | 当fullbyte/原hashと負fixture、原baseline前後同一。レビュー当時QA044/UIC004までの履歴条件を現在QA051全完了へ偽拡大しない |
| G05 狭DIF/未登録拒否 | 子02全5比較Test、NegativeTest.rejections。sequence16/field重複/mode/selector/case/広範囲/未使用等を拒否、DIF015全case契約とDIF001承認済Login scope保持 | 子02受入492と元当negative。過度な正規化/新期待値なし |
| G06 機密・原本・承認 | GateCliTest.reportMaps.../secretScan.../atomic...、binary canary、review/source/baseline negative。fake credentialとJSESSIONID canary検出、raw値をreportへ保存せず、fixture外不変/同出力競合拒否 | 当元Test/原source/snapshot/CRC/session、現Program範囲のsecret/原本契約。大file/runtime全秘密scanをこの限定canaryで代用しない |

GateContractValidatorNegativeTestは11method/17invocationで、parameterized七状態を1成功へ潰さない。全負fixtureは新TempDirのcopyだけを変更し、元Current資料/DB/鍵/実VM/実サービスを触らない。missing optional reportは空objectの後に必須contract checkで失敗し、no-op PASSにはしない。例外/parse失敗/FAIL reportは成功へ読み替えずCLI非0を維持。主入力はcaller確立のPathであり、独立path API負境界はBUG1640の三guardで是正済み。

## 親P020-01の全scopeと非該当

親ownedはArtifactComparator/GateCli/GateContractValidator/TargetAdapterの四Mainだけ（物理8class）。旧485の所有/費/4pathを保ったsource overlay、当原全Main/Test/fixture、全counter、CRC/session/終了証拠へ対応済み。各子のPGは1530～1534/本書で全method/依存/状態/例外/資源を覆い、共有実行は44/5suiteの一回だけを採用する。

evidencePlanの候補15Test中、当四Mainの直接五Testは全件対象。CurrentCharacterizationTestは実Current捕捉、SharedLogProjectionDriverTestとNative...OracleTest群はtests/java側の別capture工具を検証する候補で、所有四Mainの物理scopeではない。これらをfailed/skipped/notrunの成功に算入せず、実capture/再生/接続はN/CHRとQA051の別受入/HOLDに残す。本群のG02/G03は固定された歴史reportを読む工具の判断契約であって、現在の実VM/Current/NKを新たに実行したという認定ではない。

親requirement SCP-004/TST001～005の共通harness・独立oracle・trace/品質契約は上記へ対応するが、PGPT全体/実NK互換/IT/STの完了とは別。全三子と同sourceF02をstrict依存検査し、最後に親contract/scope/qualityを照合してから親1をoriginal190項目の新規として計上する。三子＋親4件を同じ分母へ重複加算せず、親に追加予算を付けない。

正本RD112/181との対応：SCP004は共通自動比較を整備、TST001は保存843de94のNK着手前Current gateとbaseline不変、TST002はUI264の24case/requirements/screenshot/状態・順序の比較契約を共通engineへ接続（当source実NK結果は後続）、TST003は内部class/SQL/physical pathの一致を比較項目へ追加しない、TST004は承認済16DIFだけと未登録/unused拒否、TST005は現行URL/bookmark一致を強制せずDIF015のcontract modeで独立current/nk期待を扱う。原Testの`/same-path`はcontractで差分無しも検査する固定fixtureであり、実Current/NKのURLが同一との宣言ではない。

正式1964/53・歴史17/190・工数率null・QA051 FINAL_HELD/PTALT0/F03 Root11・全actualHOLDは不変。原/v4/v5と各群開始見積を維持し、新Main/Test/原4222再演0。
