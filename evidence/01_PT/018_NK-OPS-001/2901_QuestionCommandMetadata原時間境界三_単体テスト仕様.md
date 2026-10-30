# 2901 QuestionCommandMetadata原時間境界三・単体テスト仕様

WBS-P011-03、Main QuestionCommandMetadata/constructor/at/messageId/correlationId、元PT-CMD-TIMEBOUND001～003・SS332351/PG-D331。source6b53/normal14216、Mainc62cea83/Test0d2b3fd7、全body/initializer/helper読了、現1777/371Sourceには原3/当Mainとも未登録。独立lower=0001-01-01T00:00:00Z、upper=9999-12-31T23:59:59.999999Z、固定架空UUID1711/1と1711/2。

001 lower本体/＋999nsはlowerへfloor、－1nsは拒否。002 upper本体/＋999nsはupperへfloor、＋1000nsは拒否。003 preepoch1969末999999999nsは999999microsecond、epoch後1nsはepochへfloor、両message/correlation固定UUID保持。期待は明示ISO literalでproductionを呼んで生成せず、独立整数時間計算でもnanosecondを1000単位floorして確認する。近傍負値/境界・正常異常が適用、並行/再送は不変値で対象外。

PT_DEFAULT、純record/UUID/Instantだけ、外部IO・権限・DB/JMS・process・Graph/native/実起動0。関連QuestionCommandServiceTestは@BeforeAll実DB・故障Graph依存を確認しwhole保留、null/redaction部分の抽出や新fixtureへの迂回0。その契約は未実行として明記し原3のPASSへ含めない。Main toStringは原3で呼ばず全Source counter未達になる見込み、除外/人工呼出/別exec unionで埋めない。

command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15362_question_time_three_pt.py。固定normal全input/実Jar全一class/snapshotと原Testをpin、一つのfresh自JVMでwhole3を実行してXML/exit/FES/一sessionCRC/環境保存。sharedpost v2の無fixture/全Code/API namespace/baselineMainP01103-TestUNKNOWN閉shapeで全Source分析、独立postは原3XML/ISO literal/UTC整数floor/元sourceと全counter・未達を照合。結果2902/manifest、群3295開始0.5/2/4pp固定・実費/token不明null、正式/受入/工数/HOLDは不変更。
