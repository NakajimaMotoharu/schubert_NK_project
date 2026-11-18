# CHR-S08 複数voice補助比較の単体仕様

NK-CHR-001、ArtifactComparator.compare、DAT-004、UI223 §4・UI264 DIF-009、SS355、WBS-P020-01.02/2、BUG-3333／YKT-2699。Currentの正本合成例は、保存済み supplemental.json の multiple-voice-fixture。二リンク、二player、行2、本文2の独立証拠がある。NKはUI223の同一entry内の全player維持・本文重複なしにより二リンク、二player、行1、本文1。通常S08は既存の主artifactで比較する。

比較工具の観測envelope multipleVoiceEvidence.current/nk に四つの整数フィールド linkedVoiceCount、renderedEntryRows、renderedBodies、renderedAudioPlayers のみを記録する。補助観測でDIF-009の成立を確認する。主artifactの別フィールド、表示順、ファイル名等の変化は未登録差分として追跡する。

| Test ID | 手書き観測 | 独立期待 |
|---|---|---|
| PT-CHR-DEF065 | 補助双方が期待値、通常S08の両artifactは同一 | 補助差分成立、通常差分なし |
| PT-CHR-DEF066 | 補助欠落、未知の第三側、又は元DIF行欠落 | 各独立不足を拒否 |
| PT-CHR-DEF067 | NKで二playerを残すが、行又は本文それぞれが重複 | 拒否 |
| PT-CHR-DEF068 | NKのplayer又はリンクが欠落、又は整数の代わりに文字列 | 拒否 |
| PT-CHR-DEF069 | Current側の本文数を意図せず1に変更 | 元観測不一致 |
| PT-CHR-DEF070 | 通常S08の別フィールドをDIF-009として申告 | 不許可として未登録差分へ保持 |

元192を含む工具全198、元Current27変更なし。保存済みのCurrent補助実観測は再演しない。NK実Browser、fixture作成、DB操作は別の実証。二リンク・二player・同一entry・本文・順序の実証を別の判定依存として追跡する。
