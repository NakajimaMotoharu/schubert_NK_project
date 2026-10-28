# Scenario最大snapshot純memory・実行結果

仕様2414/PG-D774・event2780、正本owner P00805。現在source5c378e064f0f8a7366316d4afa28fbb2cd9cec81は新Test一つだけ、Main/全旧Test不変更・未配備。最大10000 immutable snapshot、中間/末尾sequence gap、10000件目本文4097byteの新whole3/一suiteは同一source/runで全成功、FES-aborted/container失敗0。実DB/query/FS/file生成/Root/native/Graph9/鍵操作0、snapshot後のFILE配信やIT/ST成功にはしない。

## 旧失敗と期待値是正

旧source0a8485983/13098は3実行・最大受入1成功/異常系2 AssertionFailedError、真正終了1のまま保存。旧XMLは実cause class未exportなので、旧runで正規型を直接観測済みとは主張しない。BUG2025/YKT1773を修正前起票、SS322§11のbyte超過FieldEncodingExceptionと既immutable semanticのLayoutValidationException契約を独立照合し、誤指定したPermanentProtocolException/MessageEncodingException二種だけを訂正した。Mainや上位仕様・入力/byte/拒否要求を変えず、RuntimeException等への広い期待緩和0。

旧Test全文/元失敗はPG13100（manifest4c9db4bb）、旧2414全文/hashはPG13101-snapshot-spec-original-v1へ保全。13102/13104/13112は原954tokenへの完全逆・七非同値反例で、二import/二class指定以外の入力/操作/assertion形不変更を照合した。訂正sourceの全3を再実行し旧成功一つも転用0。これは新規成果3に加えて旧3の追加source再認証1回という手戻りであり、6 unique試験や4 unique合格と数えない。

## 同source実行・独立証跡

各entryは `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/<entry>.py`、bind前pyflakes0。JDK25.0.4/Maven3.9.12/JUnit1.13.4/JaCoCo0.8.15、時刻/OS/branch/source/command/終了code/SDK・工具hashは各manifest begin/invocationを正とする。以下はProgram018/evidence/provisional配下のmanifest.json。

| Run | SHA256 | 結果 |
| --- | --- | --- |
| PG13096-snapshot-max-six-compile-v1 | d4de109ab5b3b31ddedc8bd2fd854fe44cbc95f9cbfb95a08f775326cf3ffad1 | 旧candidate normal0/PT0、旧source維持 |
| PG13098-snapshot-max-host-v1 | bdc508fa33f1ccb731cd62427bc7b3190a91d4ad28f5d40bf2f31a766b74b27d | 旧3/1成功2失敗、actual1保持 |
| PG13100-snapshot-oracle-originals-v1 | 4c9db4bb5ddf53982ac6778a801a57a12ec84ce1ce55d37765ec1328f733a861 | 旧全文/失敗とtaxonomy根拠保存 |
| PG13102-snapshot-oracle-preflight-v1 | 31581f6939034eaabe3df2a9fe8aa590bc0ce5c289d3ec48e70542f2b61f7b95 | 954token逆/七反例・局所static0 |
| PG13104-snapshot-corrected-plan-v1 | 03bc1cd8dc48f66167728284be8e5a5d04f32aea515ff3d07119dec4c66f9cd8 | 同入力/全3・一suite固定 |
| PG13106-snapshot-corrected-six-compile-v1 | 0d052046bbfe7586c491f1cb398566301fae8d958c0e2ae3e660d477961c12c7 | 訂正source六normal0/PT0 |
| PG13108-snapshot-corrected-host-v1 | 776be8fff9f5c812c557a02f2198313adf8f506f2f88fea1c809e200911b525a | 全3真正0・一session PG13108-SNAPSHOTMAX-JP |
| PG13110-snapshot-corrected-static-v1 | 882dbee6518ab17fe8410add62aa8d228b7acd9181f0ab6f65f69a795a777f0e | SUT/新Test二source PMD-CS0/六SB0 |
| PG13112-snapshot-corrected-post-v1 | 2e506ef62e654842ad448b38aa0a61f90b26ebaa98e3b84f42df50d221f07c9d | XML/exec/CRC/全artifact/全旧byte/原逆独立0 |
| PG13118-snapshot-max-trace-v3 | 2fcf6b839ebf0cf918f81573491f82bd54a54b09184c2f685b28fee74343a83f | 旧992全field＋新一owner P00805/993row |
| PG13119-snapshot-max-trace-post-v3 | 388e6b5195ae17954975db2b46a78fed7a436dafc9b35e88484a272a95dbabb1 | 九反例・原WBS/owner-cost/旧runtime保持 |

訂正源SUTはline17/1・method2/0・class1/0・branch4/2 covered/missedで、mode/件数shapeの未実行branchを保持し四100未達。全API artifactはline17/12722・method2/1840・class1/364・branch4/4818、他五artifactも完全分母・未達を保存。既定enum/record filterだけ/手動除外0、旧NULL/10001/FILE-modeケースを抜き出して未達を埋めない。

全1843Main/旧1972Test class同byte・新一physicalだけ、全source/SDK/工具・唯一classpath定義/実Testclass pre/post同hash、全3XML/一exec・CRC/六完全artifactaccount、own CWD空・SUT以外全API/persistence query等probe0、許可外module/driverロード0を確認。最大10000を実メモリで受入れ、caller配列変更/clear後の末尾まで保持・返却変更拒否、中間/末尾の非連続sequenceと末尾field byte拒否を確認した。HTTP/DB後条件や実fileのbyte/hashを確認したとはしない。

## 工具手戻り・残条件

BUG2026/YKT1774は13114の旧case6 guard、BUG2027/YKT1775は13116の旧physical1968/新2 guard残留。両元entry/失敗を不変更保存、いずれもOUT/485486変更前に止まった。全文の異なる分母を点検し13118ではplan/観測3・suite1・旧Test1972/新1・Main1843・旧registry992/新993・Java1820/登録1818/UNKNOWN二を各意味別に一致照合、13119でcase/physicalを含む九非同値反例・原semantic/全担当費まで確認した。既3PT/build/static/coverageの確認再演0、当工具範囲限定完了とする。

BUG2025/YKT1773のPT期待層も当source全3/独立postで限定完了、修正source5c378e064・保存push456参照。PT oracle不備1、bind済み工具不備2、metrics command不正分類REWORKのguard拒否手戻り1（event未追記のままIMPLEMENTATIONへ是正）、追加source再認証1・製品Main不備0を分ける。cloneによるcount残留が反復したため、次の工具群では既plan/proofの分母schemaを事前照合し複製固定値を減らす改善を460へ残す。

原2/5/9cap10・新窓開始1→直近2/reset1793774153は共有観測のみ、NT/専有費/工数null・元/v3/v4/v5予測不変更。raw8461/corr964/introduced16・参照3259pending961は前sourceから不変参照、新Test static0と旧全input/byte不変から新finding/原是正加算0、全global再解析0/actualViolationCountnull。registry993/Java1820登録1818/unknown二、全WBS auditはactual1/HOLD、正式1964PT/53scope・歴史17/190・新個別受入0・工数null/QA051final・全actual/保留二工具/全原本は維持する。Program008/evidence/snapshot-max-memory/manifest.jsonへ新3 IDと当source/run/文書hashを結合する。
