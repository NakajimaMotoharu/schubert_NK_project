# 全物理class・Codeと空counterの静的確認結果

2026-10-26、仕様1987/群2242/WBS-G01。source8ba82083ec65abc6373b8454576dcbaee7d3e621、Main最終e598、normal9812。**1843物理classの全キーを保持、1841を二つの独立parserで構造照合、Graph9二Mainは新規解析せずHOLD**。これは静的な構造確認であり、製品PT/coverage/新規正式受入は0。

|現在の構造|物理class数|意味|
|---|---:|---|
|通常Codeあり|1388|Codeがある。実行/coverage資格を推定しない|
|synthetic Codeあり|19|compiler生成switch helper。適用性承認・全probe到達とは別|
|Codeなしinterface|397|全method Codeなしを二parserで確認。100%測定数に加算しない|
|Codeなしpackage annotation|37|field/methodなし、Codeなし。100%測定数に加算しない|
|Graph9 HOLD|2|TemporaryInfrastructureException/WebStartupExceptionのbinaryは未解析|

原e7/4222/660のcounter空426は**Codeなしinterface395、synthetic Code19、通常Codeあり12**。非XML34は全てCodeなしpackage annotationだった。追加174の内訳はCodeあり169、Codeなしinterface2、package annotation3。各件の恒等・原/current hash・byte分類・原counterを消さず全表へ結合した。したがって空counter426を一括で非実行code/100へ変換することはできない。元未到達109・現同byte1660/変更9/追加174・旧成功のsource区別も変更なし。

通常Codeあり12の構造は、InvalidMessageのprivate空record6、AccessRejected等のprivate空constructor6（Media/Scenario/ScenarioFileWriter.Attempt/TransferStartupProbe.Ownership/MorningBackupUnitCycle.Unresolved/JdbcWebSessionStore.InvalidStoredRow）。method/descriptor/Code lengthは表へ保存したが、標準filterの適用機構・生成/空constructorの要求coverage非影響・review承認は本確認で認定していない。19synthetic中Protocol4/16missはProgram002/021で静的対応済み、他15は未実施の後続として区別する。名前だけで免除せず、必要なら固定filter/原bytecode/元execの対応を別群で確認する。

## 方法・証跡

primaryは自己readerだけをcompileし、Java25 ClassFile APIで既六Jarをdataとしてparseした。対象Jarを実行classpathへ入れず、classのdefine/load/init/invokeなし。独立postは別Python binary decoderでconstant pool/flags/SourceFile/全methodのCode属性・lengthを全1841件照合した。原Code byteは実行しない。Graph9二件は両parserでZip entry名を見てskipし、class bytesの解析なし。新製品compile/JUnit/VM/DB/JMS/Root/HTTP/鍵/permit/intent/配備/署名/実process介入0。

以下は本Programのevidence/provisional配下。各manifestに元source/hash、実command/時刻/JDK25.0.4/exit、工具hash、除外・coverage・受入非昇格を保存。

- PG9848-main-code-structure-v2/manifest.json：a2b6e797428c46e7940de9e224d044b58c30233388d019c903e74fdce51876d4。`python3 -B tools/quality/pg9848_main_code_structure_v2.py`、reader Werror compile0/metadata読取0。class-structures.jsonが全1843表。
- PG9850-main-code-structure-post-v1/manifest.json：995f0f16fdc8b9df3daf40a5ba19768ac9dfcf70c2e0d4f96fb4d15ea20b953e。`python3 -B tools/quality/pg9850_main_code_structure_post.py`、exit0。independent-structures.jsonが別parserの全1841表、historical-noncounter-structure-summary.jsonが上記内訳。35固定metadata vectorと8誤claim拒否は工具品質検証であり製品PT件数へ加算0。

BUG1768/YKT1519：初回pyflakesが未使用_superを拒否（exit1、当source sha8791cfa3a0084e1ddbe2d13d71dfed11c3003d314a3e7cb544aa98c5917fb9ff）、selftest/reader未起動。起票後にsuperclassの非0 Class参照を検査する実装へ修正、他this/interface/catch/SourceFile参照の型契約も全実データと正常/不正super vectorで確認した。

BUG1769/YKT1520：V1はCodeModelとCodeAttributeを混同しcodeLength()がcompile1（18:17:45UTC）、readerは未実行。V1 helper原sha21085101/工具f603c21c/元namespaceとreceiptを保持し、別V2でAttributes.code()へ変更した。過去のcode().isPresent()だけのreader群はlength呼出しがなく非該当/再演0。原compiler stderr/exitはPG9850へ回収、Code有無/長さ・abstract/native・欠落/重複/余剰等のmetadata vectorと独立全1841methodで是正を確認した。二障害は工具scope検証済み保存commit待ち、失敗や工具修正を元計画消化へ加算しない。

正式1964PT/53scope、個別17/190、QA051final、工数null、全actualHOLD/Graph9動的/G074493/全WBS監査HOLDは不変。除外設定/到達不能扱い/標準counter変更0。全G01/451は未受入であり、全source/全run/native/CHR/静的/trace条件の代用ではない。
