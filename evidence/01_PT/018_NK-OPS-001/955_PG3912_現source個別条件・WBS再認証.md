# PG3912～3918 現source個別条件・WBS再認証

NK-OPS-001 / SS343・354・451 / WBS-G13。Productionは7fffab57a567914956b66452e5e54388642efdec、PG3748。管理工程でありProduction PT追加0、正式1964PT/53scope・工数完成率null・QA051final保留を維持する。

| Test ID | 独立根拠・期待値 | 実結果 |
|---|---|---|
| PT-WBS-3912 | PG3738真正3714件/545suite/1643MainとPG3892実20point/18streamの六XML、全941歴史Git blob/現byte、runtimeの元独立receipt | actual0、物理変更260・owner変更0。残642L/128M/5C/462B。session情報だけredact、counter不変更 |
| PT-WBS-3914 | 固定Test byteと元全回帰XMLのcase識別子を照合、期待値をProductionから生成しない | actual0、65suite/389case。再実行0 |
| PT-WBS-3916 | 既存17項目/51criteria、19変更artifactの独立oracle/同source四counter/終了依存/主担当 | actual0、17/51再認証。新受入leaf0、共通費重複0 |
| PT-WBS-3918-PURE | 全既存status・受入履歴保持、941artifact、484予算byte不変、不完全条件/owner/hash拒否 | pure2成功。TDD失敗なし |
| PT-WBS-3918-STAGE | 現四正本hash一致・new-only候補・strict全audit | actual0、17受入、97counter閉鎖/18gaps |
| PT-WBS-3918-APPLY | journal/旧hash/候補hash一致、481/485/486だけ機械反映、正本audit | actual0、新受入0、190元ID/252費用leaf/281RD/941artifact/64layout/24画面/未割当0 |

公開manifestは `evidence/provisional/PG3912-current-wbs-measurement-v1/manifest.json` (a5af5cdb4dee05a4fc0aef154966191704d7dedf6b66437500a909fb56f38f7d)、3914 (5b0ea56c952e202527ec846158b63381927247fa8aaeffaaefef3adce157e1f3)、3916 (8541cfd7b1ff48ab4c1ae0b25129f7af4a54702fda1e452f82aa5fe9672a97ce)。3918元stage/apply/hash/候補/旧正本は作業領域PG379/pg3918-current-wbs-source-switch-v1へ保持。Linux/Python3、完全PYTHONPATHで対応script、stage/applyは固定189da545d。全command終了0。

旧source測定は履歴として保持し、新sourceへ算術合算しない。N05～10/N14は有限実経路のVM_STEP_VERIFIEDだけでleaf受入ではない。N11/12/13/CHR-A01は今回未結合を明記。N14退役費の主担当はevent0981訂正どおりN14、N12参照費0。F03 raw1840/技術278/未分類1562・適用違反数null/F03未受入。生DB/鍵/原本Backup/native/raw sessionの公開0、VM/Root/stop/全回帰再発行0。
