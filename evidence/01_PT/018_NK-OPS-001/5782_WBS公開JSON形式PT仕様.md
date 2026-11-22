# WBS公開JSON形式の確認

WBS-G08、SS354、451、BUG-3674、YKT-2888。PT-OPS-WBSJSON-001。対象は580の共有JSON構文確認と固定485／486の参照値。

合成文書の一方に NaN／Infinity／-Infinity を直接書き、参照hashは独立に計算する。両文書を順に対象とし、作業ツリーとGitインデックスから同じ固定構文エラーで拒否することを確認する。既存正常文書は同じhashを返す。

`PYTHONPATH=tools/quality python3 -B -m unittest discover -s tools/quality/tests -p test_wbs_index_binding.py`。修正前12拒否漏れ、修正後5テスト成功・負例12。実製品を起動せず、全451は未受入。[PG43134証跡](evidence/PG43134-g08-publication-json-number-literals-v1/manifest.json)。
