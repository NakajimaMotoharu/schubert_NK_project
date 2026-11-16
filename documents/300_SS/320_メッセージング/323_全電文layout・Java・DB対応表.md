# 全電文layout・Java・DB対応表

## 1. 目的・追跡

UI 233で確定した64 layoutをJava record、処理class、PostgreSQL型/table、validation・変換規則へ割り当てる。Byte位置・長さ・必須条件は
UI 232～236を変更せず正とし、本書は実装境界を追加する。

- 関連UI: 232～236、241～242、261 SS-001/004～006/013
- 関連RD: MQ-014～045、MSG-001～011、DAT-004～011、FUN-001～013
- 関連QA/RDF/UIC: QA-017～020、025～032、034～040、RDFなし、UICなし

## 2. 共通Java/DB変換

| Wire/semantic | Java protocol | Domain/Application | PostgreSQL | Validation・変換 |
|---|---|---|---|---|
| N12 ID | `long`＋`*Id` wrapper | `long` | `bigint` | 0/1～999999999999、identity MAXVALUE/CK |
| N9 count/version/size | `long` | `long` | `bigint` | field別上限、version 0～999999999 |
| N6 page/count | `int` | `int` | `integer`/算出値 | 0～999999、pageは1以上 |
| N3/N4 order/count | `int` | `int` | `smallint`/`integer` | field別範囲 |
| N17 timestamp | `Instant` | `Instant` | `timestamptz` | WireはAsia/Tokyo17桁、DB/JVMはinstant |
| X timestamp17 | `Optional<Instant>` | nullable `Instant` | nullable `timestamptz` | 全space=null、値ありはstrict parse |
| UUID36 | `UUID` | `UUID` | `uuid` | lowercase canonical wire |
| Context64 | Redacted wrapper | `AuthenticationContext` | raw非保存、hash`char(64)`/cipher`bytea` | 64 lowercase hex、constant-time lookup |
| SHA-256 64 | `Sha256Hex` | 同左 | `char(64)` | lowercase hex |
| X enum | Java enum | domain enum | `varchar`＋CHECK | Allowlist、未知値拒否 |
| X text | `String` | String/value object | text/varchar/char | NFC、octet上限、control/末尾space |
| B | boolean | boolean | boolean | 0/1、error filler spaceは未設定 |
| Relative path | `RelativePath` | logical path | text | 絶対/`.`/`..`/空segment/backslash/NUL拒否 |
| Display path | `DisplayPath` | 表示専用 | text | NFC/sanitize/escape、OS解決禁止 |

Protocol recordは`dev.codex.schubert.nk.protocol.layout.*`、handlerは`dev.codex.schubert.nk.api.dispatch.handler.*`、Web mapperは
`dev.codex.schubert.nk.web.mapper.*`へ置く。Table欄の`—`は永続DB fieldを持たない算出/固定値を示す。

## 3. 認証・Scenario 16 layout

| Layout (data/record/max/total) | Java data / record | API handler・service | DB source/target・型要点 | Validation/trace |
|---|---|---|---|---|
| `LGNREQ01` 384/0/0/640 | `LoginRequestData` | `LoginHandler` -> `AuthenticationService.authenticate` | `app_users`, `login_ip_attempts`, `auth_sessions`; username text、IP inet | Context space、password redacted、UI 234 §3、FUN-001/MQ-021 |
| `LGNRSP01` 432/0/0/688 | `LoginResponseData` | `LoginResponseFactory` | auth session raw復号結果、user role | Code別presence、retry 0～900、header context space |
| `LOGREQ01` 0/0/0/256 | `LogoutRequestData`（singleton） | `LogoutHandler` -> `AuthSessionService.revoke` | `auth_sessions.context_hash` | Header context必須、UI 234 §4、AUT-004 |
| `LOGRSP01` 24/0/0/280 | `LogoutResponseData` | `LogoutResponseFactory` | `revoked_at timestamptz` | 0000/0200で日時必須 |
| `GAMREQ01` 0/0/0/256 | `GameListRequestData` | `GameListHandler` | — | Context必須 |
| `GAMRSP01` 9/272/10/2,985 | `GameListResponseData` / `GameRecord` | `ScenarioQueryService.findGames` | `games`: smallint/text/display_order | Count一致、code/title/order、UI 234 §5 |
| `SPKREQ01` 12/0/0/268 | `SpeakerListRequestData` | `SpeakerListHandler` | `games.code` | Game optional allowlist |
| `SPKRSP01` 9/152/500/76,265 | `SpeakerListResponseData` / `SpeakerRecord` | `ScenarioQueryService.findSpeakers` | `speakers.id/name`、COUNT entry | Count desc/name asc、UI 234 §6 |
| `SRCREQ01` 672/0/0/928 | `ScenarioSearchRequestData` | `ScenarioSearchHandler` | Query parameterへmap | Page=1..999999、size=100、全条件allowlist |
| `SRCRSP01` 48/5,584/100/558,704 | `PagedResponseData` / `ScenarioSearchRecord` | `ScenarioQueryService.search` | `script_entries/files/games/speakers/audio`; bigint/text/boolean | display_order、代表voice最小order、UI 234 §7/FUN-003 |
| `RTEREQ01` 12/0/0/268 | `RouteListRequestData` | `RouteListHandler` | `games.code` | Game必須 |
| `RTERSP01` 9/72/50/3,865 | `RouteListResponseData` / `RouteRecord` | `ScenarioQueryService.findRoutes` | section prefix算出、COUNT files | Prefix asc、固定route map、UI 234 §8 |
| `SCFREQ01` 14/0/0/270 | `ScenarioFileListRequestData` | `ScenarioFileListHandler` | game/prefix query | Game/prefix必須 |
| `SCFRSP01` 88/800/500/400,344 | `ScenarioFileListResponseData` / `ScenarioFileRecord` | `ScenarioQueryService.findFiles` | `script_files`、entry COUNT | Display title fallback、display_order、UI 234 §9 |
| `SCNREQ01` 12/0/0/268 | `ScenarioDetailRequestData` | `ScenarioDetailHandler` | `script_files.id` | ID 1以上 |
| `SCNRSP01` 1,728/4,800/200/961,984 | `ScenarioDetailResponseData` / `ScenarioEntryRecord` | `ScenarioQueryService.findScenario`、`LargeResultWriter` | entries/audio links、transfer file descriptor | I/F排他、file mode最大10,000/48MB、UI 234 §10/FUN-004～005 |

## 4. Media・Log 18 layout

| Layout (data/record/max/total) | Java data / record | API handler・service | DB source/target・型要点 | Validation/trace |
|---|---|---|---|---|
| `AUDREQ01` 16/0/0/272 | `AudioDescriptorRequestData` | `AudioDescriptorHandler` | `audio_files.id` | disposition I/A |
| `AUDRSP01` 1,024/0/0/1,280 | `MediaDescriptorData` | `MediaQueryService.describeAudio` | audio path/name/size/hash/container | Root/size/hash、`.ogg`=`audio/ogg`、UI 235 §2～3/FUN-005、SSC-004 |
| `ANMREQ01` 0/0/0/256 | `AnimationMenuRequestData` | `AnimationMenuHandler` | — | Context必須 |
| `ANMRSP01` 16/0/0/272 | `AnimationMenuResponseData` | `MediaQueryService.animationCounts` | `media_assets` aggregate | 15/4/1/20 current baseline、UI 235 §4 |
| `ANLREQ01` 16/0/0/272 | `AnimationListRequestData` | `AnimationListHandler` | media category | MAIN/OVA |
| `ANLRSP01` 8/928/50/46,664 | `AnimationListResponseData` / `AnimationRecord` | `MediaQueryService.findAnimation` | `media_assets`: logical_id/text/size/parent/order | Parent/category整合、UI 235 §5 |
| `VIDREQ01` 64/0/0/320 | `VideoDescriptorRequestData` | `VideoDescriptorHandler` | logical_id | 223の20 ID allowlist/DB存在 |
| `VIDRSP01` 1,808/0/0/2,064 | `VideoDescriptorResponseData` | `MediaQueryService.describeVideo` | `media_assets`＋file metadata | MEDIA1024 `.mp4`=`video/mp4`＋title/category/display path、UI 235 §6/FUN-006、SSC-004 |
| `MCTREQ01` 0/0/0/256 | `MusicCategoryRequestData` | `MusicCategoryHandler` | — | Context必須 |
| `MCTRSP01` 8/72/20/1,704 | `MusicCategoryResponseData` / `MusicCategoryRecord` | `MediaQueryService.findMusicCategories` | media_assets aggregate | 曲/BGM/名称順、UI 235 §7 |
| `MCSREQ01` 64/0/0/320 | `MusicSectionRequestData` | `MusicSectionHandler` | category text | 返却master値と一致 |
| `MCSRSP01` 8/136/100/13,864 | `MusicSectionResponseData` / `MusicSectionRecord` | `MediaQueryService.findMusicSections` | category/section aggregate | Section順、UI 235 §8 |
| `MTRREQ01` 192/0/0/448 | `MusicTrackRequestData` | `MusicTrackHandler` | category/section text | DB存在・組合せ |
| `MTRRSP01` 16/1,312/200/262,672 | `MusicTrackResponseData` / `MusicTrackRecord` | `MediaQueryService.findMusicTracks` | `media_assets`: pair_key/role/order | Pair role M/I/N、順序、UI 235 §9/FUN-007 |
| `MEDREQ01` 72/0/0/328 | `MusicDescriptorRequestData` | `MusicDescriptorHandler` | logical_id/disposition | I/A |
| `MEDRSP01` 1,024/0/0/1,280 | `MediaDescriptorData` | `MediaQueryService.describeMusic` | media_assets metadata | `.m4a/.mp3/.ogg/.wav/.flac`と`audio/mp4,mpeg,ogg,wav,flac`の完全一致、UI 235 §10、SSC-004 |
| `LGSREQ01` 656/0/0/912 | `LogSearchRequestData` | `LogSearchHandler` | app_logs query | ADMIN、31日、size100、UI 235 §11/FUN-008 |
| `LGSRSP01` 48/2,088/100/209,104 | `PagedResponseData` / `LogRecord` | `LogQueryService.search` | `app_logs`: bigint/timestamptz/jsonb/inet text projection | 日時/id desc、秘密値なし |

## 5. User管理 14 layout

| Layout (data/record/max/total) | Java data / record | API handler・service | DB source/target・型要点 | Validation/trace |
|---|---|---|---|---|
| `USRREQ01` 96/0/0/352 | `UserSearchRequestData` | `UserSearchHandler` | app_users filters | ADMIN、page size50 |
| `USRRSP01` 48/168/50/8,704 | `PagedResponseData` / `UserRecord` | `UserQueryService.search` | app_users＋active session count | username asc、state導出、UI 236 §3 |
| `UCRREQ01` 372/0/0/628 | `UserCreateRequestData` | `UserCreateHandler` | app_users INSERT、request_inbox | Password redacted/HMAC、token、ADMIN、UI 236 §4 |
| `UCRRSP01` 24/0/0/280 | `UserMutationResponseData` | `UserCommandService.create` | user id/version | 0000/0200同profile |
| `UDTREQ01` 12/0/0/268 | `UserDetailRequestData` | `UserDetailHandler` | app_users.id | ADMIN |
| `UDTRSP01` 320/0/0/576 | `UserDetailResponseData` | `UserQueryService.detail` | app_users、auth_sessions count、actor join | Nullable日時、SYSTEM fallback、UI 236 §5 |
| `USTREQ01` 60/0/0/316 | `UserStatusRequestData` | `UserStatusHandler` | app_users UPDATE、session revoke、inbox | target/version/token、自己/ADMIN保護 |
| `USTRSP01` 24/0/0/280 | `UserMutationResponseData` | `UserCommandService.changeStatus` | user id/version | 0105はerror filler |
| `URLREQ01` 68/0/0/324 | `UserRoleRequestData` | `UserRoleHandler` | app_users role UPDATE/revoke | role enum、active ADMIN lock |
| `URLRSP01` 24/0/0/280 | `UserMutationResponseData` | `UserCommandService.changeRole` | user id/version | 0000/0200 |
| `UPWREQ01` 324/0/0/580 | `PasswordResetRequestData` | `PasswordResetHandler` | password_hash UPDATE、session revoke、inbox HMAC | Password非保存、policy/token/version |
| `UPWRSP01` 24/0/0/280 | `UserMutationResponseData` | `UserCommandService.resetPassword` | user id/version | 0000/0200 |
| `ULKREQ01` 60/0/0/316 | `UserUnlockRequestData` | `UserUnlockHandler` | app_users/login counter UPDATE | token/version、非lockは0200 |
| `ULKRSP01` 24/0/0/280 | `UserMutationResponseData` | `UserCommandService.unlock` | user id/version | 0000/0200 |

## 6. 質問・通知・回答 14 layout

| Layout (data/record/max/total) | Java data / record | API handler・service | DB source/target・型要点 | Validation/trace |
|---|---|---|---|---|
| `QSBREQ01` 4,144/0/0/4,400 | `QuestionSubmitRequestData` | `QuestionSubmitHandler` | questions/jobs/notifications/outbox/inbox INSERT | A区分、本文1～4096、token、UI 236 §7/QST-001～003 |
| `QSBRSP01` 64/0/0/320 | `QuestionSubmitResponseData` | `QuestionCommandService.submit` | receipt char26、question id、submitted_at | Outbox SENT後、0000/0200 |
| `NTSREQ01` 64/0/0/320 | `NotificationSearchRequestData` | `NotificationSearchHandler` | notifications owner query | 本人、366日、size50 |
| `NTSRSP01` 48/624/50/31,504 | `PagedResponseData` / `NotificationRecord` | `NotificationQueryService.search` | notifications/questions | State/type整合、deleted summary、UI 236 §8 |
| `NTDREQ01` 12/0/0/268 | `NotificationDetailRequestData` | `NotificationDetailHandler` | notification id | Owner predicate |
| `NTDRSP01` 8,896/0/0/9,152 | `NotificationDetailResponseData` | `NotificationQueryService.detail` | notifications/jobs/questions/answers | State日時/本文presence、deleted本文space、UI 236 §9 |
| `NTCREQ01` 48/0/0/304 | `NotificationCancelRequestData` | `NotificationCancelHandler` | jobs/notifications UPDATE、inbox | Owner、RECEIVED CAS、token |
| `NTCRSP01` 32/0/0/288 | `NotificationCancelResponseData` | `QuestionCommandService.cancel` | state/cancelled_at | 0000/0200/0107 profile、UI 236 §10 |
| `QSSREQ01` 384/0/0/640 | `QuestionSearchRequestData` | `QuestionSearchHandler` | questions/answers owner query | USER username space、ADMIN optional、366日 |
| `QSSRSP01` 48/672/50/33,904 | `PagedResponseData` / `QuestionSummaryRecord` | `QuestionQueryService.search` | questions/users/answers/jobs | deleted=false、submitted/id desc、UI 236 §11 |
| `QSDREQ01` 12/0/0/268 | `QuestionDetailRequestData` | `QuestionDetailHandler` | question id | USER owner/ADMIN |
| `QSDRSP01` 8,352/0/0/8,608 | `QuestionDetailResponseData` | `QuestionQueryService.detail` | questions/users/answers/jobs | deleted 0104、answer state/presence、UI 236 §12 |
| `QDLREQ01` 48/0/0/304 | `QuestionDeleteRequestData` | `QuestionDeleteHandler` | questions/answers UPDATE、inbox | Owner/ADMIN、token、UI 236 §13 |
| `QDLRSP01` 24/0/0/280 | `QuestionDeleteResponseData` | `QuestionCommandService.logicalDelete` | deleted_at timestamptz | 0000/0200、notification不変 |

## 7. 内部event 2 layout

| Layout (data/record/max/total) | Java data | Listener/service | DB source/target | Validation/trace |
|---|---|---|---|---|
| `QWKREQ01` 64/0/0/320 | `QuestionWorkData` | `QuestionWorkListener` -> `QuestionWorkerService` | questions/jobs/notifications/answers | E/I、context space、DB再取得、TTLなし、UI 236 §14/ASY-002 |
| `WLGEVT01` 2,080/0/0/2,336 | `WebLogEventData` | `WebLogListener` -> `WebLogIngestService` | `app_logs.source_message_id` UK INSERT | E/I、context space、producer role、本文/query/cookieなし、UI 235 §12/MON-003 |

本書のlayout行数は64件でなければならない。PG/CIではbacktick内8文字layout IDを抽出し、重複0、UI 233の集合と完全一致を検査する。

## 8. Paged response mapping

`PagedResponseData`はSRCRSP01/LGSRSP01/USRRSP01/NTSRSP01/QSSRSP01で再利用するが、layoutごとのdata lengthは全て48であることを
registryで別definitionとして保持する。DB query結果から次をchecked arithmeticで算出する。

```text
totalPages = max(1, ceil(totalCount / pageSize))
effectivePage = min(max(requestPage,1), totalPages)
first = totalCount == 0 ? 0 : (effectivePage-1)*pageSize+1
last  = min(effectivePage*pageSize,totalCount)
```

Total countがpage size別のUI上限を超える場合はrecordを一部返さず`9001`。

## 9. Inbox・operation fingerprint対象

| Layout | Owner | Target canonical | Payload canonical（token/reserved除外） |
|---|---|---|---|
| LGNREQ01 | `ANONYMOUS` | `LOGIN:<username_key>:<canonical client IP>` | NFC username、NFC password、canonical client IP |
| UCRREQ01 | actor user ID | `NEW_USER:<username_key>` | username original/key、password value、role、enabled |
| USTREQ01 | actor | `USER:<id>` | enabled、expected version |
| URLREQ01 | actor | `USER:<id>` | new role、expected version |
| UPWREQ01 | actor | `USER:<id>` | new password、expected version |
| ULKREQ01 | actor | `USER:<id>` | expected version |
| QSBREQ01 | actor | `QUESTION:NEW` | question NFC bytes |
| NTCREQ01 | actor | `NOTIFICATION:<id>` | target ID |
| QDLREQ01 | actor | `QUESTION:<id>` | target ID |

Fingerprintは324のlength-prefixed canonical HMACを使用する。LGNREQ01はoperation tokenなしでMessage ID再配送の同一性検査に使う。
Password/質問本文の平文・単純hashをDBへ保存しない。

### 9.1 Scenario参照要求canonical（SSC-025）

OwnerはAPI認証actorのuser ID十進、targetは`REQUEST:<request layout ID>`、versionは001、operation tokenなし。decode済みの全有効fieldを次の順でNKOP1へ格納する。`X1`はNFC UTF-8（enumはwire値）、`N1`はpadding/signなしASCII十進。Optional未設定はLP length 0xFFFFFFFF、空byteとは区別する。検索実行用のtrim/lowercaseやpage補正をHMAC入力へ先取りせず、受けた有効field自体を拘束する。Header/context/message/correlation/sentAt、reserved、paddingはfieldに含めない。

| Layout | ASCII field名/type-version（順序固定） |
|---|---|
| GAMREQ01 | 0 fields |
| SPKREQ01 | gameCode/X1（optional） |
| RTEREQ01 | gameCode/X1 |
| SCFREQ01 | gameCode/X1、prefix/N1 |
| SCNREQ01 | scriptFileId/N1 |
| SRCREQ01 | bodyKeyword/X1、gameCode/X1、speakerName/X1、chapterTitle/X1、entryType/X1、voiceCondition/X1（以上optional）、page/N1、pageSize/N1 |

`ScenarioRequest.decode`は6 request layoutをallowlistし、共通header/layoutとfixed DATA/semanticを検証した後だけ内部値を生成する。これを同じrequestのcanonicalとread-only Repository振分けへ用い、別modelのfield落ち/順序ずれを防ぐ。Detailはimmutable snapshot（不在Optionalを含む）を返し、file I/Oは行わない。Response作成、認証、Inbox確定、JMS、transaction所有は外側serviceの責務。GAM/SPK/RTE/SCF/SRCは即時projection、SCNはdetail候補を区別する。

### 9.2 Media参照要求canonical（SSC-029）

OwnerはAPI認証actor user ID十進、targetは`REQUEST:<request layout ID>`、version001、operation tokenなし。`X1`はNFC UTF-8（enumはwire値）、`N1`はpadding/signなしASCII十進。次の全有効fieldを順序どおりNKOP1へ格納する。全field必須で、header/context/message/correlation/sentAt/reserved/paddingを混入しない。

| Layout | ASCII field名/type-version（順序固定） |
|---|---|
| AUDREQ01 | audioId/N1、disposition/X1 |
| ANMREQ01 | 0 fields |
| ANLREQ01 | category/X1 |
| VIDREQ01 | videoId/X1 |
| MCTREQ01 | 0 fields |
| MCSREQ01 | category/X1 |
| MTRREQ01 | category/X1、section/X1 |
| MEDREQ01 | trackId/X1、disposition/X1 |

`MediaRequest.decode`は8 requestをallowlistし共通header/固定DATA/semanticを検証。同じ内部値からcanonicalとMediaRepositoryの8 read-only queryへ振り分ける。通常一覧は存在するTypedPayload、3 descriptorだけ実ID不在をOptional.emptyとし、DB整合/上限/基盤障害を不存在へ補完しない。DB descriptorはまだmanifest/物理確認を通しておらず配信許可ではない。認証・Inbox/response snapshot、transaction/物理I/O/JMS所有は外側serviceに残す。

### 9.3 User管理更新要求canonical（SSC-032）

Ownerは現在API認証actor user IDの十進、version001。Targetは§9どおりUCRだけ`NEW_USER:<username_key>`、他は`USER:<id>`。Username keyは既存LoginUsernameのNFC/trim/Locale.ROOT lowercase規則。Payloadのusernameはdecode後NFC原値を拘束し、業務検索・作成用trimを先取りしない。`X1`はNFC UTF-8、`N1`はpadding/signなしASCII十進、`B1`はASCII `0`または`1`の1byte。

| Layout | ASCII field名/type-version（順序固定） |
|---|---|
| UCRREQ01 | username/X1、usernameKey/X1、password/X1、role/X1、enabled/B1 |
| USTREQ01 | enabled/B1、expectedVersion/N1 |
| URLREQ01 | role/X1、expectedVersion/N1 |
| UPWREQ01 | password/X1、expectedVersion/N1 |
| ULKREQ01 | expectedVersion/N1 |

User IDはtargetへ含まれ、§9のpayload表どおり重複fieldを追加しない。Operation tokenはInboxの別keyとして返し、header ID/time/context/CSRF/reserved/paddingとともにcanonical fieldへ混入しない。全5layoutをallowlistし、headerのlayout/version/direction/body長、actual DATA/records、typed semanticを検証してから内部値を作る。同じ内部値からSSC-031 preludeのmutation/targetとUserCommandServiceの入力を生成する。これは認証許可・Inbox NEW判定ではなく、callerが先にそれらを実行する。

Passwordは操作scope内だけの所有char bufferに切り離す。業務commandへは消費される別配列を渡す。CanonicalRequestも独立の所有bufferとして返し、callerが全照合後にcloseする。Request.closeで自分のpasswordをzero fillし、close後のcanonical/command等の再利用を拒否する。wire decodeの一時byteもfinallyで消去、Password/raw token/contextをtoString/log/例外に含めない。

BUG-048/YKT-043の境界明確化: 有効UCR wireのUsernameはUI236 §4.1のASCII allowlistに従い、先頭spaceやslashを許可しない。原値/keyの区別は`New`/`NEW`など有効なcase差で検証する。NFC・byte幅・文字/Password長等のwire semantic不正は既存Protocolの恒久拒否規則を維持する。Web/formと内部commandの防御validationをwireへそのまま持ち込まない。DB依存のUPW target username/password一致はwireだけで判定不能なのでcommand0100、Username重複は0105（UI236 §4.2）。この区別は既存外部仕様/codecを変更するものではない。PG-D-084/PT-ADM-024～027で独立LP/JCE-HMAC/手組byte/実PG dispatch/negative/100独立操作を検証し、外側replay/JMS/HTTPは別gateとして継続する。

### 9.4 User照会2layoutのNKOP1 mapping（SSC-035）

Ownerは現在認証actor user IDの十進、version001、targetは`REQUEST:<layout-id>`。USRはusernamePrefix/X1、role/X1、state/X1、page/N1、pageSize/N1の順、UDTはuserId/N1。X1はdecodeしたNFC UTF-8原値、N1はpadding/signなし十進。USRのoptional3項目はwire全spaceの欠落をNULL LP（FFFFFFFF）として表す。検索repositoryのtrim/lowercaseやページ最終補正をHMACへ先取りせず、受信した有効値そのものを拘束する。

Message ID/context/時刻/reserved/paddingをfieldへ含めず、operation tokenは参照layoutなので持たない。Strict wireのlayout/version/Q/S/固定長/record0/semanticを通過した同じtyped値をread-only ADMIN queryへ渡す。canonicalはcallerがcloseし、request自体を認証・query実行許可にしない。UDT responseは要求target IDと一致、USR responseは固定50件page-size/最終補正/total/page/record件数の整合を確認する。Snapshotは当該query時点の結果であり、replayに現在DBの内容/版を混ぜない。PG-D-088/PT-ADM-040～047。

### 9.5 Log検索要求のNKOP1 mapping（SSC-037）

LGSREQ01は一度だけstrict decodeし、同じ不変値をcanonicalとread-only queryへ渡す。ownerは現在認証したactorのUser ID十進表記、versionは`001`、targetは`REQUEST:LGSREQ01`。fieldの順序・ASCII名・型は次に固定する。

| 順序 | field名 | type-version | 値 |
|---|---|---|---|
| 1 | keyword | X1 | NFC UTF-8原値 |
| 2 | logType | X1 | wire enum値 |
| 3 | action | X1 | NFC UTF-8原値 |
| 4 | path | X1 | NFC UTF-8原値 |
| 5 | level | X1 | wire enum値 |
| 6 | fromAt | T1 | decodeしたInstantのUTC ISO-8601表記（Instant.toString） |
| 7 | toAt | T1 | decodeしたInstantのUTC ISO-8601表記（Instant.toString） |
| 8 | page | N1 | 要求page十進表記 |
| 9 | pageSize | N1 | 要求pageSize十進表記（100） |

先頭7 optional fieldの欠落はNULL LP（FFFFFFFF）とし、空文字との同一視、検索用trim、実効page補正、暗黙日時範囲をcanonicalへ先取りしない。header ID/context/sentAt/reserved/paddingはcanonicalへ含めない。operation tokenはない。T1はwireのms精度を維持し、default timezoneや現在時刻へ依存しない。

LGSRSP01保存結果はrequest/owner/layout/versionへ拘束した暗号化全電文とする。初回0000はCOMPLETED/NONE、確定9001だけERROR/NONE。保存時headerはms、completed_atはμs、retentionは後段Inboxが完了時刻から24時間を所有する。再送成功だけ0200へ変更し、保存record・9001は不変、応答ID/context/correlation/timeは現在要求から再構成する。現在ADMIN認証、HMAC、transaction、JMSは後段application責務であり、このvalue/replay部品だけで認可済みとみなさない。

### 9.6 QSBREQ01のNKOP1 fieldと入力所有（SSC-070）

Ownerは検証済actor.userId十進、layout QSBREQ01/version001、target `QUESTION:NEW`、field count1、field名`question`/type`X1`/値はwire decode後のNFC UTF-8本文とする。本文以外のtoken/header ID/time/context/reserved/paddingはcanonicalへ混入しない。既存§9の対象/意味を変更せずfield名/typeを具体化する。

`QuestionSubmitRequest.decode`はQSBREQ01のQ/A・DATA4144・record0・reservedとUUID/本文を既存共通codecで検証してからowned char[]へ切離し、decode用byteコピーはfinally消去する。`copyQuestion`はcaller-owned clone、canonicalの各bufferは返却後callerが別途closeする。request.closeは本文を消去してterminal、冪等close可・close後の業務access不可。private lockによりcopy/canonicalとcloseの途中状態を公開しない。String型wire DTOや呼出元のFixedPayloadは別所有であり、このcloseで他所有者の全メモリを消去したと主張しない。利用者認証/owner照合、Inbox NEW、DB受付/Outbox送達、保持期限後再送は上位service責務として別gateに残す。PG189/011003～004へ追跡。

## 10. DB rowとwire recordの分離

- RepositoryはDB rowを返し、Application mapperがenum/日時/nullable/owner/deleted状態をdomainへ変換する。
- Protocol mapperはdomainからwire fieldへ変換する。SQL projectionをwire位置順へ直接`Object[]` mappingしない。
- Display pathとstorage pathは異なるvalue objectとし、compiler上相互代入できない型にする。
- Error responseは成功domain objectのdummy値を生成せず、`ErrorResponseFactory`がlayoutのerror filler/profileを構築する。
- `0200`はresult referenceから成功domain objectを再構成し、0000と同じmapperを使用する。

## 11. Trace完了条件

| 確認 | 完了条件 |
|---|---|
| Layout集合 | UI 233 64 = Java registry 64 = 本書64、ID重複0 |
| 長さ | 全layoutで256+data+record×max=最大長、1,000,000以下 |
| Field | UI 234～236全fieldがJava component/validatorへ1:1 |
| DB | 永続fieldが331 columnまたは算出根拠へ対応、型範囲がwire内 |
| Handler | Q layout 31＋E layout 2がhandler/listenerへ一意、S layoutはresponse mapperへ一意 |
| Security | Role/owner/context条件がWeb/API両層へ対応 |

## 12. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-019 | Protocol record名をlayoutの業務名＋Request/Response/Data/Recordで統一する | 64 layoutの検索性とQ/S誤使用防止 | Java registry/catalog naming check |
| SS-D-020 | Storage pathとDisplay pathを別Java value objectにする | UI 237/242、file解決への表示値混入を型で防ぐ | Mapper/ArchUnit/file security PT |

## 13. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | 全64 layoutのJava class、handler/service、DB型・table、validation対応を初版作成。 |
| 2026-08-31 | 横断監査でLGNREQ01の匿名Inbox HMAC対象を追加し、失敗counterの再配送二重更新を防止。 |
| 2026-09-02 | SSC-004によりMEDIA1024のAudio/Video/Music拡張子・MIME完全一致allowlistを固定。 |

## QA-054 WLGEVT01の限定意味拡張（SSC-336）

UI235 §12.2/SS351 §3.3を適用し、Log typeの固定REQUEST一値を必須REQUEST/ACTION二値へ変更する。REQUESTはHTTP_REQUEST_COMPLETED（Action省略補完を維持）、ACTIONはMENU_VIEWED必須に限定し、LOG_SEARCHEDや他ACTIONをこの電文から取り込まない。WebLogEventData・固定field定義・codec・意味検証・API ingestを同じ契約へ合わせる。

既存64 layoutの集合、WLGEVT01 EVENT/INTERNAL、header256/data2080/total2336、全offset/length/type、認証context space、Role/Username表示用途、source_message_id UKを維持する。app_logsは既存category ACTION許容・action64 byte・source UKで収容でき、今回の承認に伴うDDL/index/grant変更は不要。API LOG_SEARCHEDは別の既存app_logs業務監査経路である。独立golden vectorでREQUEST互換・MENU_VIEWED・未知/交差/欠落の拒否を検証する。

## SSC-442 N12非instance validatorと九識別子の値契約（2026-11-16）

BUG3104/YKT2576のN12共通IdValueをpackage-private static-only interfaceへ表現する。非instance責務のfinalclass宣言と空privateconstructorだけを外し、MAXIMUM=999999999999Lとvalidate(long)の全body/固定IllegalArgumentException文言を保持する。interfaceで冗長なfield staticfinalだけを省き暗黙publicstaticfinalとなるが、型自体のpackage-private境界は維持しpackage外へ新型を公開0、private状態やPatternを公開0。static validateもinterfaceで暗黙publicとなる内部flag差を記録し、全Main参照をsource/owner/行で列挙する。九record constructorのinvokestaticはInterfaceMethodrefへ変わるため全九callerを同じRoot/sourceでfreshcompile・実constructor実行し旧class型helperとのbinary混用禁止、全module/release JAR再構築は後続条件。publicProtocolIdと九recordの型/permits/component/constructor/getter/equality/hash/toStringの既ABI・意味を維持する。九IDだけの正値N12であり0許容のcount等generic数値fieldへ適用を広げない。独立new3通常PTは九factory×正常1/123/MAX・異常LongMIN/-1/0/MAX+1/LongMAX、固定診断、全record同値/異値/null/異型/独立signed32 Long hash/既literal表示、全81型対と実HashMap九key保持を確認する。期待MAXをproduction定数から生成0、private反射/空instance/除外/到達不能合格0。Main11/physical11(10Code・ProtocolId Code0自然N/A)/freshRoot/static/current10CRC-initXML/同run3/raw四100を要求する。元120/124やaccepted17全面再資格を行わず、元raw不足PG35880と旧JARは保全・合算0。RD/UI/DIF変更不要のSS内部詳細、SS322323354914をPG前にmainへ反映する。Actual4/Root2/VMDBkeys/native/aru/HOLD・全451/正式/wholeProtocolModule未受入を維持する。

状態:設計確定・main反映前、製造/通常PT3/全module/正式未完。

## SSC-443 PathSyntax非instance字句検査と二callerの現source契約（2026-11-16）

BUG3107/YKT2579のうちPathSyntax責務だけをpackage-private static-only interfaceへ整理し空privatectorを除去する。二私有Patternの正規表現文字列を完全保持し、各利用method内のlocal Patternへ移す。interface fieldの暗黙public化で私有cacheを外部公開することは禁止、型はpackage-privateのまま・三static methodの暗黙public内部flag差を記録する。旧静的cacheからmethod毎compileへallocation timingが変わる内部差を明記し、PG/PTで性能又はIT/STを承認しない。先頭slash/backslash/ASCII drive prefix・slash/backslash区切り親segment・ISO control判定の順序/short-circuit/診断/Unicode処理を保持し、Pattern変数名/宣言scopeと型/ctor以外の実bodyを逆展開で一致証明する。二実Main caller RelativePath/DisplayPathはstrictUTF16検査を含む現sourceを不変のままfreshcompileしInterfaceMethodrefと両factory実行を確認、旧helper binaryと新callerの混用禁止。二path公開ABI/正規化/length/segment/equals/hash/redactedtextは不変。独立new3通常PTで境界255/256segment・512/513 UTF8total・空/絶対/drive/root/末尾separator/空dotdotsegment/control・NFC/多byte・同値異値null異型/独立JavaString hash/実HashMapを確認、既PathUnicodeBoundaryTest全2をbyte不変で必要回帰する。三Main/三physicalCode/currentCRC-initXML/freshRoot/static/同run全5/raw四100が限定条件。ProtocolValidatorの別空ctorは未修正OPENとして残し、この範囲へ成功加算しない。元Protocol120/124/accepted17全面requal/旧exec合算0、privateReflection/無意味instance/除外禁止。SS323333354914を製造前にmainへ反映、RD/UI/DIF変更不要。Root2Actual4/DB鍵nativeVMaru等HOLDと全451/正式未受入を維持する。

状態:設計確定・main反映前、製造/通常PT5/全module/正式未完。

## SSC-444 ProtocolValidator非instance責務と現Protocol全module再組立（2026-11-16）

BUG3107/YKT2579残のProtocolValidatorをpublic static-only interfaceへ表現し空privatectorを除去する。既公開PERSISTENT_DELIVERY_MODE=2とvalidateTransport(CommonHeader,TransportMetadata,ExpectedRoute)引数戻り値/例外/null/全分岐順序/固定診断を保持、private PROTOCOL_VERSION文字列001はvalidateTransport内localへ移し新publicfield公開0。classからinterfaceへのpublic型kind差とstatic呼出InterfaceMethodref差を内部Java ABI変更として明記、旧binaryとの混用禁止。全Main参照検索で直接caller FixedWidthDecoderを特定、同source Protocol全165MainをRoot規則でfreshcompile・全physicalを証明し、新helper/旧callerまたは旧helper/新callerの混合を禁止する。IdValue/PathSyntaxの先行型整理も含むため、必要なmodule再組立と通常全140PTを当source一回だけ行う。原130は成功確認で再演するのでなく、三helper型変更の下流/64layout/JMS transport snapshot/QA054/Unicode/独立goldenを同source/moduleで回帰する依存検証。既原130と追加N12三/WireEnum四/Path三の全31source(一helper含む)・五独立TSVを無変更で使用し、元source期待値をproduction methodで置換0。公開record constructor/getterに対する既public反射は固定UI由来型表/nonnull negative契約の範囲だけでprivate反射/Root権限反射無し、元有限2workerの期限/cleanup保持。実物DB/JMS接続/FS/master/鍵/VM/native/aruは操作しない。memory byte streamとtest literalのみ、枠/空き/所有を確認して新job一回とし重複起動禁止。標準coverageはdefaultfilter由来値として保存し、同singleexec全physicalのrawCodeも独立測定、missがあれば全451/当Program受入を保留・修正前BUGへ起票する。Interface/Code0/branch0は自然N/A、除外/旧exec合算/成功算術加算禁止。元904.85/SV/群開始見積保持、477停滞是正として細かなutility追加から一つの実module/caller/source閉包へ作業順を変更するが工程scope/品質/モデル/HOLDは変更しない。SS322323354914をPG前にmain反映、RD/UI/DIF変更不要。正式1964/53・正本184/625・元17/190・工数nullのまま、module回帰成功だけで全PGPT/ITST完了にしない。

状態:設計確定・main反映前、製造/通常PT140/全module/正式未完。

## SSC-445 Payload型registryの状態所有とprivate binding責務（2026-11-16）

BUG3111/YKT2583のうちPayloadTypeCatalogとprivate補助Mapping/RecordMapping責務だけを整理する。公開finalclass/四static APIの型・引数戻り値・例外/diagnostic・全64layout key/69namedtype・decoder methodref/登録順と不変Map/読取順序を保持する。privateSTANDARD cacheはclass初期化時に一回生成する実cache owner INSTANCEのprivatefinal standardへ移す。privateconstructorはこの不変registry実状態を確立し全lookupが参照する責務を持つためのもので、試験から無意味なinstanceや反射で空ctorを呼ばない。JLS class初期化とfinalfield safe publicationを保持し新publicinstance/API/可変cache公開0、性能/heap量は未測定でITST承認しない。二private recordはvalue-equality対象ではないdecoder bindingなのでprivate static final field-only classとし、実使用dataType/dataDecoder/recordMapping・recordType/recordDecoderのprivategetterとconstructorだけを定義する。外部から利用不能でsource検索上未使用のrecord由来equals/hash/toStringとMapping.layoutId accessorは生成せず、registry keyと重複するlayoutId component/privatefactory引数を除く。64Map.entry keyは不変、各mapping引数先頭に重複していた同じkey literalだけを除き、逆展開時は当Map.entry keyから元重複literal/旧privatefactory二signature/元record表現へ復元して全body/表/diagnosticをformatted完全一致で証明する。対象削除はprivateに不要なvalue APIの責務整理でありcoverage除外や到達不能合格としない。private全constructionは固定class literal/methodref/Optional.empty-or-ofに閉じたnonnull入力をRoot静的解析で確認、任意入力/private反射を追加しない。全Main参照をsource/ownerで保存し公開API javap完全一致を確認、他164Mainと既32Test source/五TSVの期待を保持する。新通常1は独立named-types-ss323.tsv64行からexpected class名/record有無を作り、有限二reader/ready-start latch/future10sec/finally shutdownNow-await10secで全64lookupを同時検証、128観測を128Testへ増幅0。初回cold-initを実測したと断定せず公開同時readとJLS安全公開根拠を分ける。Main変更の下流として同source全165Main/176physicalをfresh組立・既144＋新1＝全145通常PTを一回実行、旧source成功/exec転用0。Code変化はparent＋private2 classだけが想定で他173classのbyte一致を確認、parent/private2全Code raw100・全module rawは実値と不足を保存し全451へ昇格0。SS322323354914をPG前にmain反映、RD/UI/DIF変更不要。モデル/枠/Root2Actual4/実DB鍵VMnativearu/QA051final等HOLDと正式1964/53・正本184/625・工数nullを維持する。

状態:設計確定・main反映前、製造/通常PT145/全module/正式未完。

## SSC-446 固定長field paddingの三値dispatch（2026-11-16）

BUG3111/YKT2583のFieldDefinition compact constructor内のpadding選択だけを詳細化する。wireTypeは先行Objects.requireNonNullでnonnullを確立、承認済みWireTypeはTEXT/NUMERIC/BOOLEANの三定数に閉じる。TEXTならSPACE_RIGHT、NUMERICならZERO_LEFT、それ以外の現三値中BOOLEANならNONEという対応を、final local expectedへのif/else-if/else代入で明示する。三入力の対応・不一致時の既存診断・全null/範囲/end検査・両publicconstructor/recordcomponent/全API・独立UI TSV/期待値を変更しない。新enum定数追加はこの既定処理を無審査で流用せずwire型/設計/codec/全対応試験の変更対象とする。javac enum switch由来の理論上のunknown default/補助mapを作る必要がない責務へ整理するもので、列挙値の不正注入や反射、coverage除外、未実行を到達不能PASSに変換しない。型kindはrecordのままで公開ABI javap完全一致、変化Mainはこの一sourceのみ。元switch全byteを逆展開formatted完全一致で証明、他164Main/既全Test/五TSV不変。全165Mainを当sourceでfresh組立、physicalは元176からFieldDefinition$1のみ非生成となる175、親以外174class byte不変を独立照合。新JUnit定義0、現集約4＋必要原14＝同18を当sourceで一回必要再実行し現七class raw全line/method/class/branch100と全physical不足を別保存する。四mapを除外せず三残mapをrawで測定、全module/451/native/正式受入へ昇格しない。RD/UI/DIF変更不要、SSC設計を先にmain反映後PG。全HOLD/枠停止条件/正式1964-53/正本184-625/工数null維持。

状態:設計確定・main反映前、製造/通常PT18/全module/正式未完。
