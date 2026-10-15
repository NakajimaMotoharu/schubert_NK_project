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

実command：`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pyflakes-runtime> python3 -B tools/quality/pg3264_header_oracle_mutations.py before`。是正後は別new-only `after`。実時刻/source/終了code/hash/障害/通常PTのsourceとrunは105の実結果へ保存する。現段階は未実行。
