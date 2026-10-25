# 全物理class・Codeと空counterの静的確認仕様

2026-10-26、WBS-G01/群2242、開始.5/2/5pp cap10。先行1983-84/PG9828-30と生成CodeのProgram002/020-021を参照。後続の公開資料に全六moduleのCode/空counter構造の完了はなく、旧426空counter/34非XMLの理由を一律非実行と推定していない。本確認はその構造不足を埋める静的品質作業であり、旧4222や成功済み通常PTを再演しない。

current source8ba82083/normalPG9812の全六Jar・1843Mainを固定し、Graph9のTemporaryInfrastructureException/WebStartupException二Mainは名前/hashを既表から参照するだけで、新規class解析をせず明示HOLDへ置く。残1841の既classをJava25 ClassFile APIでdataとしてparseし、class flags、SourceFile、全method名/descriptor/flag/Code有無、fields数を取得する。readerの実行classpathは自己classだけ、製品Jarはdata引数。対象define/load/init/invoke、製品compile/JUnit、agent/VM/Root/DB/JMS/HTTP/鍵/permit/intent/配備は行わない。

独立postは別Python classfile binary decoderで全1841の恒等・flag・SourceFile・method Code属性を照合する。既PG9828の全physical hash/歴史counter/byte分類を固定し、同byte/変更/追加を明示したまま結合する。Codeなしはpackage annotation/interface/annotation/その他を分け、Codeありsyntheticと通常Codeを別分類する。Codeなしも100%測定としては数えず、Codeあり空counterは理由未解明/要適用性確認として残す。過去結果を現source合格へ変換しない。

期待は1843キー完全、解析1841/HOLD2・重複/欠落0、原六Jar/全source byte不変。独立decoderでは各constant pool種別・二slot long/double・Code/SourceFile/切断/不正kind/別entry/余剰byte等の固定metadata vectorを使用し、対象classの実行fixtureを作らない。工具vectorは製品PTへ加算0。誤coverage昇格、欠落class、HOLD混入、誤Code数の拒否も確認する。

成果は全physicalの構造表、module別件数、旧空426/非XML34/新174の内訳、Codeあり未説明箇所の後続対象。標準filter/生成適用性の承認や全G01/451認定は別のまま。正式1964PT/53scope、個別17/190、QA051final、工数null、Graph9動的/全actualHOLD/G074493/全WBS監査HOLDを維持する。source/manifest/hash・実command/exit・失敗/再試行・共有quota観測を結果へ残す。
