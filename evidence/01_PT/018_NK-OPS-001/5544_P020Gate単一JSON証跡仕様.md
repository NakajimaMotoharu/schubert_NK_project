# PT-CHR-SYN007 比較ゲートが読み込む証跡の文書終端

WBS-P020-01.03/2、NK-CHR-001、UI264、SS355のG01／G04、GateContractValidator.read、BUG-3441／YKT-2753。PG40658と同じ隔離合成fixtureをTestのTempDirにコピーする。合成のgate-contract.json以外は元入力を保持する。通常、末尾空白、同ファイルに二つ目のroot JSONを置いた場合を比較する。

- 一つのJSON文書＋改行、スペース、タブは通常のPASS。
- 一つ目のJSONの後に別の空オブジェクトが続くときは、文書全体が単一JSONでなくIOException。成功値が返らないことを確認する。
- 元の20 suite／210比較工具ケースと新1件を変更後の一回の試験で確認。JUnit XML、終了、sourceと原票hash、実測scopeを保存。実FileStoreの同候補資格、実Current／NK、Browser、DB、実CHRは別。Current baselineのGit treeを保全する。
