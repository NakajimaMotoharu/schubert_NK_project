# Host pure post最小cardinality・工具是正仕様

2026-10-30、BUG2109/YKT1856起票後、群HOST_PURE_POST_MINIMUM_CARDINALITY_V2、主F03/元.5/3/5pp。旧v1は凍結し、一methodへの適用保留を維持した上で新v2を作成する。製品/source/品質・許可scope変更ではない。

修正はduplicate metadata反例生成だけ。一要素なら同一caseのdeepcopyをappendして不正metadataにし、二以上なら元どおりindex1を重複caseへ置換する。既assessのcase数/一意性/失敗拒否は変更しない。全形状・byte/source/session/CRC/所有・metadata/無fixture制約も変更しない。入口で通常の全body審査を省略しない。

14706は元14702 rawを固定参照し、**synthetic metadata**として1/2/8に縮小した三入力だけをassess（実製品選択ではない）。各正常metadata受理、duplicateはValueError拒否、元metadata不変・deepcopy別実体を検証する。v1→v2は意図した関数追加と呼出置換以外の全文一致を要求。続いて既真正14702の原8execだけをv2で再解析し、既14704と全実質値一致を14708で独立照合する。Product再演/新methods/source/coveragecredit0。

元consumer14670/14678/14692/14698/14704の実8/5/3/10/8はいずれも二以上で非該当、元XML/post保持・確認再演なし。metadataかactual XMLかを混同しない。新一method製品試験は本工具資格の後に別途通常判定を必要とし、工具資格だけで実行許可へ拡大しない。

command `PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14706_pure_post_minimum_cardinality_selftest.py`、後続14708。日時/環境/実command/exit/pin/元post参照はmanifest、結果2752。正式・工数・全HOLD不変。
