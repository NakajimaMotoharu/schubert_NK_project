# 固定長電文codec実装設計

## 1. 目的・追跡

固定長UTF-8電文のlayout定義、encode/decode、NFC、byte境界、padding、header/transport照合、error profile、例外とtest vectorを定める。

- 関連UI: 232～237、261 SS-004
- 関連RD: MQ-014～038、MSG-001～011、MSG-F01～F09、AVL-009～010
- 関連QA/RDF/UIC: QA-003、017～021、025～032、RDFなし、UICなし

## 2. Object model

| Type | 主field | 不変条件 |
|---|---|---|
| `CommonHeader` | protocol/version/layout/direction/interaction/message/correlation/sentAt/context/length/result | Header 256 byte、予約全space、ID/区分相関 |
| `LayoutDefinition<P,R>` | ID/version、direction、interaction、data length、record definition、max count、max total | 233の64 layoutと1:1 |
| `FieldDefinition<T>` | name、offset、length、wire type、presence、semantic validator | offset 1開始、gap/overlapなし |
| `WireMessage<P,R>` | header、payload、records | Header長さ式とlist size一致 |
| `TransportMetadata` | JMS type/IDs/replyTo/expiration/delivery mode/properties | JMS objectをprotocolへ持ち込まない |
| `ValidationContext` | request/error/success profile、layout | Result code先行検証 |

`LayoutRegistry`はimmutable singletonで、起動時に全64 layoutを明示登録する。Reflectionによるfield順推測、annotationだけからの暗黙offset計算、
Map順依存を禁止する。定義sourceはJava builder/recordとし、offset/lengthは323およびUI 232～236と機械照合する。

## 3. Wire typeとJava型

| Wire | Java decode型 | Encode入力 | 未設定 | DB変換 |
|---|---|---|---|---|
| X text | `String` | `String` | `Optional.empty()`またはsemantic wrapper | text/varchar/char、enum |
| X numeric optional | `OptionalLong`等へmapper変換 | 文字化前のwrapper | 全space | nullable bigint/integer/timestamptz |
| N integer | `long`/`int`/semantic ID | 非負整数 | 原則禁止。Error profileは全0 filler | bigint/integer/smallint |
| N timestamp17 | `Instant` | `Instant` | Error fillerのみ全0 | timestamptz |
| B | `boolean` | boolean | Error profileまたは個別Cだけspace | boolean |

Nはbinary integerではなくASCII digit列である。桁overflowを検査後`long`へparseし、浮動小数へ変換しない。N12 IDは
0～999999999999、N9 version/countは各field意味上限を追加検査する。

## 4. Encode algorithm

`FixedWidthEncoder.encode(WireMessage)`は次を順に行い、途中結果を送信しない。

1. Layout IDから`LayoutDefinition`を取得し、payload/record Java type、Q/S/E、S/A/Iを照合する。
2. Record件数とmax、response result profileを決定する。
3. Data/recordの各fieldを`FieldCodec`でencodeする。
4. `dataLength`、`recordLength`、`recordCount`、`totalLength=256+data+record×count`をchecked arithmeticで算出する。
5. Headerの宣言長を算出値で生成し、`HeaderCodec`で256 byteへencodeする。
6. Exact sizeの`byte[]`を1回allocateし、header/data/recordを順にcopyする。
7. 最終offset=totalLength、最大body、header宣言との一致をassertし返す。

### 4.1 X型

```text
null/empty optional -> 全ASCII space
値あり
 -> Unicode NFC
 -> CR/LF/TAB/NUL検査
 -> 末尾ASCII space禁止検査
 -> UTF-8 strict encode
 -> encodedLength <= fieldLength
 -> value bytes + 右ASCII space
```

Search/usernameのtrimはHTTP/application mapperがNFC前に行う。Password、質問/回答本文を自動trimしない。Unicodeの`　`は値であり
ASCII paddingではない。Unpaired surrogateはstrict UTF-8 encode errorとする。

### 4.2 N型

```text
semantic range検査 -> ASCII decimal（符号/小数点なし）
 -> digitsLength <= fieldLength -> 左ASCII '0' padding
```

Timestampは`Instant`をAsia/Tokyoへ変換し、厳密17桁`yyyyMMddHHmmssSSS`。Resolver style STRICT、存在しない日時を生成しない。
Wire上にoffsetを持たないため夏時間変化のないAsia/Tokyo前提を固定する。

### 4.3 B型

通常値は1 byte`0`/`1`。成功時必須Bへspaceを設定できない。Error profileはspaceを未設定fillerとして許可し、falseと解釈しない。

## 5. Decode algorithm

`FixedWidthDecoder.decode(byte[],TransportMetadata,ExpectedRoute)`は業務object生成前に次を行う。

1. Null/body size 256未満/1,000,000超を拒否する。
2. Headerの固定byte sliceを取り、UTF-8 decoderを`REPORT` modeで実行する。
3. Protocol `SCHBNK01`、header version `001`、header length `0256`、予約44 spaceを検査する。
4. Layout ID/versionからdefinitionを一意取得し、未知値を拒否する。
5. Direction/interaction/route、JMS type、`NKLayoutID`/version、Message/Correlation ID、ReplyToを照合する。
6. 宣言data/record長がdefinitionと一致し、record count上限内であることを検査する。
7. Checked arithmeticで総長式を計算し、header total、実body lengthと一致させる。
8. Responseはresult codeを先にparseし、success/error profileを決定する。Errorならrecord count=0を検査する。
9. Data/recordをbyte offsetでsliceし、型/padding/必須/semantic allowlistを検査してJava recordへ変換する。
10. Record間順序・cross-field conditionをlayout validatorで検査する。

Decodeはbody全体を文字列化してsubstringしない。Byte offsetを保持し、UTF-8 sequenceがfield境界を跨ぐ場合は各fieldのstrict decodeが失敗する。

## 6. Padding検証

### 6.1 X

- 末尾から連続する`0x20`をpaddingとし、その前をstrict UTF-8 decodeする。
- 値領域内にASCII spaceは許可するが、末尾spaceはencode規則上存在しない。
- Padding領域に`0x20`以外があればerror。全spaceは未設定。
- NFC再正規化してbyte列が変わる受信値は、非canonical inputとして恒久protocol errorにする。

### 6.2 N

- 全byteが`0x30`～`0x39`であることを先に検査する。
- 先頭0はpadding/値0を区別せず数値としてparseする。Field semantic rangeで0可否を判定する。
- Error response fillerの全0はsemantic parseせず未設定として扱う。

### 6.3 Fixed/reserved

固定値はbyte完全一致、reservedは全`0x20`。未知拡張を無視しない。

## 7. Header validation

| Field | Q | S | E |
|---|---|---|---|
| Message ID | UUID、新規root | UUID、新規response | UUID、新規event |
| Correlation ID | Rootは自身ID | Request Message ID | QWKは元受付request、WLGEVTは業務request/自身 |
| Context | Login Q/Sとinternalは全space、他は64 hex | Login responseもheaderはspace、他はrequest scope | 全space |
| Result code | 全space | 定義code必須 | 全space |
| Record count | Request原則0 | Layout/profileによる | 0 |

JMS `JMSCorrelationID`はwire correlation、`NKMessageID`はwire Message ID、`NKLayoutID`はlayout、protocol propertyは`001`と一致する。
Provider採番`JMSMessageID`はwire Message IDと同一である必要はない。

## 8. Result profile

| Profile | Code | Data validation | Record |
|---|---|---|---|
| Success | 0000 | M/F/C通常規則 | 定義件数 |
| Idempotent success | 0200 | 0000と同じ | 定義件数 |
| Business/system error | その他定義code | F固定、個別error fieldだけ検証、X全space/N全0/B space | 0件 |

Receiverはerror fillerへ通常M/range検査を適用しない。固定data長/header record lengthは成功・errorで不変。未知result codeは恒久protocol error。
`error_field` 32 byte、`error_message` 256 byteを持つlayoutは利用者表示可能なbounded文字列だけを許可し、内部語/pathを拒否する。

### 8.1 個別error field（SSC-012）

UI234 §3を正として、`LGNRSP01`の0106ではDATA開始168/長さ6のRetry after秒を0～900の数値として保持する。他errorでは同fieldは全0。開始177/長さ256の利用者messageは全errorでoptional X（NFC/UTF-8、control・末尾space禁止）として保持する。Username/Role/context/発行日時/期限日時は全space、残り試行回数は全0、record0。任意の内部例外文を設定せず、利用者向け文言はapplication mapperの固定messageから設定する。

`NTCRSP01`の0107は既定の更新後状態だけを保持する。`NTDRSP01`のERROR job状態は成功profileの業務dataであり、header error profile例外ではない。他29responseに例外を推測追加しない。型付き業務recordの通常semantic変換はsuccess用であり、error responseはresult-aware field codec経由で読む。Booleanのみの低水準filler APIを0106等の個別error応答生成へ使用しない。

## 9. Cross-field validator

| Layout/領域 | 検査 |
|---|---|
| 全page | page size固定50/100、total/pages/first/lastの算術整合 |
| SRCRSP01 | Audio有無=1ならID/path必須、0ならspace。1 entry 1 record |
| SCNRSP01 data | Iならinline 0～200＋descriptor未設定、Fならbody record 0＋file descriptor完全 |
| SCNRSP01 record | Entry/Audio sequence昇順、audioなしsequence 0、同entry本文一致 |
| MEDIA1024 | disposition要求一致、size>0、SHA hex、MIME allowlist |
| User update | UUID token、N9 version、path/form target一致はmapper/APIで検査 |
| NTDRSP01 | Stateごとの日時/error/answer/削除flag condition |
| NTCRSP01 | 0000/0200はCANCELLED＋日時、0107は最新state＋日時space |
| QSD/QSS | Answer stateとanswer日時/本文presenceの整合 |
| Internal | Context全space、producer MQ role、layout allowlist |

## 10. Large-result record codec

SCNRSP01 file modeはheaderなし、4,800 byte recordを連続配置する。`LargeResultRecordCodec.decode(InputStream,descriptor)`は
4,800 byte exact-readを繰返し、EOF途中を拒否する。最大10,000件/48,000,000 byte、BOM/newline/separatorなし。

Hash/sizeを全体検証後にrecord decodeするため、Webは一度fileをstreamしてSHA-256を計算し、同じopen file descriptorをseek 0へ戻すか
再open時にfile key/size/mtime不変を確認する。File差替えを防ぐ詳細は333を正とする。

## 11. Exception・fatal処理

| Exception | 発生例 | Sender/receiver処理 |
|---|---|---|
| `FieldEncodingException` | byte超過、control、invalid value | Senderは送信しない。HTTP field errorまたは内部処理ERROR |
| `MessageEncodingException` | 長さ式/registry不整合 | 起動/production defect。送信せず非zero終了 |
| `PermanentProtocolException` | Body/JMS/version/UTF-8/padding不正 | 業務未実行、originalをDLQへtransactional隔離、commit後exit |
| `UnsupportedLayoutException` | 未知ID/version | Permanent protocolと同じ |
| `TransportTemporaryException` | Broker read/send失敗 | JMS rollback、再接続/再配送 |

Fatal logはerror code、component、layout（安全にpeekできた場合）、Message/transport ID、body length、検証stepだけを記録する。Body、field値、
password/context/questionをdumpしない。DLQ隔離自体が失敗した場合は元messageをACKせずexitする。

## 12. Layout定義生成・監査

PGはUI 232～236から手作業でoffsetを複製せず、1つのJava `LayoutDefinition`から次を機械出力・比較する。

- Layout catalog: ID/version/data/record/max count/max total/direction/interaction
- Field catalog: area/name/start/end/length/type/presence/padding/semantic validator
- Java record component名/type
- Golden blank/min/max body SHA-256とhex fixture

生成結果を323の表とUI正本へ照合するが、生成処理がUI byte値を自動変更してはならない。不一致はbuild失敗。

## 13. 必須PT vector

### 13.1 全64 layout共通

- Success最小/最大、error profile、record 0/1/max、総長式、header/property一致。
- 各fieldの1 byte不足/上限/1 byte超過、N最小/最大/overflow、B 0/1/space/その他。
- ASCII、日本語3 byte、合成文字NFD入力→NFC、emoji 4 byte、field境界直前/超過。
- CR/LF/TAB/NUL、末尾ASCII space、不正UTF-8、途中切断、予約非space。
- 未知header/layout version、Q/S/E・S/A/I不一致、Message/Correlation不一致。

### 13.2 Golden vector

各layoutで最低次を`src/test/resources/protocol/<layout>/`へ固定する設計とする。

`minimum.bin`、`maximum.bin`（巨大maxはhash＋generator seed）、`error-0100.bin`等の適用error、`expected.json`、`sha256.txt`。
Passwordを含むLGNREQ/UCRREQ/UPWREQのfixtureは公開test専用値とし、production credentialを使わない。

## 14. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-016 | Offsetはbyte sliceで処理し、body全体のString化を禁止 | UI 232、UTF-8境界と固定byte位置を正確に検査 | Codec property/golden PT |
| SS-D-017 | 受信X値がNFCでなければ恒久protocol error | 送信NFC規則をreceiverでも保証し、検索/HMAC揺れを防ぐ | NFD受信negative vector |
| SS-D-018 | Layout definitionを唯一のcode側metadata源としcatalogを生成監査 | 64 layoutの手書きoffset重複を抑止しつつUI正本を変更しない | CIでUI/323/catalog照合 |

## 15. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Codec object、encode/decode、validation、fatal/test vector設計を初版作成。 |

## SSC-442 N12非instance validatorと九識別子の値契約（2026-11-16）

BUG3104/YKT2576のN12共通IdValueをpackage-private static-only interfaceへ表現する。非instance責務のfinalclass宣言と空privateconstructorだけを外し、MAXIMUM=999999999999Lとvalidate(long)の全body/固定IllegalArgumentException文言を保持する。interfaceで冗長なfield staticfinalだけを省き暗黙publicstaticfinalとなるが、型自体のpackage-private境界は維持しpackage外へ新型を公開0、private状態やPatternを公開0。static validateもinterfaceで暗黙publicとなる内部flag差を記録し、全Main参照をsource/owner/行で列挙する。九record constructorのinvokestaticはInterfaceMethodrefへ変わるため全九callerを同じRoot/sourceでfreshcompile・実constructor実行し旧class型helperとのbinary混用禁止、全module/release JAR再構築は後続条件。publicProtocolIdと九recordの型/permits/component/constructor/getter/equality/hash/toStringの既ABI・意味を維持する。九IDだけの正値N12であり0許容のcount等generic数値fieldへ適用を広げない。独立new3通常PTは九factory×正常1/123/MAX・異常LongMIN/-1/0/MAX+1/LongMAX、固定診断、全record同値/異値/null/異型/独立signed32 Long hash/既literal表示、全81型対と実HashMap九key保持を確認する。期待MAXをproduction定数から生成0、private反射/空instance/除外/到達不能合格0。Main11/physical11(10Code・ProtocolId Code0自然N/A)/freshRoot/static/current10CRC-initXML/同run3/raw四100を要求する。元120/124やaccepted17全面再資格を行わず、元raw不足PG35880と旧JARは保全・合算0。RD/UI/DIF変更不要のSS内部詳細、SS322323354914をPG前にmainへ反映する。Actual4/Root2/VMDBkeys/native/aru/HOLD・全451/正式/wholeProtocolModule未受入を維持する。

状態:設計確定・main反映前、製造/通常PT3/全module/正式未完。
