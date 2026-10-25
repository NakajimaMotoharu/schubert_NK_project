# G13 method case識別子と既存PT仕様行の明示照合

2026-10-25 17:35 JST、G13_EXPLICIT_CASE_ROW_JOIN_V1、主G13.07。fresh08:35:08UTC使用5/残95/reset1793513544/secondarynull、開始.5/3/8pp/cap10。現Production64446不変更、入力は9592の5622宣言/全exact対応と、保存HEAD854c8b6e2cee973939fdffa05cca9121d6f9450cに存在するProgram直下・ファイル名に「仕様」を含むGit管理Markdownだけ。

method名先頭のletters＋三桁＋終端/大文字/underscoreに合うcase token候補は3344宣言/3204token。各既存仕様のtable第一cellに明記された完全Test IDから、そのcase tokenが完全又はhyphen境界suffixとして一致する行を集める。range省略行は展開せず、alias/番号差/語形変換を推定しない。source class前Javadocに仕様番号が明記されている場合は、その既存仕様番号とcase tokenの両方で候補を狭める。

成果はmethodDeclarationKey→case token→既存spec path/hash/line/row hash/Test IDという参照である。一意のsource明示docref付き、一意のglobal候補、複数/未対応を区別する。期待値の本文はProductionから生成せず、元仕様行を改変しない。この照合だけでassertion/oracleの意味的正しさ・現在PT成功・受入を認定しない。既存header108等の明示method対応は別種であり、method名にtokenがないからoracle不存在とはしない。

producerは固定corpus/current Git hashと厳密token境界で候補を作成、独立postは別method token parser/table ID parserとsource docref/全候補再計算・負vectorで照合する。証跡は公知method名/既存Test ID/公開文書path/hash/line/集計だけでcandidate秘密値/私有rawは保存しない。対象class/compiler/JUnit実行0、読み取るものは既存公開source/仕様/metadataだけ。元4222/完了試験再演0、実Root/VM/native/DB/鍵/intent/permit/配備・拒否未特定操作HOLD維持。

5622の静的分母/既23method対応は保全し、今回新しく対応候補を得た数と未対応数だけを報告する。新Test ID/Main/実PT/coverage/正式増分0、file責任1781/1789/残8・正式1964-53/17-190/工数null/QA051final/G07残4493/全current WBS audit1HOLDは不変更。開始予実/原/v3/v4/v5を保持し、通常小群で止めず許可PG/PTへ継続、fresh現在窓残10以下等だけで保全する。
