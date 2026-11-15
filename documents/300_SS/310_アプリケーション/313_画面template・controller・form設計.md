# 画面template・controller・form設計

SSC327（2026-10-21、WebNativeRuntime component PT）：ordinary Webの実startup body/五volatile公開/二ownerLock/五borrowed aliasを、実Root許可とは分離した自己所有DB/JMS/HTTPで検証するため、同package内の既標準functional型によるI/O portを追加する。Productionの既5引数constructorとWebProcessMain唯一の5引数構築は維持し、directory Acquire・path BiFunction・port ToIntBiFunction・directory検証OwnedActionを固定native method referenceへbindする。追加の9引数constructorは内部component用のみで、CLI/YAML/ENV/HTTP/署名・権限へ選択入口を設けない。通常配置の固定path/OS identity/port値・Root admission/promote・業務/画面/電文/DBは不変更。SS343/354、WEBOWN327001～007に追跡し、既空owner成功を当実startupの代替にしない。

## SSC325 Web借用frameのUNKNOWN診断故障

WebRuntimeExecution.executeでcloseが未確認となった場合、固定「WEB cleanup unconfirmed」の診断自体がRuntimeException/Errorをthrowしても元borrowed frameをunwindしない。保護診断と固定有限観測policyは取得前に準備し、start/await/stop/close callbackと元unconfirmedを同frame loop内の到達性fenceで保持する。正常順序・stop通知の既非throwing native実装と例外順位は変更せず、再close・外側finally・正常終了への読替えを禁止する。VM致命終了まで保証するものではなく、当component成功で実native安全条件を代替しない。

## SSC324 Web startup cleanupの依存owner保持

BUG1574/YKT1329：WebLogApplicationRuntimeが取得済みのReplay/repliesをstartup失敗後に閉じる順序はReplay→repliesとし、最初のcloseがchecked/RTE/Errorで未確認なら後続close/再close/正常return/外側unwindを禁止する。固定UNKNOWN retention policyは資源取得より前のclass初期化で準備する。cleanup開始後にarray/保持callbackを新規割当せず、元startup failure・失敗した資源・後続ownerをreachability fence付き同じ呼出frameへ保持する。固定秘匿診断だけ、割込は解放証明ではない。既正常startup/checked failure/通常closeの確認後retry・業務/HTTP/wire/SS352契約は不変更。factoryが返却する前の部分取得や他runtimeのUNKNOWNは別個に照合し、本scope成功から推測しない。

## SSC312 HTTP資源factoryの取得前owner準備（2026-10-21、内部詳細補足）

API/Web管理HTTPは、入力・固定loopback住所/port/backlog32を検証し、owner・全flag/lock・未開始executor（core/max1、queue32、daemon名は既定）・応答情報を先に準備してからHttpServer factoryを一度だけ呼ぶ。取得成功後は追加の未保護allocationを挟まずfinal serverへ格納してownerを返す。取得例外/nullは成功へ変換せず、未取得serverをcloseしない。factory内部で取得後に失敗した資源はfactoryの責務であり、callerが未返却資源を推定回収しない。WebHttpServerも未refreshのMVC context・private final lifecycleLock・ownerを先に準備してからTomcat supplierを一度取得しfinal格納、既startWithOwnerの捕捉callbackとvendor設定/startは既存try内を維持する。未refresh MVCはclose義務のある開始済資源として扱わない。

取得後の既start/stop/destroy/cleanup例外順位・失敗owner再試行・readiness・API8091/Web8081/業務8080・URL/電文/権限/SQL/制限を変更しない。実OOM/実運用漏えいを観測したとの認定ではなく、取得後のowner準備allocation gapを構造上除く。BUG1545/YKT1305、関連SS313/342/354、PG-D461。取得前準備→factory最後→final格納は実ClassFile順序を独立点検し、故意のOOMや稼働VM操作で検証しない。動的PTは通常の有限self-owned fixtureだけ、拒否PT代替や実親/native/配備証明とは分離する。

## 1. 目的・追跡

SSC176内部接続補足（2026-10-04）：SCR007/010/013の4GETは明示ContentDetailMvcConfigurationの一つのbounded参照adapterへ注入する。既存Scenario/Animation/Music階層controllerは維持し、SCN/VID/MTRの既存verified facade・API0102終端handlerと保持済transferのLargeResultReaderを借用する。Scenario IDは既存game経路と混同しないnumeric mappingで受け、FILEはSS333の属性/hash/全record/held能力を検証してから既存ScenarioDetailViewModelへ渡す。fragment `#entry-ID`はHTTPへ送られず既存entry anchor/`:target`によるhighlightを維持、任意anchorを業務要求へ追加しない。VIDは検証済request-bound metadataだけ、Musicはstored pair_key/role/display_orderによる閉display projectionだけをHTMLへ渡し、descriptor/DTO/context/物理pathを入れない。戻り先・title/pair表示・全順序・media/DL操作はUI223/235のまま。borrowed root・DB/JMS/codecの所有を変えず、画面単体成功でSS342 fullreadyを公開しない。追跡PG-D365/PT-CONTENT001～009/016079080、独立literal wire/DOM/file integrity/境界null例外並行・同source品質/実nativeを別受入とする。RD/UI/DIF/電文/DDL変更なし。

SCR-001～023/090と非画面endpointについて、template、controller method、form、View Model、固定長IF、validation、表示・権限制御を定める。

- 関連UI: 221～226、232～237、264
- 関連RD: FUN-001～013、AUT-001～003、TST-001～005、PER-002～004
- 関連QA/RDF/UIC: QA-015、023、034～040、RDFなし、UICなし

## 2. Template構成

```text
templates/
  fragments/layout.html          # head、topbar、nav、flash、footer
  fragments/forms.html           # field/error/CSRF/operation token
  fragments/pagination.html      # 100/50件page共通
  fragments/media.html           # audio/video、download
  fragments/error-summary.html
  login.html
  menu.html
  search.html
  scenarios.html
  scenario-routes.html
  scenario-files.html
  scenario.html
  animation.html
  animation-list.html
  animation-watch.html
  music.html
  music-sections.html
  music-list.html
  logs.html
  admin/user-list.html
  admin/user-new.html
  admin/user-detail.html
  questions/new.html
  questions/accepted.html
  notifications/list.html
  notifications/detail.html
  questions/list.html
  questions/detail.html
  error/error.html
static/
  css/schubert.css
  js/search-speaker-submit.js
```

現行14 templateのファイル名は互換性追跡を容易にするため維持する。新規画面だけsubdirectoryへ配置する。Inline JavaScript、
inline event handler、外部CDNを使用しない。TemplateはView Modelだけを参照し、protocol record、DB row、認証context raw、storage pathを参照しない。

SSC-074/QA-045/UIC-005: SCR-001 LoginのGET controllerは`login` templateのみを返し、認証処理は既存POST `/login` filterへ委ねる。Login templateの可視brandは`schubert NK`、document titleは`schubert NK - ログイン`。Username autofocus/autocomplete、Passwordの空再表示、CSRF、既存error/locked/logout表示・操作はUI226とCurrent互換を維持する。title差分だけをDIF-001/CHR-A01に帰属し、他の比較項目を除外しない。QA-055/UIC-012/SSC-338: locked表示はUI226のCurrent固定15分文を維持する。API確定の実残秒は既存HTTP Retry-Afterだけとし、GET controllerへの動的残秒handoffや新session属性を追加しない。

## 3. Controller共通規約

- Controller packageは`dev.codex.schubert.nk.web.controller`、classは`@Controller`、constructor injectionとする。
- GETは副作用を持たず、更新はPOST＋CSRF＋Post/Redirect/Getとする。
- `BindingResult`のfield error時はMQ送信せず同一templateを再表示する。
- Passwordは再表示、flash、Model、URL、sessionへ保持しない。質問本文はvalidation error時だけrequest scopeで再表示し、sessionへ保存しない。
- 固定長result codeは`WebResultMapper`でHTTP/viewへ変換し、Controller内でcode文字列を分岐しない。
- 全保護methodはWeb側`@PreAuthorize`またはrequest matcherを適用し、API側認可を省略しない。
- Request IDはfilterが生成し、error画面・監査へ渡す。物理path、Queue名、exception messageをModelへ入れない。

## 4. 画面・class対応

### 4.0 Scenario階層のHTTP binding・終端具体化（SSC-071/PG-D-194）

- SCR005は`/scenarios/{game:NUKITASHI[12]}`、SCR006は`/scenarios/{game:NUKITASHI[12]}/{prefix:[0-9]{2}}`とし、SCR007の数値ID segmentと衝突させない。Current SearchControllerのgame/prefix/numeric区別を維持し、未知game・非ASCII/桁不一致prefixはhandlerへ入れない。数値IDは後続明細controllerで別routeとして扱う。
- GAM/RTE/SCF要求は既存ScenarioWireClientへ1回だけ委譲する。保護pathの認証済SessionPrincipalだけからcontextを取得し、request parameterでrole/contextを上書きしない。WebResultMapperで承認済resultをHTTP分類、0102は既存ApiSessionInvalidHandlerへ委譲した後に即終端する。
- SCR004の0件は一覧として空結果文言を表示する。SCR005/006の0件はCurrent SearchController同様404とし、成功コードの空recordを200画面へ変換しない。§6.1のPageViewModelの0件規則はpaged一覧の規則で、この階層404を変更しない。
- SCF応答のgame/prefixを要求値へ照合し、不一致は503で終端、正常時はAPIのrouteName/title/順序をそのまま閉modelへcopyする。DTOや認証contextをHTML Modelへ入れない。
- HTTP送信済みのMVC endpoint戻り値だけはSpring ServletInvocableHandlerMethodのrequestHandled契約に従う`@Nullable String`とする。HttpServletResponse引数を持ち、sendErrorまたは0102 handler完了直後だけnullを返す。成功は固定template名。業務helperはOptional/non-null契約、nullを成功値・欠落補正へ使わない。MVC/実HTTP PTで二重render/後続MQがないことを確認する。
- ScenarioMvcConfigurationで依存を明示注入し、WebMvcConfigurationのview名allowlistへ3templateだけを追加する。これだけで本番bootstrap/全画面登録/実brokerの完了とはしない。共通layoutのuser操作fragmentを共有し、Currentの見出し/業務nav/card/list順を維持する。

追跡: NK-WEB-002、FUN004/AUT001～003/SYS006/TST001～005、UI221～223/234/264、016001/002・PT-SCR-001～016。実NK CHR-S05/S06/U02/E01と本番REQUEST log結線は別gateで未完了を明示する。

| SCR | Method/URL | Template | Controller.method | Form / View Model | Fixed IF | Role・追跡 |
|---|---|---|---|---|---|---|
| 001 | GET `/login` | `login.html` | `LoginController.show(LoginQuery,Model)` | `LoginForm` / `LoginViewModel` | なし | 未認証、UI 226、FUN-001 |
| 001 | POST `/login` | redirect/再表示 | Spring Security `MqAuthenticationProvider` | `LoginForm` | IF-001 | 未認証、AUT-004、MQ-021 |
| 002 | GET `/` | `menu.html` | `MenuController.show(Principal,Model)` | `MenuViewModel` | なし | USER/ADMIN、UI 223、FUN-002 |
| 003 | GET `/search` | `search.html` | `ScenarioController.search(ScenarioSearchForm,Model)` | `ScenarioSearchForm` / `ScenarioSearchViewModel` | IF-003～005 | USER/ADMIN、FUN-003 |
| 004 | GET `/scenarios` | `scenarios.html` | `ScenarioController.games(Model)` | `GameListViewModel` | IF-003 | USER/ADMIN、FUN-004 |
| 005 | GET `/scenarios/{game}` | `scenario-routes.html` | `ScenarioController.routes(GameCode,Model)` | `RouteListViewModel` | IF-006 | USER/ADMIN |
| 006 | GET `/scenarios/{game}/{prefix}` | `scenario-files.html` | `ScenarioController.files(GameCode,RoutePrefix,Model)` | `ScenarioFileListViewModel` | IF-007 | USER/ADMIN |
| 007 | GET `/scenarios/{id}` | `scenario.html` | `ContentDetailController.scenario(String,Model)` | `ScenarioDetailViewModel` | IF-008 | USER/ADMIN |
| 008 | GET `/animation` | `animation.html` | `AnimationController.menu(Model)` | `AnimationMenuViewModel` | IF-010 | USER/ADMIN、FUN-006 |
| 009 | GET `/animation/main`,`/animation/ova` | `animation-list.html` | `AnimationController.list(AnimationCategory,Model)` | `AnimationListViewModel` | IF-011 | USER/ADMIN |
| 010 | GET `/animation/opening`,`/animation/videos/{id}` | `animation-watch.html` | `ContentDetailController.opening/watch(String,Model)` | `AnimationWatchViewModel` | IF-012 | USER/ADMIN |
| 011 | GET `/music` | `music.html` | `MusicController.categories(Model)` | `MusicCategoryViewModel` | IF-013 | USER/ADMIN、FUN-007 |
| 012 | GET `/music/{category}` | `music-sections.html` | `MusicController.sections(String,Model)` | `MusicSectionViewModel` | IF-014 | USER/ADMIN |
| 013 | GET `/music/{category}/{section}` | `music-list.html` | `ContentDetailController.tracks(String,String,Model)` | `MusicTrackViewModel` | IF-015 | USER/ADMIN |
| 014 | GET `/logs` | `logs.html` | `LogController.search(LogSearchForm,Model)` | `LogSearchForm` / `LogSearchViewModel` | IF-017 | ADMIN、FUN-008/AUT-002 |
| 015 | GET `/admin/users` | `admin/user-list.html` | `UserAdminController.list(UserSearchForm,Model)` | `UserSearchForm` / `UserListViewModel` | IF-018 | ADMIN、FUN-009 |
| 016 | GET `/admin/users/new` | `admin/user-new.html` | `UserAdminController.newForm(Model)` | `UserCreateForm` | なし | ADMIN |
| 016 | POST `/admin/users/new` | redirect/再表示 | `UserAdminController.create(UserCreateForm,BindingResult)` | `UserCreateForm` | IF-019 | ADMIN、token |
| 017 | GET `/admin/users/{id}` | `admin/user-detail.html` | `UserAdminController.detail(long,Model)` | `UserDetailViewModel`＋操作別form | IF-020 | ADMIN |
| 017 | POST `/admin/users/{id}` + `operation=STATUS` | redirect/409 | `UserAdminController.changeStatus(...)` | `UserStatusForm` | IF-021 | ADMIN、token/version |
| 017 | POST `/admin/users/{id}` + `operation=ROLE` | redirect/409 | `UserAdminController.changeRole(...)` | `UserRoleForm` | IF-022 | ADMIN、token/version |
| 017 | POST `/admin/users/{id}` + `operation=PASSWORD` | redirect/再表示 | `UserAdminController.resetPassword(...)` | `PasswordResetForm` | IF-023 | ADMIN、token/version |
| 017 | POST `/admin/users/{id}` + `operation=UNLOCK` | redirect/409 | `UserAdminController.unlock(...)` | `UserUnlockForm` | IF-024 | ADMIN、token/version |
| 018 | GET `/questions/new` | `questions/new.html` | `QuestionController.newForm(Model)` | `QuestionSubmitForm` | なし | USER/ADMIN、QST-001 |
| 018 | POST `/questions/new` | redirect/再表示 | `QuestionController.submit(...)` | `QuestionSubmitForm` | IF-025 | USER/ADMIN、token |
| 019 | GET `/questions/accepted/{receiptId}` | `questions/accepted.html` | `QuestionController.accepted(ReceiptId,Model)` | `QuestionAcceptedViewModel` | Web受付参照＋毎GET fresh IF-030照合結果 | 現在API Owner/受付照合、QST-002、QA048 |
| 020 | GET `/notifications` | `notifications/list.html` | `NotificationController.list(NotificationSearchForm,Model)` | `NotificationSearchForm` / `NotificationListViewModel` | IF-026 | 本人だけ、NTF-001 |
| 021 | GET `/notifications/{id}` | `notifications/detail.html` | `NotificationController.detail(long,Model)` | `NotificationDetailViewModel`＋`CancelForm` | IF-027 | 本人だけ |
| 021 | POST `/notifications/{id}` + `operation=CANCEL` | redirect/最新表示 | `NotificationController.cancel(...)` | `CancelForm` | IF-028 | 本人、RECEIVED、token |
| 022 | GET `/questions` | `questions/list.html` | `QuestionController.list(QuestionSearchForm,Model)` | `QuestionSearchForm` / `QuestionListViewModel` | IF-029 | USER本人/ADMIN全件 |
| 023 | GET `/questions/{id}` | `questions/detail.html` | `QuestionController.detail(long,Model)` | `QuestionDetailViewModel`＋`QuestionDeleteForm` | IF-030 | Owner/ADMIN |
| 023 | POST `/questions/{id}` + `operation=DELETE` | redirect | `QuestionController.delete(...)` | `QuestionDeleteForm` | IF-031 | Owner/ADMIN、token |
| 090 | GET `/error` | `error/error.html` | `ErrorController.error(HttpServletRequest,Model)` | `ErrorViewModel` | なし | 全scope、TST-002 |

PathはUI 221のURLをGET/POSTとも維持する。SCR-017は同一POST pathにhidden `operation`を付与し、
`@PostMapping(params="operation=STATUS")`等のallowlistで操作別handler/form validationへ分岐する。SCR-021/023も同じ。
Operation欠落・複数・未知値はMQ送信前に400とし、form actionとpath IDはCharacterization Testで比較する。

### 4.1 SCR016/017のsession・API接続補足（SSC-177）

SCR016/017の通常全構成は同じcurrent session repositoryから作ったtoken lifecycleを明示注入し、旧read-only構成を全Readyへ使わない。SCR017はfresh IF-020に基づく操作別formを表示し、自己無効化/自己ADMIN解除を許すformを出さず、Lock解除はlock中だけ表示する。実際に表示するform群のtokenは314の単一短TXで全確保し、不足時に未表示pendingを部分発行しない。

同POST pathの閉じたoperation dispatcher（又は操作別mapping）でSTATUS/ROLE/PASSWORD/UNLOCKを分離し、欠落/多重/未知operationはMQ前400にする。既存formを借用してpath ID/version/確認/用途tokenを検査し、password確認を電文へ重複送信しない。PasswordResetFormへ与えるtarget usernameは現在の真正IF-020だけを正とし、HTTP hidden値を正にしない。

検証済IF-019/021～024の0000/0200・USRMUT24のtarget/versionを確認してから、現在tokenの初回完成印を保存し固定相対redirectとする。入力error/応答喪失はpasswordを消去して同tokenで再入力し、0105ではIF-020の最新値を取得して409を表示する。再表示だけで新token・API更新・自動再送を行わない。自己Password reset成功はAPIで現在を含む全session失効済なので、現在のlocal sessionとdisplay/security contextを終端消去しLoginへ戻す。追加Logout送信や、受信していない0102の監査は生成しない。他Userの成功・旧保持token再送は従来の現在API認証/owner/HMAC/保存結果検証を省略しない。

IDは1～999999999999、optimistic VersionはSS331/IF-020の0～999999999を正とし、新規Userのversion0を表示・更新formから拒否しない。IF-019新規成功はversion0、変更成功は既存APIのversion更新結果、Lock解除の既解除0200は同versionを維持し得る。IDとVersionへ同じpositive条件を適用しない（BUG639/YKT452、上位変更ではなく実装誤りの是正）。

## 5. Form validation

### 5.1 共通validator

| Validator | 対象 | 規則 |
|---|---|---|
| `NfcByteLength` | 全wire X項目 | NFC後UTF-8 byte数。超過時切捨てなし |
| `NoWireControl` | 文字入力 | CR/LF/TAB/NUL拒否 |
| `NoTrailingAsciiSpace` | Password、質問 | 末尾`0x20`拒否 |
| `AllowedValue` | enum/select | UI定義値だけ。定義外をDB条件へ渡さない |
| `ValidDateRange` | From/To | From≦To、Log 31日、通知/質問366日 |
| `ValidOperationToken` | 更新form | lowercase UUID canonical 36文字、用途とsessionを照合 |
| `ExpectedVersion` | User更新 | ASCII 0～999999999 |

Client-side `maxlength`は補助であり、UTF-8 byte validatorをWeb/API双方で適用する。JavaScriptなしでもserver validationが成立する。

### 5.2 画面別

| Form | 主field | Validation/error key |
|---|---|---|
| `LoginForm` | username 1～64 byte、password 1～256 byte | `login.invalid`は不存在/不一致/disabled共通 |
| `ScenarioSearchForm` | q 256、speaker 128、chapter 256、page 1～999999 | 空をnullへmap、全条件AND |
| `LogSearchForm` | q 256、action 64、path 256、enum、31日、page | USER送信はController到達前403 |
| `UserCreateForm` | username regex/64、password 12～128文字かつ256 byte、確認、role/enabled | Password確認はWebだけ、電文へ1つだけ |
| User変更form | path ID=form ID、version、操作値、確認check、token | ID不一致400、自己保護はAPIで再検証 |
| `QuestionSubmitForm` | question 1～4096 byte、token | 改行/末尾spaceをfield error、byte残量表示 |
| `NotificationSearchForm` | type、From/To 366日、page | ADMINもowner指定fieldなし |
| `CancelForm` | confirm=true、token | 最新stateはAPIで検証 |
| `QuestionSearchForm` | keyword 256、username 64 ADMINのみ、answer state、366日、page | USERがusernameを送れば400 |
| `QuestionDeleteForm` | confirm=true、token | Owner/ADMINはAPIで再検証 |

## 6. View Model・表示制御

SSC-073（LogSearchForm限定）: HTTP fieldはq/log_type/action/path/level/from/to/pageの8個、未知名・同名複数値は400相当でMQ前に拒否する。既存5文字列はCurrent LogSearchFiltersのtrimを維持し、制御文字/不正Unicode検査→NFC→前後ASCII trim→byte/enum検査とする。q256/action64/path256byte、種別空/ACTION/REQUEST/SECURITY/MQ/SYSTEM/BATCH、level空/INFO/WARN/ERROR。pageは欠落/空1、ASCII int範囲内の0以下を1へ補正、正数999999超過・plus・小数・指数・非ASCII数字・overflowは拒否する（UI222§6優先）。

From/ToはDIF010の新条件をdatetime-localで入力し、JST（固定+09:00）のyyyy-MM-ddTHH:mm、任意の:ssと1～3桁小数秒を受ける。秒がない場合は00、毫秒未満は受けない。4桁年0001～9999・実在日付/時刻のstrict検査、timezone suffix/offset/24時/うるう秒は拒否する。空は未指定、片側だけは許可、両側指定時はFrom≦Toかつ差が31日以下（境界含む）。wireへInstantとして渡し既存JST17桁codecで再検査、丸め/切捨てなし。文字列の再表示は閉snapshotとescape、失敗理由は固定field/codeでraw入力を診断へ出さない。ADMIN認可は既存security chainとAPIに維持する。

SSC-072（ScenarioSearchForm限定）: UI222§5/6・223§3とCurrent SearchFiltersの優先規則を明示する。HTTPの7field `q/game/speaker/chapter/entry_type/voice/page` だけを受け、未知名・同名複数値は拒否する。欠落文字列は空、欠落/空pageは1。入力Unicode・制御文字を検査してからNFC/trimし、検索文字列の前後ASCII spaceはtrim対象（Password/質問の末尾space禁止を適用しない）。CR/LF/TAB/NULをtrimで消して受け入れない。byte上限・enum検査は正規化後で、超過切捨てなし。pageはASCII整数、先頭plus/小数/指数/非ASCII数字は拒否する。ただしUI222§6の明示例外として先頭minusの負整数と0は1へ補正する。Currentのint範囲を超える値、正数999999超過はfield error。leading zeroは数値として解釈する。最終pageへの補正は結果総件数を持つAPI側に残す。

内部formは不変snapshotとclosed field/error-code集合を返す。raw入力を例外/診断へ反射しない。文字入力値は画面再表示のためだけに保持しtemplateで必ずescapeする。検証失敗時はtyped検索要求を生成せずMQを送らない。正常時の空文字はwire mapperでOptional.empty（設計上のnull条件）へ写像する。候補取得/HTTP binding/field error描画は別接続試験で確認する。

### 6.1 共通

`PageViewModel`はeffective page、page size、total count/pages、first/last、previous/nextを持つ。0件でもtotal pages=1、first/last=0。
Templateは0件時に`該当するデータはありません`を表示し、pagination linkを出さない。

`TopBarViewModel`はbrand、username、role、Menu/通知/上位link、POST Logout formだけを持つ。認証context/session IDを含めない。

### 6.2 状態・role表示

| 条件 | Template制御 | API再検証 |
|---|---|---|
| USER | Log/User管理card・nav非表示 | IF-017～024を`0103` |
| ADMIN | Log/User管理表示、質問一覧にusername条件/列表示 | APIが最新roleをcontextから取得 |
| Notification RECEIVED | Cancel form表示 | IF-028がowner/state CAS |
| PROCESSING/COMPLETED/ERROR/CANCELLED | Cancel form非表示 | IF-028要求でも拒否/冪等 |
| Question deleted | Notification本文を`削除済み`表示 | IF-027が本文を返さない |
| User self | Disable/ADMIN解除button非表示 | API transactionで拒否 |
| User non-locked | Unlock button非表示 | APIは既解除を0200 |
| Audioなし | Player/download非表示 | Descriptor IFを呼ばない |
| Music pair欠落 | `メインなし`/`インストなし` | Pair metadataをAPI正本とする |

## 7. 現行互換表示

- Menuは2列card、USER 7項目、ADMIN 9項目。現行4項目のtitle/順は264で比較する。
- Searchは100件/page、`script_entries.display_order`、代表voice最小display order、Game/Route/章title fallbackを維持する。
- Scenarioは前後linkを上/下、entry anchor highlight、同一entryの複数voiceをgroup化し本文1回とする。
- Animationは20 logical ID、main/SUBTRACK pair、OVA/openingと16:9 playerを維持する。
- Musicはcategory/section/pair順、129件、欠落placeholder、非`曲`path/MB表示を維持する。
- Logは100件/page・日時降順、REQUESTのHTTP項目、ADMIN限定を適用する。
- 認証済みHTMLは`Cache-Control: no-store`。質問/回答はHTML escapeしMarkdown/link化しない。

## 8. 非画面HTTP endpoint

| Endpoint | Controller.method | API IF | Web service | 応答 |
|---|---|---|---|---|
| POST `/logout` | Security logout handler | IF-002 | `LogoutCoordinator` | 302 `/login?logout`、CSRF必須 |
| GET `/audio/{id}` | `MediaController.audio` | IF-009 I | `MediaRangeService` | 200/206/416、実MIME |
| GET `/audio/{id}/download` | `MediaController.audioDownload` | IF-009 A | `MediaRangeService` | 200 attachment/octet-stream |
| GET `/animation/media/{id}` | `MediaController.video` | IF-012 | `MediaRangeService` | 200/206/416 video/mp4 |
| GET `/music/media/{id}` | `MediaController.music` | IF-016 I | `MediaRangeService` | 200/206/416許可MIME |
| GET `/music/download/{id}` | `MediaController.musicDownload` | IF-016 A | `MediaRangeService` | 200 attachment/octet-stream |

毎回HTTP sessionとAPI contextを検証し、Caddy direct file、storage path反射、認証済みdescriptor cacheを禁止する。

## 9. HTTP/error mapping

| 条件 | Status/遷移 | View/表示 |
|---|---|---|
| 未認証保護GET | 302 Login | Safe same-origin GETだけSavedRequest |
| 未認証POST/media | 401/403 | Login案内、body再送なし |
| Field error | 400相当、同一画面 | Field＋summary、秘密値なし |
| `0102` | Web session破棄、通常GETは302 Login、POST/AJAX/media等は401 | `session-expired` message、更新body再送なし（SSC-048/UI221） |
| `0103` | 403 | 権限なし。対象存在を開示しない |
| `0104` | 404 | 対象なし |
| `0105` | 409 | 最新GETを取得して再表示、新token |
| `0107` | 409相当、通知明細 | 最新stateと取消不可message |
| `9000/9001` | 503 | 再操作案内、request ID |
| Invalid Range | 416 | bodyに内部pathなし |

SSC-047（SCR-090具体化）: ErrorController/ProblemViewFactoryはserver Request ID、containerのERROR_STATUS_CODE、要求内の表示専用snapshotだけからErrorViewModelを作る。ERROR_EXCEPTION、ERROR_MESSAGE、ERROR_REQUEST_URI、query、raw request/session/DBを参照しない。400/401/403/404/405/409/416/429/503は固定表示、500/未知statusは503へ分類、error属性なしの直接GET /errorは404とする。response statusとModelを一致させ、利用者文言はUI222の既定403/404/409/503を維持する。認証済みsnapshotがある場合だけusername/role/Logout＋解決済hidden CSRF、ない場合はMenu/Login案内を表示する。通常画面から使う認証失効handlerはsnapshotの破棄も行う。 外部/errorはGET/HEADだけを表示用として受け、他methodは405＋Allow: GET, HEADとする。内部ERRORでは元methodを業務実行せずerror statusだけ表示する。

## 10. Accessibility・security

- `lang=ja`、一意な`title`、見出し階層、landmark、label/id、validation summary anchorを必須とする。
- Focus outlineを消さず、状態を色だけで示さない。破壊操作は確認checkbox＋明示POST buttonとする。
- 900px以下は1列。Tableはheaderを保ったscroll containerまたはcardへ変換する。
- CSPは`default-src 'self'`、scriptも`'self'`だけ。CSRF、cookie、token、physical pathをDOM data属性へ出さない。
- Password fieldは常に空で再表示し、question/answer/request bodyをREQUEST logへ出さない。

## 11. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-007 | 現行14 template名を維持し、新規画面だけsubdirectory化する | UI 221～223、264。比較とCSS移植を容易にする | CHR DOM/screenshot selectorを安定化 |
| SS-D-008 | SCR-017/021/023はUI 221の同一GET/POST URLを維持し、hidden operationとrequest-param allowlistでhandlerを分離する | 外部URLを変更せず、CSRF/認可/validationを操作別に明確化 | Form action/operation正負PT、CHRでURL比較 |
| SS-D-009 | Templateへprotocol/DB objectを直接渡さない | Storage path/秘密値の誤露出防止 | Mapper PT、ArchUnit/template model review |

## 12. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | 全画面・endpointのtemplate/controller/form/validation/表示制御を初版作成。 |
| 2026-08-31 | 横断監査でUI 221のPOST URL維持とhidden operation分岐へ是正。 |

## QA-048承認反映：SCR019 locatorと業務照合（2026-10-03）

業務側DB（APIが管理するquestions/関連業務data）が正である。`schubert_web_session.web_receipt_references`はreceiptIdからquestionIdを解決するためのtechnical locatorだけとし、検証済IF025のreceiptId/questionId/submittedAtの3値以外を保存しない。本文・回答・password・認証context・operation token・owner・結果snapshot・検証済flagを蓄積しない。

SCR019のGETごとにlocatorを読む短Web transactionを終了してからfresh MessageIDのIF030を現在API認証で呼び、API側の現在owner認可に加えてquestionId/receiptId/submittedAtを照合する。日時比較は既存wireのUTC millisecond精度へ揃え、DBの追加microsecondを誤不一致にしない。表示はこの要求で取得したAPI結果だけをHTML escapeし、request scopeへ置く。不一致・他人・削除済み・locator欠落・API確認不能は既存error処理へ進め、古いlocatorやsessionから受付成功/本文を補わない。

IF025成功後のWeb保存は3値をimmutableに登録する。同receiptの同値再登録は冪等、異なる値の競合は上書きせず非成功・診断とする。業務commitとWeb保存は別transactionなので一時欠落が起こり得る。その際、業務受付を取り消したと仮定せず、新operation tokenで質問を再生成しない。保持中の同token/同入力の正規再操作からAPIの既存確定受付結果を取得し、Web参照登録を再試行する。参照欠落のURLだけからquestionIdを推測して復元する保証はしない。

Backup/restore後もWeb値は信頼せず毎GETのAPI検証を省略しない。修復は正規APIの検証済み結果を根拠にWeb参照を合わせる片方向とし、Web参照を正として業務DBを書き換えない。Webから業務schemaへの直接接続/FK/権限は追加しない。cleanupは当日backup gateの下、業務質問が物理削除されたlocatorだけを固定保守functionで削除し、存続する質問のlocatorへ独自TTLを設定しない。実装・DDL適用・独立PTは未完了であり、QA048承認による設計条件である。

独立PTは本人正常/他人/別受付/時刻不一致/欠落/論理・物理削除/API障害/HTML escape、IF025業務成功後Web保存失敗→同token再操作、同値再登録/競合、backup復元の古いlocatorを含む。Web参照だけから成功を返したり、API本文をsessionへ保存した場合は不合格とする。

## SSC-430 Web form分類のfatal保全と有限単体試験（2026-11-16）

LoginFormAuthenticationConverter.convertの既catch(IllegalArgumentException|IllegalStateException|NoSuchElementException)では、固定LoginFormRejectedExceptionへ変換する前に既SessionStoreException.preserveFatal(failure)を呼ぶ。元Error/cause/suppressed/SQLnextをidentity seenで有限走査する既helperを再実装せず、Error無しの例外は原因/診断を保持しない同じ固定input rejectionを返す。通常POST/login/UTF8/contenttype/charset/query予約名/parameters多重-null/数値proxy信頼/非認証token/char[]受渡し/CSRF前提/公開API/400入力拒否と403proxy拒否/ログ秘匿/上位503分類/承認DIFを変更しない。外部設定/provider/資格/権限/実認証/DB/MQ/鍵/Root2Actual4/VM/native/aru/HOLDを追加しない。元LoginFormConverterPortTest全13の全入力/独立HTTP・token・配列消去期待はinverse exact保持、八task/二worker/既Futureget10を保ちfinally shutdownNow/await10assert/classTimeout30へ有限化する。新FORM014は三分類例外それぞれcause/suppressed内の公開合成AssertionErrorをgetMethod/getParameterValuesから与え元Error同一/固定正常結果0を検証、新FORM015はError無しcause循環/共有suppressedの固定秘匿分類と未分類RTE同一を確認する。既JDK Servlet-interface proxyだけを使いMockserver/actualcontext/key/native/JDBCを起動0。safe MainはConverter/CaddyResolver/LoginClientAddress/FormRejected/CaddyRejected/SessionStoreException/InvalidSessionRowExceptionの七source、SDKは既qualifiedServlet6.1/Spring7標準libの明示hashだけ、旧全Web/APIjarを読取・hash・抽出・定義しない。原13＋新2全15、一source/runのfreshRootNullAway/静的全site/物理CRC-init/XML/default及び無filterConverter必須四整数100、依存七全体の未達を隠さない。

BUG3063/3064、YKT2546/2556、状態:設計確定・main反映前、PG/PT/正式未完。
