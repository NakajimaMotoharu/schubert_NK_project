# Protocol現候補の全単体試験

対象はNK-PRO-001〜003、RD SYS-011、SS311・322・323・354。製品Core `e7bfd5e1f2ec4b4e16ecf32601bed052b5330461`、試験は実行manifestの `source` に固定した。開始前に旧[全体仕様](102_NK-PRO-002_SSC451452全Protocol単体テスト仕様書.md)と、Git上で追加された4クラスだけを照合した。

| 対象 | 独立期待値の根拠 | 試験数 |
|---|---|---:|
| 元全体 | 旧仕様と独立golden、元XMLのclassname・method全件 | 156 |
| LogSearchWireUnicodeTest | SS323の固定テキスト位置、UTF-8/NFCと空欄区別 | 2 |
| QuestionNotificationWireTest | SS323のQSS/NTS各位置とUTC、未知値と期間境界 | 4 |
| UserCommandWireUnicodeTest | SS323の256バイト固定欄と次field、切断surrogateと非NFC | 4 |
| UserListReplyWireTest | SS323のUSRRSP01 Username 64バイトと次field、空欄と文字境界 | 4 |

Maven 3.9.12、JDK 25.0.4、fresh隔離Protocolツリーで module POM を指定し、offline `verify` を1回実行。親のNullAway／Werrorを適用し、テスト・JaCoCo・SpotBugsの終端は0。39 suite、成功170／失敗0／エラー0／skip0／未実行0。Test IDの実行照合キーは既仕様と同じclassname・method。追加14の宣言と保存済み元156の両方を現XMLに照合した。

現Maven JARと製品候補JARの全176 classが同一。単一execを独立CRCと非フィルター解析へ入力し、line 3,638、method 1,432、class 162、branch 1,078、instruction 20,347の未到達はすべて0。Codeのない14物理は本文と一覧に保持。SpotBugsの指摘、欠落、処理エラーは各0。旧execの結合、手動除外は各0。別moduleの同等性、全製品451、正式PT合計は増やしていない。

PG40600元終了、PG40602独立SHA-256 `94b3c550c89f0903370ef0f2544e011cf74341ae309c3eff880843e3942cc6f7`。元の独立検証停止と修正はBUG-3391（PG40601）。製品Mavenの再実行は0。
