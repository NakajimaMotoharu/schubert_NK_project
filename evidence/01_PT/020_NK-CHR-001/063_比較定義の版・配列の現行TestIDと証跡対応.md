# 比較定義の版・配列の現行Test IDと証跡対応

WBS-P020-01.02、SS355 §5／§8／§10、BUG-3477／3481、YKT-2773／2777。書式・独立期待・操作は元仕様060のとおり。現行Test IDは次の表を正本とする。

| 現行Test ID | Testクラスとmethod | 独立期待 |
| --- | --- | --- |
| PT-CHR-DEF079 | ArtifactComparatorTest.rejectsUnrecognizedComparisonDefinitionVersions | 不正な版に CATALOG_VERSION、DIF_VERSION |
| PT-CHR-DEF080 | ArtifactComparatorTest.rejectsNonArrayComparisonDefinitions | 配列位置のobjectに CATALOG_CASES_NOT_ARRAY、DIF_NOT_ARRAY |

060～062とPG41284の該当二methodのDEF077／078表記は上表へ読み替える。従来のDIF-015のDEF077／078はPG40132の原対応を維持する。元の試験source、実行結果と証跡は保全した。

[元の試験仕様](060_比較定義の版と配列の単体仕様.md) · [元の試験結果](061_比較定義の版と配列の実行結果.md) · [元の包装実行](062_現包装工具のローカル216実行結果.md) · [ID訂正と元JUnitの独立照合](../018_NK-OPS-001/evidence/PG41332-p020-comparator-test-id-correction-v1/manifest.json)

PG41268 v2は二methodの異常未拒否を記録。PG41270／274は両methodの合格。包装付きのPG41280の元JUnit全216内にも同じclass/methodが各1件、失敗・エラー・skipなし。PG41282の独立受領と同一sourceに結合した。追加実行と正式加算は0。実NK・実FileStore・全451は未成立。
