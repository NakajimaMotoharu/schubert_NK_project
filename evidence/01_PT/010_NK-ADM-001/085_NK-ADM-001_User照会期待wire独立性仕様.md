# 利用者照会expected wireの独立性

2026-10-26、BUG1814/YKT1565、PG-D679、G03.01（原業務担当P01001、関連追加費0）。関連RD FUN009～013、UI236 §§3/5・UI232共通header、SS321/324、451。Production Main/外部仕様不変更。

対象UserQueryApplicationServiceTest.expected/15site、UserQueryReplayServiceTest.wire/実14内部caller、adm045の七fixture選択。先行記録13は行内grepが折返し一件を見落とした履歴、実装前に14へ訂正。元list/detailを明示形式文字列で渡し、独立helperの固定USR/UDT mappingで長さ・response layoutを選ぶ。App input headerのimmutable layout/ID/contextはTestが構築した元入力であり、SUT UserQueryRequest.decode/detailRequestではない。

新UserQueryWireOracleはJDKだけへ依存。元byte配置・元全@Test/assertion・非profileの全処理を保持する。adm045はTest側booleanでrequest factory/保存error/負例profile/幅/ページ条件を選ぶ。元七SUT判定をそのbooleanへ替え、誤ったProduction判定を期待へ流用しない。

|資格ID|fixture/操作|独立期待と根拠|
|---|---|---|
|META-USR-WIRE001～027|一覧0/1/50件、51件中2page、total49999950/page999999/count50、明細ID1/999999999999×optional false/true、各0000/0200/0104|UI236の各幅を順次連結する独立Python。PAGEDのpageCount/from/toは各fixtureの明示算術結果1/0/0、1/1/1、1/1/50、2/51/51、999999/49999901/49999950。Java helperやProductionをexpected生成に呼ばない。|
|META-USR-NEG001～003|空/UDTRSP01/未知request layout|IllegalArgumentException。|
|META-USR-ISOLATION|取得byte先頭変更後に同入力を再生成|先頭S、配列非共有。|
|META-USR-SOURCE|旧二Test/元byte配置と新source・全normal classを比較|14caller/七fixture条件だけを明示逆変換、五同値定数を展開し元token全一致、全元assertion保持、全Main1843同byte。|

公開合成UUIDはnew UUID(100,100)/new UUID(101,101)、sent2026-10-01T00:00:01.123456Z/row00:00:00.123456Z。JSTは独立固定20261001090001123/20261001090000123、contextは公開合成b64で実sessionではない。vectorはwhole byte SHAへ比較する。

command=tools/quality/pg10316_user_query_oracle_metadata.py（javac-proc:none、helper＋metadata runnerだけ、classpath自己readerのみ）、pg10318_user_query_oracle_six_compile.py（-DskipTests/六module正常compile/NullAway）、pg10320_user_query_oracle_post.py（source/byte/静的の独立結合）。実環境・stage command/exit/tool/source hashは公開manifestへ保存。

元PT-ADM044～等のDB/key/crypto/例外graph/実broker依存試験はNOT_EXECUTED_HOLD。上のMETAはoracle資格であり製品PT/PASS/TestID追加/実測coverage/実環境資格へ加算しない。元null/異常/再送/並行/SQL後条件の実施を代用したことにしない。Nullはsource/正常NullAwayと元未実行負例を区別、並行oracleは新helperが共有可変状態なしのsource確認のみ。品質条件451/四100/正式1964-53/QA051final/全安全HOLDは不変。
