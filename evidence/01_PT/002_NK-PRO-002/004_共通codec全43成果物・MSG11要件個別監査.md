# 共通codec全43成果物・MSG11要件の個別監査

2026-10-15、WBS-P002-01、Production a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25、UI231～236/SS311322323333351、既Program仕様X/N/B/H/M/T/E/T03/T04を適用。認定は実3702/全source品質・同byte native資格の終端を待ち、監査記述だけで変更しない。

## 全43artifactと独立期待値

| 所有対象 | 明示契約・実Testとの対応 |
|---|---|
| FieldCodec | FieldCodecTest全五：X01～03のASCII、日本語3byte、emoji4byte、NFD→NFC固定byte/padding/超過/不正surrogate・UTF8/必須・任意/制御文字/末尾space、N01/02の0/1/max・符号/範囲/overflow・error filler、B01の0/1/space/未知・予約space。標準Java UTF8又はbyte literalがexpectedでありProduction encodeをexpectedに使用0 |
| FieldEncodingException | 上記送信側異常：型付き変換失敗と固定diagnostic/CharacterCodingException原因。受信恒久例外と区別し、本文値や秘密値をmessageへ再構成しないsource review |
| FixedWidthEncoder、FixedWidthDecoder | MessageCodecTest全七のM01/02：独立256byte header、固定data/record1・最大/短255/過長1000001/実長と宣言不一致・未知layout/route maximumを検証。input/returned byte及びrecord listは防御copy、null・不変条件を境界で拒否 |
| ProtocolValidator | T01、transportAndRouteContractsRejectEveryMismatch/metadataAndExpectedRouteEstablishNullAndRangeContracts：Bytes/persistent2/protocol001、Message/Correlation/layout/direction/interaction/destination/replyTo/expirationを各一不一致へ変更し恒久拒否。null内部参照も即時拒否 |
| 18 wire enum：AnimationCategory、AnimationListCategory、AnswerState、ContentDisposition、DeliveryMode、EntryType、GameCode、LogLevel、LogType、MediaMimeType、NotificationErrorCode、NotificationState、NotificationType、PairRole、UserRole、UserState、VideoCategory、VoiceCondition | ProtocolSemanticTypeTest.approvedEnumNamesWireValuesAndConversionMatchIndependentDesignTables：UI234～236/SS333351からの独立name=wire全allowlist。値数/各wire/変換/未知/nullを検証。102/103の消費側・実変異拒否を履歴保全。戻り値を期待allowlistにしない |
| N12 ID九型：AsyncJobId、AudioId、EntryId、LogId、NotificationId、QuestionId、ScriptFileId、SpeakerId、UserId＋内部IdValue | allN12IdentifierTypesEnforceTheSharedPositiveRange/typedHelpersConvertIntAndIdentifiersWithoutLosingWireKinds：独立1/999999999999を受理、0/1000000000000を拒否。SS323のID正範囲と一般Nの0許可を混同しない。numeric optionalはwire Xへ変換 |
| DisplayPath、RelativePath、内部PathSyntax | SemanticFieldValueTest全四のT03：独立safe Unicode/NFD→NFC・相対path、Unix絶対/drive/UNC/parent/empty segment/backslash/control/nullを各拒否、redaction/比較/hash。filesystem解決はせずstorage/表示pathを区別し、UI243/SS333の禁止matrixへ対応 |
| Sha256Hex、HttpStatusCode、ElapsedMilliseconds | SemanticFieldValueTest全四とProtocolSemanticTypeTest.xNumericWrappersAndGeneratedNumericRangesRejectNonCanonicalValues：lower64hex/大文字・短長・未知、HTTP100～599/99/600/非数字、elapsed0～999999999/上限超過/負数/非正規形式、null/Unsetを固定vectorで確認 |
| ProtocolId、WireEnum | value()/wireValue()のpublic抽象契約のみ、default/static実行なし。九ID/18enumのactual経由で契約を検査。実行不能interface二件を恣意的coverage除外としない |
| codec/package-info、semantic/package-info | @NullMarked宣言、実全compileのNullAway/JSpecify/lintへ含める。注釈の存在だけで静的合格としない |

485の43path/hashと一致、39実行family＋2抽象interface＋2package注釈。sharedClassReferencesは空、専有RD11行。型別methodは既Program仕様T03/T04及び上表actual class/methodへ追跡する。他ownerのJstWireTimestamp/TypedFieldValues/DTO/JMS senderを参照しても製造費・受入を二重付与しない。

## MSG原文全11行

| RD | 独立期待値・actualとのjoin |
|---|---|
| MSG-001：JMS BytesMessage/UTF8文字表現 | codecはJMS非依存の正確byteを返す。T01で非BYTESを拒否。実ArtemisRequestSenderTest.questionAcceptanceSendUsesSameApprovedQueue/sendsOneValidatedPersistentRequestAndCommitsは独立request wireと受信BytesMessage body/metadata一致、実commitを検証。JmsReplyDecoderTest.nullTypeBodyLengthAndCopyAnomaliesAreRejectedはTextMessage/短長/nullを拒否。これらWeb二suiteは当source全体XML witnessへ明示接続してから認定 |
| MSG-002：UTF8後byte長 | X01/02の日本語3/emoji4byte exact境界とemoji＋xの4byte超過拒否、NFD入力の固定正規化byte。文字数だけで判定しない |
| MSG-003：右ASCII space | X01のAB4byte=`41 42 20 20`、payload独立UI offset golden、全389項目/287hash。左padding/Unicode spaceを代用しない |
| MSG-004：数値左0・原則必須 | N01/02の000/001/999 literalと負値/桁/range/overflow。固定桁ASCII digit以外を受理0、error0 fillerは通常zeroと区別 |
| MSG-005：任意数値X・全space未設定 | Xの一般左寄せ/右space encode pathと、ID/HTTP/elapsedの独立numeric→FieldValue.Text/Unset期待値を対応。NumericOrErrorFillerの通常N=0と未設定を別扱い。仕様の123例をbinary integerへ変換しない |
| MSG-006：BのASCII0/1一byte | B01の固定0/1/spaceと未知2/二byte/null拒否、error/任意だけspace。全31response error goldenでも検証 |
| MSG-007：超過は変換例外・切捨て/途中分割/送信0 | FieldCodecのstrict encoder→encoded.length検査→exactcopyという実制御順を確認し、X02のmultibyte超過/不正surrogate及びN02 overflowが返却前に型付き例外。共通codecはIO/JMS副作用を持たず部分結果を送らない。Sender側のnullWireIdentityLengthKindAndSessionModeFailBeforeCommitでも不正wireをcommit前に拒否 |
| MSG-008：CR/TAB/NUL禁止、初期改行なし | X02/03のCR/LF/TAB/NULそれぞれのencode/decode拒否。将来LF許可という未承認変更を先取り0 |
| MSG-009：文書/設定/生成file LF標準 | PG3310 managed text snapshot。v1は既知suffix1678fileを検査し六textを除外と明示、隠れた合格加算0。suffix補完後v2は1684file/24418695byte・除外0・CR0/UTF8異常0/NUL0を実確認（operatora7dd5dc20666f4d3429f9ab21ed6d648d287d7c5）。deployment template19件も含む。scope=documents/src/Maven/root管理text、私有生成物やCurrent baseline、Git外/binaryのLF・秘密scanを実施したとは主張しない。生成固定長binaryは改行追加の対象外、標準LF政策/明示UTF8出力と当artifact内容を照合する。読取のみで正規化0 |
| MSG-010：NFCをbyte長判定より前 | FieldCodec.encodeTextのNormalizer.normalize→strict UTF8→encoded.length判定をSource a9でレビュー、X01のNFD e+accent→c3a9とsemantic path正規化の独立literal、受信NFD拒否。本文を切り詰めてNFCらしく見せない |
| MSG-011：Asia/Tokyo yyyyMMddHHmmssSSS | 共通P003-03/JstWireTimestampTest全四の固定Instant03:34:56.789Z→JST12:34:56.789/17桁、うるう日・小数精度超過・短長・非数字・不正日/月・expanded yearを独立検証。Header/Payload送信側の境界拒否も同Testに含む |

## 品質・終了条件

本対象はimmutable/純変換・local copy/検証のみでDB/transaction/owned resourceを持たない。副作用を伴う再送・broker所有は他ownerに残し、並行は共有codecのP09独立384byte/8workerとimmutable registryを参照する。BUG1285の旧expected由来を受入へ含めず、その新P09とBUG1288の実二誤実装拒否/related85・必要一全3702/同native28を閉じた証拠で判定する。

同sourceの39family全四miss0/当Protocol四100、全六static0/FES-flaky-notrun0、全scope同Main/resource/debug byte、11要求・43artifact・Test ID/原XML/canonical/独立oracle、P001-01/P001-02終了依存の同a9受入を照合する。NPEの正常化は禁止、明示nullable任意入力と内部即時参照preconditionを区別する。静的注釈だけ・counter100だけ・hash存在だけで認定0。

契約matrix/actual suite witness/whole-native proofのhashを持つ個別reviewを厳格audit前/候補/後で適用して初めてACCEPTEDへ進める。正式1964/53・工数null/QA051final保留・全体の残counter/他WBSは維持し、IT/ST完了とはしない。
