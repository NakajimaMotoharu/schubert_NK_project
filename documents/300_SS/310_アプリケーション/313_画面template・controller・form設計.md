# 画面template・controller・form設計

## 1. 目的・追跡

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
| 007 | GET `/scenarios/{id}` | `scenario.html` | `ScenarioController.detail(long,String anchor,Model)` | `ScenarioDetailViewModel` | IF-008 | USER/ADMIN |
| 008 | GET `/animation` | `animation.html` | `AnimationController.menu(Model)` | `AnimationMenuViewModel` | IF-010 | USER/ADMIN、FUN-006 |
| 009 | GET `/animation/main`,`/animation/ova` | `animation-list.html` | `AnimationController.list(AnimationCategory,Model)` | `AnimationListViewModel` | IF-011 | USER/ADMIN |
| 010 | GET `/animation/opening`,`/animation/videos/{id}` | `animation-watch.html` | `AnimationController.watch(String,Model)` | `AnimationWatchViewModel` | IF-012 | USER/ADMIN |
| 011 | GET `/music` | `music.html` | `MusicController.categories(Model)` | `MusicCategoryViewModel` | IF-013 | USER/ADMIN、FUN-007 |
| 012 | GET `/music/{category}` | `music-sections.html` | `MusicController.sections(String,Model)` | `MusicSectionViewModel` | IF-014 | USER/ADMIN |
| 013 | GET `/music/{category}/{section}` | `music-list.html` | `MusicController.tracks(String,String,Model)` | `MusicTrackViewModel` | IF-015 | USER/ADMIN |
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
| 019 | GET `/questions/accepted/{receiptId}` | `questions/accepted.html` | `QuestionController.accepted(ReceiptId,Model)` | `QuestionAcceptedViewModel` | 保存済みIF-025結果 | Owner、QST-002 |
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
