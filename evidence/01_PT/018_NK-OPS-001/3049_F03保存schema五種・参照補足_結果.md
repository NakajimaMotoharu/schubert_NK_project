# F03 保存schema五種・参照補足 結果

2026-10-31 / PG-D974 / 群3383。3048の固定五公開inputのみ、Product/PT/scanner/外部/私有raw操作なし。

15938/d34c396e `PG15938-f03-saved-schema-supplement-v1/manifest.json` SHA256 `a907cb510165be0cba32f9700d5efe23248bbe27ba03aa1f0766b75ec69b1218` 真正0。15940/d647f1ee `PG15940-f03-saved-schema-supplement-post-v1/manifest.json` SHA256 `bc0974e4142ae16f9d6ed5af9243c9975e5a55c1a36629803f704d9a3488cb65` 真正0、独立23変異拒否。manifest directoryは全て既存 `evidence/provisional/` 配下、checked entryのcommand/入力hash/生成JSONhash/終了値を保持。

固定schema inputの元row/現Main byte・全属性座標一致は順に：thread2125中243、classloader542中1、protocol10中3、JSON5中4、identity28中28。Test/源byte不一致/現在rawに同座標なしは対象外数としてmanifestへ記録。identity元IDは固定10690へ結びASTと原座標も一致した28だけ、補正推測なし。

原1491raw/283参照を凍結、追加279接続、合計562参照・選択未参照1208→929。参照は既存手動レビューへの接続で新規手動review0、元PT再演0、raw抑制0、PT免除/適用性PASS/旧runtime資格転用0。旧67選択のPG13044別schemaは本群の明示adapterで解決したが、旧15930/33の「当時0row未適用」という証跡は変えない。

独立検査で全五入力/全row/hash、原965byteと1491raw不変更、source/座標/参照hash/schema/旧参照保持/queueを検証。欠落・重複・偽byte・偽座標・未知schema・PASS意味付替え・新review/実PT/受入の偽装等23を拒否。新BUG/プラットフォーム拒否なし。

BUG2152/53・YKT1899/1900実修正commit `6d97a17ea3a8c059ae648ff9297755719c249445`、push77982真正0。有限工具scope完了と、全F03適用性・動的資格の未受入は区別する。

着手0.5/1.5/3共有pp cap10固定、開始50。専有費/N-Tnull、費用/原見積りを新接続数から推定しない。正式1964/53・歴史17/190・工数null・QA051final/451/外部Graph HOLD不変。後続は、現source全Mainのclass/method分母と明示TestIDの不足をstatic metadataで整理し、個別source-methodの未検証を測れる形にする。旧global/whole/nativeを成功確認目的で反復しない。
