# F03既存同source文脈六五の照合仕様

NK-OPS-001/F03、Main28af、913の原.25/.75/2pp cap3 ordinary。目的は既存同一sourceのレビュー根拠を発見し、重複読取・再演を減らすこと。分類/受入はこの群で増やさず、旧sourceのruntime成功を移植しない。

PT-OPS-REUSE65-001: Git tracked public review.jsonのうちcontext/thread/volatile/monitor/mapsをdirectory名に持つ65件（現197/198/199系を除外）だけを読む。元801 remainingへpath/rule/全attributes/whole-source SHAを厳密対応し、JSON row pointer・旧review/manifest hash・reason有無・manifest直接review hash宣言を記録する。該当しないschemaは未評価であり、全旧history網羅を宣言しない。
PT-OPS-REUSE65-002: postは全65のfile hashと各candidate pointerを独立に辿り、元remaining rawとの一致を確認する。候補は全件current semantic review requiredとし、既存根拠の直接宣言hashがないものや理由なしは資格済扱いしない。
PT-OPS-REUSE65-003: 前690+新分類0+残801=元1491の独立完全partition、unique1439/duplicate52組とMorning残12(7/4/1)保持。全Main/POM/normal19740-SB19742/JAR不変を確認する。Expectedは既公開metadataと原rawであり、production methodや旧Product試験を実行しない。

実行順: 023 metadata run 034config→033 run→033 post→023 metadata post 034config（全てenv PYTHONPATH=tools/quality python3 -B、入力は同input directory）。未使用PG19940/Pythonmetadataのみ。意味分類・現行設計の照合は次群で行うため本群newClassified0/新leaf0/技術46/正式1964-53/工数null不変。Product/fixture/graph/DB/JMS/Root/VM/PT/analyzer再演なし、coverage未測定/全F03・451未受入。3550/manifestへcommand/日時/HEAD/hash/終了を結合する。
