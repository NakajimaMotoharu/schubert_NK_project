# 5836 認証SpotBugs収集の診断と名簿

003の正式収集に属する純XML処理、451、BUG-3804、YKT-2958。元正常の局所API32 class XMLを読取り、変更はメモリコピーのみに限定する。実認証、鍵、実DB、製品JARの再解析、保留範囲に接続しない。

| Test ID | 入力差分 | 期待 |
| --- | --- | --- |
| PT-OPS-F03-AUT-SB001 | MissingClassを記録 | 拒否 |
| PT-OPS-F03-AUT-SB002 | 欄外にErrorsを追加 | 拒否 |
| PT-OPS-F03-AUT-SB003 | ClassStatsを名簿外の名前へ置換 | 拒否 |
| PT-OPS-F03-AUT-SB004 | 同名のClassStatsを追加 | 拒否 |
| PT-OPS-F03-AUT-SB005 | 欄外にBugInstanceを追加 | 拒否 |

既正常32classは指摘・欠落・エラー各0で受理。対象source、元XML、独立before/after、終端をPG44596に保存する。製品PT・全451・正式受入に加算しない。
