# 動画Range補助確認の定義単体仕様

NK-CHR-001、UI264 CHR-M04、SS355 §5・§9・§11 CHR-G01、BUG-3813／YKT-2971。ProgramはGateContractValidator.validateDefinitions／validateRequirements。PT-CHR-DEF-MEDIA001は固定公開定義のコピーだけを使う。

| 入力 | 独立期待値 |
| --- | --- |
| CHR-M04の補助確認が通常200だけ、複数Rangeの最初だけ、行自体なし、または別名で置換 | 各入力で `REQ_VIDEO_RANGE_SUPPLEMENTAL` 1件。UI264に二つの観測が明記され、承認済み定義の各登録キーと対応する。 |
| 承認済み固定定義 | 診断なし。定義・baseline・DIF・期待識別値の変更0。 |

実ブラウザ、実HTTP、実データ、遠隔接続なし。修正前の同fixture失敗と、是正後の既許可独立工具一式、規則と対象ファイル、同一局所execのraw、正規包装の結果を実行票へ保存する。製品PT・実CHR・正式受入の集計は別。
