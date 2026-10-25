# G13 非token名Header八method・独立期待値意味対応

1952の親review記録。UI232/SS322はorigin/main8b91944df5820535e23ba2469740f1c0aa94c447を参照、SHAはUI232=e2092eb5e02855734bf7faec37abcee5d918de3b7fa689e7ae1a9f4b81228288、SS322=f6dcecf979d9dbac0338aae079d5730f97ba53afaa3dd46db3e20ef49b21618d。既Program001仕様001/104/108とProgram002仕様001の期待値を変更せず使用する。

| Class | method | 既Test ID（複数は同methodが担うfamily） | 独立期待値・確認根拠 | 適用性/制限 |
|---|---|---|---|---|
| HeaderModelTest | enumsMapOnlyApprovedWireValues | PT-PRO-001-H01 | UI232§3のQ/S/E、S/A/I全六name-wire literalを両方向に確認、§7の12 result literal/0000・0200だけ成功profile、未知/空/複数/null拒否 | 許容集合/正常/異常/null。parse往復だけでencode wireを認定しない |
| HeaderModelTest | authenticationContextValidatesAndRedacts | PT-PRO-001-H01,PT-PRO-001-H03 | 固定公開dummy a64/b64の等値/hash/異値/異型、lowercase64hex、63/大文字/null拒否、toString完全REDACTED | 内部value/null契約、実session/token実体は扱わない |
| HeaderModelTest | validHeadersCoverRequestResponseErrorAndEventProfiles | PT-PRO-001-H02 | Login context空/通常request必須/internal空、Q/S/E/result相関、固定256+9+272=537、明示redaction | registryとの整合だけで正本の全offsetを認定せずgoldenで補完 |
| HeaderModelTest | headerConstructorRejectsEveryStructuralViolation | PT-PRO-001-H03 | version/protocol/length/count/ID/日時精度/profileの固定反例、assertInvalidはLayoutValidationExceptionに限定 | 非null構造違反。広いRuntimeException/NPE代用の旧弱oracleは使わない |
| HeaderModelTest | headerValidateAgainstRejectsEachMetadataMismatch | PT-PRO-001-H03 | layout ID/kind/interaction/data/record/max countを一つずつ変え型付き拒否、definition nullはJava参照precondition | LayoutDefinition固有の他契約はP001-02へ残す |
| HeaderModelTest | headerReferencesRejectNullAtTheNamedInvariantBoundary | PT-PRO-HDR3266-001 | 九参照を一つずつnull、固定field名の即時NPE、正常LOGREQ01/256/同一correlation | 104で確定した内部precondition。業務成功にNPEをcatchしない |
| HeaderModelTest | headerLengthArithmeticAcceptsExactMillionAndRejectsTheNextByteAndOverflow | PT-PRO-HDR3266-002 | 1000000-256=999744をdata/record双方、次byte拒否、999999×999999はchecked overflow/ArithmeticException原因/固定診断 | layout固有の狭い上限とconstructor全体上限を混同しない |
| MessageCodecTest | headerEncodingMatchesIndependentUi232GoldenVector | PT-PRO-002-H01 | 別test-side ASCII builder/全space初期化でUI232の17fieldの256byte Login Q expected、array完全一致/peek相関とnull/255byte拒否 | H01 family全Q/S/EではなくLogin Q配置の独立golden。codec ownerP002-03 |

## Golden fieldの独立位置表

Java offsetはUIの1開始位置から1を引いた値。長さ/先頭/末尾をUIから手で固定し、Production HeaderCodec/FieldCodecからexpectedを生成しない。UUID二fieldは公開固定入力、timestampは03:34:56.789Z→JST12:34:56.789のliteral、Login context/result/reservedはspace。実session/credentialはない。

| FieldNo | UI開始 | 長さ | test offset | Golden期待値種別 |
|---:|---:|---:|---:|---|
| 1 | 1 | 8 | 0 | SCHBNK01 |
| 2 | 9 | 3 | 8 | 001 |
| 3 | 12 | 8 | 11 | LGNREQ01 |
| 4 | 20 | 3 | 19 | 001 |
| 5 | 23 | 1 | 22 | Q |
| 6 | 24 | 1 | 23 | S |
| 7 | 25 | 36 | 24 | 固定公開Message UUID |
| 8 | 61 | 36 | 60 | 同固定UUID |
| 9 | 97 | 17 | 96 | 20260902123456789 |
| 10 | 114 | 64 | 113 | ASCII space |
| 11 | 178 | 4 | 177 | 0256 |
| 12 | 182 | 6 | 181 | 000384 |
| 13 | 188 | 6 | 187 | 000000 |
| 14 | 194 | 6 | 193 | 000000 |
| 15 | 200 | 9 | 199 | 000000640 |
| 16 | 209 | 4 | 208 | ASCII space |
| 17 | 213 | 44 | 212 | ASCII space |

HeaderModelTest.HeaderBuilderの通常入力は一部Production識別子定数を用いるため、その自己整合だけを独立識別子oracleとしない。別MessageCodecTest.requestHeaderは固定SCHBNK01を入力し、expectedも固定SCHBNK01/17fieldを使う。test側ascii helperはUS_ASCII.getBytes/System.arraycopyだけでProduction呼出しなし。enum name-wireはliteral allowlist、構造反例は型付きLayoutValidationException、nullの九field名もtest literalである。旧BUG1244/1279の弱oracleは元仕様104/108に従い戻さない。

immutable header/value/enumにtransaction/再送状態はなく、実JMS/DB/同時session/業務再実行・native所有は他ownerの受入へ残す。当八methodの静的意味対応で全layout/全QSE/全branch/四100を認定しない。別sourceの旧84/3701/native成功を現在sourceへ転用0、実行PT/新ID/Main/coverage/正式増分0。現行Root/VM/DB/native/私有raw/鍵/配備/拒否未特定操作のHOLD維持。
