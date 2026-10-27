# Program ID追記訂正の独立確認結果

2026-10-27 10:13 JST、NK-OPS-001/BUG1903/YKT1654、仕様2167、sourceae55baa85af2174fa01d73b62ad8899d3f44f306。追加発見/文書trace手戻りであり元PG/PT消化・新試験・coverageへ加算0。

11226 actual0、manifest `8174ccc98140462b0f28bd279668657c6f5167acfee215293dd09c39444ff862`。証跡evidence/provisional/PG11226-program-id-correction-post-v1/manifest.json、command=`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg11226_program_id_correction_post.py`、Linux/Python3・lint0後元entry実行、source/hash/工具invocationを同manifestへ保存。メタ検査で製品PT0。

PT-OPS-PROGRAM-ID-META-001～003確認済み。431登録行`018 / NK-OPS-001`を実byte確認・SHA1ee5e867、未登録IDが正本にないことを確認。2157/2161の原sealed SHA0bcc979b/f14de99f、11170/11196の原manifest f6a7798f/7a492037とproducer entry hashを全保持。旧sourceaafcc/34試験と5eeb/46試験の元実結果/FES0を変更せず、effectiveProgramIds=[NK-OPS-001]へ別correspondenceを付与する。両者を合算して新80試験とはしない。

current2165/current11222は正規Programのみ、元32試験のsourceae55/実結果を保持。未知ID/誤source/原hash改変/架空PT増分/旧結果再束縛の五metadata反例を拒否。元製品再演・解析・coverage0、原DB/鍵/保留工具・実環境アクセス0。2167原hash61f8c6f9を新manifestへ結合、元仕様・証跡を書換え0。

全列挙対象の修正又は原保存＋正規対応/再発防止確認済み、BUG1903はMETADATA_CORRECTED_VERIFIED・YKT1654はSCOPE_COMPLETE、完了2026-10-27。修正保存commitは当保存commit（Git履歴参照）へ結合、製品sourceae55は変更なし。正式1964/53・17/190・工数null・全F03/451/QA051final/全安全HOLD不変更。
