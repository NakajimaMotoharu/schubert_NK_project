# UTF16原token座標の独立再照合

NK-OPS-001/F03、PT-OFFSET-UTF16、BUG1321/YKT1087。Main7fff/元source4c9は不変更、同時にPG3734の固定snapshot e63f01649を変更しない。

期待：JDKのsource start/endをUTF16単位として厳密に読み、nonBMP prefixがあっても元tokenへ結合する。型/負/逆/範囲外/surrogate分断は拒否する。

before=c738da449、private PG379/pg3742-utf16-before-v1。独立literal「//emoji\nint permission=0600;」のUTF16位置20～24にPython codepoint sliceを適用すると600;、期待0600と異なることを修正前に保存。実DB/VM/Productionの不正受理ではない。

source_utf16.source_sliceへ是正、ASCII/日本語/非BMP・empty/両pair境界/unknown型等の独立純1 PASS。consumerの他対象はJava内/JDK LineMap/UTF16そのままrequestか既UTF16 byte処理で非該当。旧成功試験や候補を再演しない。

別読取post PG3742-octal-offset-post-v1は元3736全187vector/30原Git fileを厳密UTF16で照合actual0。元30fileの非BMP0、旧座標の実不一致0、全元vector有効・公開原manifest不変更、元snapshot巻戻し0。manifest **e39cd807170504f76c3c4eaf942fda739feb4c18068f850ceaf9295950352926**、元vector SHA f93c9de072413cd44f71e0c621f8088443c6921840d4eb3027e5336d6773922b。

実行commandは `PYTHONPATH=tools/quality python3 -B tools/quality/source_utf16_test.py` と `PYTHONPATH=tools/quality python3 -B tools/quality/pg3742_octal_offset_post.py`、両exit0、JDK25.0.4由来の座標・Python実数値/原Git sourceを使用。Production PT件数・受入・F03・coverageへの加点0。
