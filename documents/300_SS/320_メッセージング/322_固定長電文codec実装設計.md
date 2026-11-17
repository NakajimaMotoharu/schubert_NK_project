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

## SSC-444 ProtocolValidator非instance責務と現Protocol全module再組立（2026-11-16）

BUG3107/YKT2579残のProtocolValidatorをpublic static-only interfaceへ表現し空privatectorを除去する。既公開PERSISTENT_DELIVERY_MODE=2とvalidateTransport(CommonHeader,TransportMetadata,ExpectedRoute)引数戻り値/例外/null/全分岐順序/固定診断を保持、private PROTOCOL_VERSION文字列001はvalidateTransport内localへ移し新publicfield公開0。classからinterfaceへのpublic型kind差とstatic呼出InterfaceMethodref差を内部Java ABI変更として明記、旧binaryとの混用禁止。全Main参照検索で直接caller FixedWidthDecoderを特定、同source Protocol全165MainをRoot規則でfreshcompile・全physicalを証明し、新helper/旧callerまたは旧helper/新callerの混合を禁止する。IdValue/PathSyntaxの先行型整理も含むため、必要なmodule再組立と通常全140PTを当source一回だけ行う。原130は成功確認で再演するのでなく、三helper型変更の下流/64layout/JMS transport snapshot/QA054/Unicode/独立goldenを同source/moduleで回帰する依存検証。既原130と追加N12三/WireEnum四/Path三の全31source(一helper含む)・五独立TSVを無変更で使用し、元source期待値をproduction methodで置換0。公開record constructor/getterに対する既public反射は固定UI由来型表/nonnull negative契約の範囲だけでprivate反射/Root権限反射無し、元有限2workerの期限/cleanup保持。実物DB/JMS接続/FS/master/鍵/VM/native/aruは操作しない。memory byte streamとtest literalのみ、枠/空き/所有を確認して新job一回とし重複起動禁止。標準coverageはdefaultfilter由来値として保存し、同singleexec全physicalのrawCodeも独立測定、missがあれば全451/当Program受入を保留・修正前BUGへ起票する。Interface/Code0/branch0は自然N/A、除外/旧exec合算/成功算術加算禁止。元904.85/SV/群開始見積保持、477停滞是正として細かなutility追加から一つの実module/caller/source閉包へ作業順を変更するが工程scope/品質/モデル/HOLDは変更しない。SS322323354914をPG前にmain反映、RD/UI/DIF変更不要。正式1964/53・正本184/625・元17/190・工数nullのまま、module回帰成功だけで全PGPT/ITST完了にしない。

状態:設計確定・main反映前、製造/通常PT140/全module/正式未完。

## SSC-445 Payload型registryの状態所有とprivate binding責務（2026-11-16）

BUG3111/YKT2583のうちPayloadTypeCatalogとprivate補助Mapping/RecordMapping責務だけを整理する。公開finalclass/四static APIの型・引数戻り値・例外/diagnostic・全64layout key/69namedtype・decoder methodref/登録順と不変Map/読取順序を保持する。privateSTANDARD cacheはclass初期化時に一回生成する実cache owner INSTANCEのprivatefinal standardへ移す。privateconstructorはこの不変registry実状態を確立し全lookupが参照する責務を持つためのもので、試験から無意味なinstanceや反射で空ctorを呼ばない。JLS class初期化とfinalfield safe publicationを保持し新publicinstance/API/可変cache公開0、性能/heap量は未測定でITST承認しない。二private recordはvalue-equality対象ではないdecoder bindingなのでprivate static final field-only classとし、実使用dataType/dataDecoder/recordMapping・recordType/recordDecoderのprivategetterとconstructorだけを定義する。外部から利用不能でsource検索上未使用のrecord由来equals/hash/toStringとMapping.layoutId accessorは生成せず、registry keyと重複するlayoutId component/privatefactory引数を除く。64Map.entry keyは不変、各mapping引数先頭に重複していた同じkey literalだけを除き、逆展開時は当Map.entry keyから元重複literal/旧privatefactory二signature/元record表現へ復元して全body/表/diagnosticをformatted完全一致で証明する。対象削除はprivateに不要なvalue APIの責務整理でありcoverage除外や到達不能合格としない。private全constructionは固定class literal/methodref/Optional.empty-or-ofに閉じたnonnull入力をRoot静的解析で確認、任意入力/private反射を追加しない。全Main参照をsource/ownerで保存し公開API javap完全一致を確認、他164Mainと既32Test source/五TSVの期待を保持する。新通常1は独立named-types-ss323.tsv64行からexpected class名/record有無を作り、有限二reader/ready-start latch/future10sec/finally shutdownNow-await10secで全64lookupを同時検証、128観測を128Testへ増幅0。初回cold-initを実測したと断定せず公開同時readとJLS安全公開根拠を分ける。Main変更の下流として同source全165Main/176physicalをfresh組立・既144＋新1＝全145通常PTを一回実行、旧source成功/exec転用0。Code変化はparent＋private2 classだけが想定で他173classのbyte一致を確認、parent/private2全Code raw100・全module rawは実値と不足を保存し全451へ昇格0。SS322323354914をPG前にmain反映、RD/UI/DIF変更不要。モデル/枠/Root2Actual4/実DB鍵VMnativearu/QA051final等HOLDと正式1964/53・正本184/625・工数nullを維持する。

状態:設計確定・main反映前、製造/通常PT145/全module/正式未完。

## SSC-446 固定長field paddingの三値dispatch（2026-11-16）

BUG3111/YKT2583のFieldDefinition compact constructor内のpadding選択だけを詳細化する。wireTypeは先行Objects.requireNonNullでnonnullを確立、承認済みWireTypeはTEXT/NUMERIC/BOOLEANの三定数に閉じる。TEXTならSPACE_RIGHT、NUMERICならZERO_LEFT、それ以外の現三値中BOOLEANならNONEという対応を、final local expectedへのif/else-if/else代入で明示する。三入力の対応・不一致時の既存診断・全null/範囲/end検査・両publicconstructor/recordcomponent/全API・独立UI TSV/期待値を変更しない。新enum定数追加はこの既定処理を無審査で流用せずwire型/設計/codec/全対応試験の変更対象とする。javac enum switch由来の理論上のunknown default/補助mapを作る必要がない責務へ整理するもので、列挙値の不正注入や反射、coverage除外、未実行を到達不能PASSに変換しない。型kindはrecordのままで公開ABI javap完全一致、変化Mainはこの一sourceのみ。元switch全byteを逆展開formatted完全一致で証明、他164Main/既全Test/五TSV不変。全165Mainを当sourceでfresh組立、physicalは元176からFieldDefinition$1のみ非生成となる175、親以外174class byte不変を独立照合。新JUnit定義0、現集約4＋必要原14＝同18を当sourceで一回必要再実行し現七class raw全line/method/class/branch100と全physical不足を別保存する。四mapを除外せず三残mapをrawで測定、全module/451/native/正式受入へ昇格しない。RD/UI/DIF変更不要、SSC設計を先にmain反映後PG。全HOLD/枠停止条件/正式1964-53/正本184-625/工数null維持。

状態:設計確定・main反映前、製造/通常PT18/全module/正式未完。

### SSC446 Root compile適合補足（2026-11-16）

SSC446補足（BUG3123/YKT2595）。Root実ビルドがcompact constructorの未初期化final expectedへの分岐代入を拒否したため、三値のif/else-if/else判定はprivate pure static expectedPaddingFor(WireType)へ置き、constructorはfinal Padding expected = expectedPaddingFor(wireType)で初期化する。先行nonnull契約/三値対応/TEXT SPACE_RIGHT/NUMERIC ZERO_LEFT/BOOLEAN NONE・既診断・公開record API・独立全期待を保持する。JDK単体の欠陥とは未証明、Root flags/静的条件を緩和しない。新private関数一methodは三入力を通常PTで全branch確認し除外0、逆展開ではhelperを除き元switchへ完全復元する。元47da/36514のcompile失敗を成功へ混ぜず保全、別freshRoot165/175physical/同18必要再試験・ABI/他174byte/raw七class100で是正を確認する。元開始.25/.75/2.25 cap2.5は維持し今回の内訳を再試行原因として記録、追加Junit0/外部仕様差0/全HOLD維持。

## SSC-447 型変換・JST日時の不変cache所有（2026-11-16）

BUG3111/YKT2583のうちTypedFieldValues/JstWireTimestampのprivate empty constructorと不変cache所有だけを整理する。公開finalclass/全public static APIとWIRE_LENGTH=17は保持、private cacheを外部公開0。TypedFieldValuesはprivate final Pattern retainedOptionalIdを実状態として所有するprivate INSTANCEをclass初期化時に一回生成し、constructorで元OPTIONAL_IDと同じPattern.compile("[0-9]{1,12}")を初期化、元parseOptionalIdはINSTANCE.retainedOptionalIdを読む。LITERAL_VALUE定数や全semantic変換/例外/範囲診断は不変。JstWireTimestampは元JAPAN ZoneId/17桁Pattern/STRICT formatter三cacheをprivate final retainedJapanZone/retainedWireDigits/retainedWireFormatterとして実所有し、private INSTANCE constructorで元と同じ順序・引数で一回生成、format/parseはその不変stateを参照する。class初期化/finalfieldの安全公開、Pattern matcherは毎callで分離、非並行mutable formatterやnew publicinstanceは追加しない。constructorは通常static経路が必ず使用する実cache状態のinvariantを確立し、試験から無意味なinstanceやprivate反射で呼ばない。追加二owner objectのheap/性能は未測定でITST合格を断定0。全cache literal/初期化順/変換body/診断を逆展開formatted完全一致、他163Main/全Test/五TSV不変、公開ABI完全一致・親二class以外173physical byte不変を確認する。生成class数は175/Code162を維持。日時header・全named69変換に影響するため、新定義0で既全35Testsource（helper含む）152通常PTを当source一回必要回帰し、両親raw100と全175raw不足を別記録、Module/451/正式を推測昇格0。元public oracleの四Class.forName/閉32public scalar/元helper inverse SHA/全期待は不変、工具は既module33/145に新二fixtureを加えた35/152構成だけ認識するよう補足し14負境界等の自己検証を実施、private/任意/HOLD反射やSDK接続を許可しない。旧同145/18の確認再演や旧exec合成0。SS322323354914をPG前にmain反映、RD/UI/DIF変更不要、全HOLD/枠10以下停止/正式1964-53/184-625/工数null保持。

状態:設計確定・main反映前、製造/通常152PT/全module/正式未完。

## SSC-451 Protocolの非instance namespaceと明示dispatch（2026-11-17）

BUG3111/YKT2583・YKT2647の残る四空privatector/17switchを詳細化する。FieldCodec/LargeResultRecordCodec/MediaDescriptorValidator/PayloadSemanticValidatorをpublic static-only interfaceとし、全public static methodの名前・引数・戻り値・例外・null契約を保持する。private static helperはprivateのまま、既private定数と不変Pattern/Map/Setは同一packageの非公開companion interfaceへ移す。companion型は公開namespaceへextendsせず、publicfieldを公開namespaceに増やさない。class初期化による不変cacheの一回生成・安全公開、matcher毎call分離を維持し、空instance/guard呼出/private反射でcoverageを稼がない。public型kindと呼出constant-poolのInterfaceMethodref差はJava内部ABI変更として記録し、旧class/helper/callerの混在禁止。Protocol全Mainと参照477Mainを当sourceでfreshcompileする。四held型を含むAPI/Webの全再構築はQA056成立後の終了依存として残し、当局所結果を全六module認定にしない。

PayloadCodec四、MediaDescriptorValidator二、LayoutFieldCatalog七、file.ContentDisposition一、PayloadSemanticValidator三の計17switchを、selectorの一回評価とnonnull契約を保つ明示比較へ置換する。Stringは同じcase literalのequals/同じ順序/default body、closed enumは既定数をif/elseで対応し新enum追加時は設計・全対応試験の変更を必須とする。case body/固定diagnostic/先行後続処理/64layout389field/69型/golden byteを保持する。javac専用hash/ordinal map/defaultを生成不要にする責務整理で、仮想enum注入/到達不能扱い/coverage除外/旧exec合算を行わない。変更前17case表と逆展開比較、全公開API差/物理class増減・debug差を記録する。

原35Testsource152と独立TSV/期待値は保持し、namespace四の公開型・publicstatic API集合/非instance契約を新四Testで確認、private memberアクセス無し。必要な変更後whole156を同sourceで一回実施し、全actualCodeのline/method/class/branch100、全例外・境界、NullAway/PMD/Checkstyle/format/SpotBugs・XML/CRC/init/独立postを要求する。新不足は修正前BUG起票、未達を合格へ換算しない。RD/UI/DIF/外部利用者挙動変更不要。SS322323333354/914をPG前にmainへ反映する。全Root/実DB/JMS/VM/native/認証/鍵/intent等HOLD・QA051/056/057・451・正式1964/53・元17/190/工数nullを維持する。

状態:設計確定・main反映前、製造/PT156・全六module・正式未完。変更前source db668dd02b/製品Core0a2b32d0、予定.50/1.80/4.50 cap5、費用F03一回、他program論理owner参照は二重課金0。

## SSC-452 digest生成の内部namespace可視性（2026-11-17）

BUG3182/YKT2650。SSC451のclass→interfaceではpackage-private static methodを同じ可視性で保持できないため、LargeResultRecordCodec.digestFor(String)をpackage-private companion interface LargeResultDigestのstatic digestFor(String)へ移す。公開facadeはwrite/decodeだけ、private sha256Digestが同じliteral SHA-256で内部関数を呼ぶ。LargeResultDigestは非公開型で外部公開APIを増やさず、元digestForのbody/NoSuchAlgorithmException→同IllegalStateException/診断/cause/null挙動を保持する。公開facadeの追加digestForはBUGとして不受理。元LargeResultRecordCodecTestのnegative一箇所は呼出型のみLargeResultDigestへ変更し、Test ID/入力not-an-algorithm/期待例外・cause全assertionは保持する。期待値をproductionから生成しない。interface暗黙publicの内部methodは非公開型内の境界に閉じ、空constructor/private反射/ダミーinstanceを作らない。新Mainは169・physical176（新helper一つ）、既152＋新namespace四=156を当sourceで一回実行し、全actualCode/NullAway/PMD/CS/format/SB/全publicABIを確認する。四namespace全method/172共通classのpublic surfaceを再照合、旧public型kind四差以外の公開method/field差0を要求し、全caller480→481Mainをfreshcompileする。旧失敗Core3b275/PG37624・compile失敗/原証拠を保全し成功へ合算0。RD/UI/DIF変更不要、SS322323333354914をPG前にmainへ反映。全HOLD/451/正式1964-53・17/190・工数null維持。

状態:設計確定、main反映前、製造/PT/全六module/正式未完。元SSC451群開始見積.5/1.8/4.5cap5は保持、当見落しの手戻りを内訳へ記録し新規原受入に加算0。

### SSC451/452 main反映と製造・PT限定結果（2026-11-17）

設計はPR415/416・main23aea46eへ反映済み。製品Corea013a6d676454082de3c59bc199e87f37fefe159／Unitf08897ce8742091dbf1c7575e25780d31b30c089、PG37652当156件は成功156・F/E/S/notrun0。169Main/176physical・162Code/1432method、単一execの独立XML/CRC/init及び未filter raw3638行/1432method/162class/1078branch/20347instruction全miss0、自然NoCode14は除外せず0/0 N/A。原152の独立期待値は保持（digest negative一箇所の呼出型と整形だけ逆変換SHA exact）、公開namespace四を追加。全literal/initializer645一致・172共通public ABIは承認済四型kind差以外同一、Root四module481Main・Protocol176byte一致、NullAway/SpotBugs176/CS/format0、PMD46は元個別anchor・適用根拠を照合し未分類0。新37指摘を無条件非該当とせず是正、元失敗を保持した。MIME内部helperはnullable-returnを明記し元reject結果を保持するPG-D1176。

公開証跡: [PG37674 Protocol品質結合](https://github.com/NakajimaMotoharu/schubert_NK_project/blob/2009b097ce44a1374219d53b92e9526c3186ca57/evidence/01_PT/018_NK-OPS-001/evidence/PG37674-ssc451452-protocol-module-criteria-return-v1/manifest.json)。BUG3111/YKT2583のProtocol全raw不足は閉鎖。全六module、API/Web QA056、実Root/DB/JMS/VM/native/鍵/権限等HOLD、451全体、正式1964PT/53scope・元17/190・工数nullは維持し、本限定結果で全PGPT/ITSTの完了を宣言しない。未受入実装/工具/証跡はmainへ混入せず、実施branchの公開証跡を参照する。
