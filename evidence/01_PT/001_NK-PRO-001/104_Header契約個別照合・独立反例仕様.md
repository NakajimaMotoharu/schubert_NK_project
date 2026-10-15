# 共通header契約・独立oracle照合（PG3264、P001-01）

2026-10-15。対象=AuthenticationContext/CommonHeader/MessageKind/InteractionKind/ResultCode/package-info、MQ014～018、UI232、SS322/323、451。既1964PT/53scopeの正式認定・工数率nullは不変更。PG3258 whole3699は別固定sourceで稼働しており、本工具/後続Testをその成功へ合算しない。

## 独立反例（Production/VM/coverage変更なし）

PT-PRO-HDR3264-001：現在の実Protocol JarとJUnit実class pathをSHAで固定し、私有shadow classを先頭にした別JVMで実HeaderModelTestを一methodずつ選択。agent無し、実一testのfound/started/success/failure/skip/abort/containerを検査。compile拒否・NoTestsを反例成功としない。

| Vector | 独立期待値・試験対象 | before予測 | 是正後に必要な結果 |
|---|---|---|---|
| BASE_STRUCTURE | 正常Main、構造不正を拒否する既Test | 実一Test成功 | 同成功 |
| BASE_ENUM | 正常Main、UI232のQ/S/E・S/A/I・result一覧 | 実一Test成功 | 同成功 |
| WRONG_EXCEPTION | protocol不正にLayoutValidationExceptionでなくNPEを返す合成変異 | 広いRuntimeException期待で見逃す仮説 | AssertionFailedErrorで拒否 |
| MESSAGE_WIRE | UI232でSと定めるRESPONSEのwireをRへ変更、decode側はそのまま | parseの往復だけではwire片側を見逃す仮説 | AssertionFailedErrorで拒否 |
| INTERACTION_WIRE | UI232でSと定めるSYNCHRONOUSのwireをXへ変更 | 同仮説 | AssertionFailedErrorで拒否 |

本操作は実装済み試験oracleの診断であり、Production障害は主張しない。実見逃しを確認した場合、修正前に915/916へ起票し、同種のheader五型と関連semantic18型の独立name/wire/null/例外契約を横断する。Production mutationを元tree/Jarへ書き戻さず、旧失敗・compile・全rawを私有保存する。診断5caseをProduction PT/coverageへ加点しない。

## 受入trace（調査中、未認定）

MQ014/015=MessageCodecTestの固定256byte黄金値・body長式・route/header、MQ016=PayloadTypeCatalogTestのSS323独立64行/69型、MQ017=LayoutMetadata/FieldCatalogのUI233/234～236独立TSV、MQ018=FieldCodecTestのUTF8/NFC/byte超過/不正decode。要求ownerがP001-01であっても他主担当の共通実装費を再計上せず、個別証跡/全同source品質/終了依存を照合するまでacceptanceを変更しない。

実command：`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pyflakes-runtime> python3 -B tools/quality/pg3264_header_oracle_mutations.py before`。是正後は別new-only `after`。実時刻/source/終了code/hash/障害/通常PTのsourceとrunは105の実結果へ保存する。

## BUG1279/YKT1045修正後の通常PT

beforeは実五selector全成功で三見逃しを再現。915/916のaec31c214先行起票後、構造invalidはLayoutValidationExceptionへ限定（暗黙NPE/他RuntimeExceptionは不可）、MessageKind/InteractionKind全六name/wireをUI232 literalで照合。ResultCode十二literalは既BUG1244是正を保持、AuthenticationContextの形式/比較/redaction・MessageCodec固定黄金値も保持する。

PT-PRO-HDR3266-001：CommonHeaderの九参照を一つずつnullとし、protocolIdentifier/layoutId/messageKind/interactionKind/messageId/correlationId/sentAt/authenticationContext/resultCodeの順に、Java内部constructorの即時requireNonNull契約と当field名を要求。nullのまま保持して後で偶発NPEとなる実装を拒否する。外部wireのdecode拒否型とは区別し、NPEを正常業務結果へcatch/変換するものではない。無欠落の場合は固定LOGREQ01/256/同一correlationを要求。旧仕様H03の「NPEではなく」は非null構造不正値のvalidationを指し、既Java参照preconditionを外部protocol成功/異常へ置換しない。

PT-PRO-HDR3266-002：UI232総長式から独立算出`1,000,000-256=999,744`。data999744/recordなしとdataなし/record1×999744の両方で総長1000000を受理し、各次一byteを拒否。999999×999999はint overflowとして型付きvalidation例外とArithmeticException原因を要求する。layout固有の狭い長さ上限は別validateAgainstであり、constructorの百万byte上限と混同しない。

通常command=`python3 -B tools/quality/pg3266_header_protocol_regression.py`。期待=Protocol実84PT/17suite/174Main、全四counter100/静的0/FES-flaky-notrun0、既PG3248から全Jar member同byte（外Jar timestamp差は許可）、Header全七Test。Main/VM/署名/配備0。全六への新Test集合統合と他WBS固有受入は別未完、今回の旧3699を本新84の統合成功へ流用しない。
