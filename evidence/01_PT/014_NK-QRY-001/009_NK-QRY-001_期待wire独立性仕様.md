# 質問照会expected wireの独立性是正

2026-10-26、BUG1811/YKT1562、PG-D678、G03.01（原業務担当P01401/P01403、重複費用0）。関連RD QST005～010/NTF001～012、UI236 §§8/9/11/12、SS323/324、451。製品Main/仕様/oracleの外部期待値は変更しない。

対象はQuestionQueryApplicationServiceTest.expectedとQuestionQueryReplayServiceTest.wire。期待profileはTest入力のQSS/QSD/NTS/NTDから選び、Production request.decode/detailRequest/questionScope/responseLayoutIdでexpectedを決めない。全九内部caller・一外部callerを更新し、元全@Test/assertionと固定byte配置を保持する。新QuestionQueryWireOracleはJDKだけに依存する。

|資格ID|目的/fixture/操作|独立期待/根拠|
|---|---|---|
|META-QRY-WIRE001～024|四profile×0000/0200/0104×count0/1、公開合成UUID100/101、sent=2026-10-01T00:00:01.123456Z、row=00:00:00.123456Z|UI236の項目幅を順に連結するPython実装で24whole-byte hashを生成。Java helper/Productionをexpectedへ呼ばない。JST時刻は固定文字列。|
|META-QRY-NEG001～005|未知profile空/response名/未知名、count-1/2|IllegalArgumentException。helperは既fixture0/1だけを表す。|
|META-QRY-ISOLATION|返却配列の先頭を変更後、同入力を再生成|先頭S、共有配列を返さない。|
|META-QRY-SOURCE|当二Testの元token/assertion/byte配置と新helperの入力依存、正常六module全class差分を比較|元assertion保持、宣言したprofile選択変更だけ、全Main1843byte不変。|

commandはpg10282_query_wire_oracle_metadata_v2.py（javac-proc:none、helper＋metadata runner二sourceだけ、classpathは自己readerのみ）とpg10284_query_wire_oracle_six_compile.py（-DskipTests、六module正常compile/NullAway）。pg10286がmanifest/hash/source/元byte配置・全classを独立結合。各工具はtools/quality、実際のcommand/version/exitは公開manifestとstageログhashに保存する。

元業務PT（qry013～026など）はDB/key/例外graph等の既HOLDを含み、今回NOT_EXECUTED_HOLD。上記METAはoracle資格で、製品PTのPASS件数・新Test ID・実測coverageへ加算しない。正常業務/再送/例外/null/並行/DB整合の元試験を代用したことにしない。並行性は当純関数に共有可変状態なしのsource確認のみ、元サービス並行PTは未実施。coverage未測定、451四100/全scope/source/run/正式認定は未更新。

静的PG10280 raw29/CS0/exit1を保存。BUG1812/YKT1563起票後、新helper重複questionだけ同値定数へ是正。PG10281 raw28中既二Test19重複は未是正、他九文脈は結果文書へ分離、全静的合格とはしない。修正前V1 metadata24成功は履歴、整形/定数化後のV2当SHAへ改めて資格結合するが新製品実績へ重複加算しない。
