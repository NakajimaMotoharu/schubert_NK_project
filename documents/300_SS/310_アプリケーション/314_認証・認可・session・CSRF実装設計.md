# 認証・認可・session・CSRF実装設計

## 1. 目的・追跡

Login、Logout、password、失敗lock、HTTP/API session、認証context、CSRF、USER/ADMIN認可、owner検証と暗号key rotationを定める。

- 関連UI: 211～212、221～226、232、234、241～242、251～253
- 関連RD: FUN-001、FUN-009、AUT-001～004、MQ-004、MQ-021、MQ-030、MQ-036、MON-004、OPS-005
- 関連QA/RDF/UIC: QA-002、006、017～021、023、030、040、044、RDFなし、UIC-004

## 2. 認証component

```text
Browser
 -> Spring Security filter chain + CSRF
 -> MqAuthenticationProvider
 -> IF-001
 -> API AuthenticationService
      -> app_users / login_ip_attempts / auth_sessions
 <- context raw（Login responseだけ）
 -> EncryptedWebSessionRepository
      -> schubert_web_session.web_http_sessions
 -> Cookie（random opaque session IDだけ）
```

Webはpassword照合、account正本、最新role決定を行わない。APIは利用者起点の全requestでcontext hash、expiry、revoke、account status、
roleを検証する。Header/HTML/cookieへ認証contextを出さない。

## 3. Spring Security filter chain

初期構成は単一`SecurityFilterChain`とし、順序を固定する。

1. Forwarded headerはCaddyからのloopback接続だけを採用し、外部値を上書き済みとする。
2. Request ID/filter、security header、session repositoryを適用する。
3. CSRF tokenを全POSTへ検証する。Login POSTも例外にしない。
4. `/login`、static CSS/JS、`/error`だけpermitAll。Actuatorは別loopback port＋OS/network制限。
5. `/admin/**`と`/logs`は`ROLE_ADMIN`、その他保護URLはauthenticated。
6. Form loginは`MqAuthenticationProvider`、success/failure handler、safe SavedRequestを使用する。
7. LogoutはPOST `/logout`だけ。API revoke coordination後にcookie削除・session invalidateを行う。
8. 401/403はHTML/media/POSTごとのhandlerでUI 221の遷移へ変換する。

`ROLE_` prefixはWeb framework内部だけとし、wire/DBのroleは`USER`/`ADMIN`を正とする。

## 4. Password

### 4.1 保存・照合

- `DelegatingPasswordEncoder`形式を必須とし、初期encoding IDは世代固定の`pbkdf2-v1`とする。
- `pbkdf2-v1`はSpring Securityの`Pbkdf2PasswordEncoder.defaultsForSpringSecurity_v5_8()`相当、すなわち
  PBKDF2-HMAC-SHA256、salt 16 byte、310,000 iteration、derived key 256 bit、additional secret空、
  `setEncodeHashAsBase64(false)`で固定する。
- Hash文字列は`{pbkdf2-v1}` prefix付きで保存する。salt＋derived keyのhex出力96文字とprefixを含めても
  `password_hash`の255 byte以内である。平文、可逆暗号、単純hash、独自pre-hashを保存しない。
- Java 25/本番CPUでLogin照合p95を計測し、目標0.5～1.0秒から外れる場合はsecurity reviewを行う。Parameterを変える場合は
  同一IDの意味を変えず`pbkdf2-v2`等の新IDを追加し、旧IDも照合mapへ保持する。
- 将来encoding IDを変更した場合、Login成功時に`upgradeEncoding`で新hashへtransactional rehashする。
- Password入力はNFC後12～128文字、256 byte以下、usernameとcase-insensitive同一禁止、末尾ASCII space/control文字禁止。
- 文字種組合せは強制しない。初期releaseでは外部由来common-password listを採用しない。長さ、rate limit、hashを正とし、
  listの出典・更新・誤検知を未管理のまま利用者挙動へ追加しない。

### 4.2 Memory/log

Web/API境界では固定長上の制約により一時`String`が生じるが、mapper以降は`char[]`を使用し、照合後zero fillする。PasswordをDTO
`toString`、MDC、exception、inbox response、DLQ property、metricへ出さない。Login/Password resetのDLQ本文閲覧権限を特に制限する。

## 5. Login失敗・lock

SSC-013: 同Message ID再送は324 §6.1の匿名Inbox保存結果を返し、以下のpassword照合/counter/発行を再実行しない。成功は初回応答snapshotとAUTH_SESSION参照の整合検査後0200、失敗は初回result/retryを維持。Replayはactive認証・権限付与・idle延長ではない。

### 5.1 API transaction

| Step | 処理 |
|---:|---|
| 1 | Client addressを`inet`へparse。Caddy検証済み以外はrequest拒否 |
| 2 | username_key一致userがあれば先に`FOR UPDATE`、次に`login_ip_attempts`をUPSERT後`FOR UPDATE`。全LoginでUser→IPのlock順を統一 |
| 3 | IP/userの`locked_until > now`を確認。Lockならhash照合せず`0106` |
| 4 | Account ACTIVEならconstant-work password照合。不存在/disabledも利用者messageは共通 |
| 5a | 成功: user/IP counter/window/lockをclear、last_login更新、session発行 |
| 5b | 失敗: 15分窓外ならcount=1へreset、窓内ならincrement。User 5/IP 10到達で15分lock |
| 6 | SECURITY auditを同transactionで保存してcommit |

User不存在でもIP制御と同程度の処理経路を取り、timing/responseで存在を開示しない。DB/MQ timeoutは`9000`であり失敗counterを増やさない。

#### 5.1.1 失敗窓とlockの境界（SSC-009）

現行互換を維持し、USER/IPとも`now > window_started_at + 15分`のstrict超過で窓外resetする。終了時刻の一致は旧窓へ加算する。窓の開始が未設定なら初回count=1とする。これは`locked_until > now`のlock有効性とは別条件であり、lock終了一致では照合を許可する。その照合が失敗して旧窓の閾値へ到達した場合は新たな15分lockを設定する。失敗回数が閾値へ到達した当該要求から`0106`を返し、次の要求までlock表示を遅らせない。

根拠はUI226/234の15分窓・閾値と未承認差分禁止、現行`LoginAttemptService.isExpired/recordFailure`および`LoginAuthenticationFailureHandler`。BUG-021/YKT-018の固定Clock比較で終了±1ns/一致を検証する。DB精度では±1μs/一致を検証し、Current baselineとDIF allowlistは変更しない。

### 5.2 Retry-After

APIは`retry_after_seconds = ceil(locked_until-now)`を0～900で返す。WebはHTTP `Retry-After`を設定し待機messageを表示する。
Remaining attemptsは存在推測を避け通常認証失敗では0とし、運用logだけ内部counterを保持する。

## 6. API認証context

### 6.1 発行・保存

| 項目 | 設計 |
|---|---|
| Raw | CSPRNG 32 byte、lowercase hex 64文字 |
| Lookup | `SHA-256(raw ASCII bytes)` lowercase hexを`context_hash`へ保存 |
| Replay | RawをAPI context encryption keyでAES-256-GCM暗号化して`context_ciphertext`へ保存 |
| Nonce | MessageごとにCSPRNG 12 byte。Ciphertext envelopeへkey version、nonce、tagを格納 |
| AAD | `SCHUBERT-NK-AUTHCTX-v1`＋auth session UUID＋user ID |
| Lifetime | 8時間idle。`last_accessed_at`更新時に`expires_at=now+8時間`へ延長 |
| Concurrent | Userごと有効最大2。3件目は`last_accessed_at,id`最古をrevoke |

UIで確定したidle 8時間だけを適用する。未承認の絶対lifetimeを追加しない。

QA-044/UIC-004で確定したとおり、現行は設定と異なり3 sessionがすべて継続するが、これは既知不具合`DIF-016`である。NKではこの挙動を再現せず、Login成功transaction内で同一userの有効sessionをlockし、上記の最大2件・最古revokeを強制する。

### 6.2 Request検証

`AuthenticationContextVerifier.verify(String raw, Instant now)`は次を単一read/write transactionで実行する。

1. 64 lowercase hexを検査し、constant-timeでhash keyを検索する。
2. `revoked=false`、`expires_at>now`、account ACTIVEを検査する。
3. DBの最新role/usernameを`AuthenticatedActor`へ設定し、wire/HTTP roleを信用しない。
4. 認証済みrequestごとに`last_accessed_at=:now`、`expires_at=:now+8h`を更新し、idle 8時間を短縮しない。
5. 機能role/ownerはApplication Serviceでも対象rowと照合する。

失効・期限切れは`0102`、DB障害はdeny closedで`9000`。Raw/hash/ciphertextをlogしない。

### 6.3 Logout・管理失効（SSC-011）

LOGREQ01だけは312 §4.2の失効専用lookupとし、通常のactive verifierによる先行拒否をしない。User→session lock、既失効なら元のrevoked_at/0200、未失効の有効contextだけLOGOUT/0000。idleを延長せず、既失効への再要求は時刻/reasonを上書きしない。管理の全失効はADMIN認可済みのcaller transaction内でtarget Userをlock後、未失効sessionを全件対象とし、DISABLED/PASSWORD_RESET/ADMINの閉じたreasonを保存する。更新数0でも既失効rowの時刻は維持する。更新と監査の途中失敗はcallerが全rollbackする。

## 7. HTTP session

### 7.1 Cookie/session ID

- Cookie名は`SCHUBERT_NK_SESSION`。Secure、HttpOnly、SameSite=Lax、Path=/、Domain未指定とする。
- Raw session IDはCSPRNG 32 byteのbase64url paddingなし。DBはSHA-256 hashだけをlookup keyとする。
- Cookie max-ageはsession cookieとし、server-side idle 8時間を正とする。
- Login成功時にraw session IDを必ず再採番し、旧rowを同一transactionで無効化する。

### 7.2 `EncryptedWebSessionRepository`

Spring Sessionの汎用Java serializationは使用せず、version付きJSON allowlistをAES-256-GCMで暗号化する。

| Attribute | 型/上限 | 用途 |
|---|---|---|
| username | String 64 byte | Top bar表示 |
| role | enum USER/ADMIN | Web側早期gate。APIが毎回再検証 |
| authenticationContext | String 64 hex | Wire header設定。Cookie/HTML非表示 |
| loginAt | Instant | 監査/表示外 |
| csrfToken | String 64～128 | Synchronizer token |
| savedRequest | path/query合計2,048 byte | Same-origin safe GETだけ |
| operationTokens | 最大10件の用途、UUID、発行時刻 | 更新timeout/PRG |

Password、質問/回答本文、検索結果、固定長body、DB rowをsessionへ保存しない。Envelopeは`formatVersion`、`keyVersion`、12 byte nonce、
ciphertext/tagを保持し、AADはsession ID hash＋created_at。復号後の未知field/type/上限超過はdeny closedでsession失効。

### 7.3 Lifecycle

| Event | Web session | API session |
|---|---|---|
| Login success | 新規row、CSRF再発行 | 新規auth session |
| Idle expiry | Row削除/無効 | 次回API検証で期限切れ |
| Logout success | 即時削除 | revoke |
| Logout API障害 | 即時削除、pending revoke暗号row | recovery taskでrevoke |
| Password reset/status/role変更 | 次回requestで0102、local session破棄 | 全session即時revoke |
| Web再起動 | DB row復号後継続 | 有効なら継続 |
| Key復号失敗 | 失効・Loginへ | API sessionは期限まで残るがWebから利用不可 |

## 8. CSRF・operation token

### 8.1 CSRF

- Spring Securityのsynchronizer token方式を使用し、tokenは暗号化server-side sessionへ保存する。
- 全POST（Login、Logout、User更新、質問、取消、削除）でhidden `_csrf`とsession tokenをconstant-time比較する。
- Login成功/session fixation、Logout、権限変更後の再Loginでtokenを再発行する。
- GET、MQ request、media Rangeは状態更新に使わない。CSRF失敗はAPIへ送信せず403 SECURITY log。

### 8.2 Operation tokenとの差

CSRFはBrowser origin/sessionを検証し、operation tokenは同一論理更新の再操作を識別する。両方を必須とし代替しない。
Operation tokenはCSPRNG UUID、用途別に発行し、成功確定/新規formでrotate、timeout時だけ同一値を再利用する。Tokenとpayload/Passwordを
Web sessionで関連付けて保存せず、APIのHMAC fingerprintを正とする。

## 9. 認可・owner検証

### 9.1 Layer

| Layer | 検査 | 目的 |
|---|---|---|
| Web URL | Security matcher/`@PreAuthorize` | Menu/direct URLの早期拒否 |
| API common | Context有効性、最新role、producer/layout | 偽造wire roleを拒否 |
| Application Service | 操作role、owner、状態、自己保護 | DB対象ごとの最終判断 |
| Repository SQL | `owner_user_id=:actor` predicate、ADMIN用別SQL | IDOR・条件漏れ防止 |

### 9.2 Matrix

| 操作 | USER | ADMIN | API条件 |
|---|:---:|:---:|---|
| Scenario/audio/video/music | ○ | ○ | 有効context |
| 本人質問送信/通知閲覧/取消 | ○ | ○ | notification owner=actor。ADMIN拡張なし |
| 質問回答検索/閲覧/削除 | 本人 | 全利用者 | USER SQLはowner必須、ADMIN handlerだけ全scope |
| Log | × | ○ | role=ADMIN |
| User管理 | × | ○ | role=ADMIN＋自己/active ADMIN保護 |

他人IDはUSERへ404を返し、存在を開示しない。ADMIN URLをUSERが要求した場合は対象に関係なく403。Web表示非表示だけで許可しない。

## 10. Logout失効再試行

`pending_context_revocations`にはcontext rawをWeb session keyとは別のrevoke queue keyでAES-GCM暗号化し、key version、requested/
next attempt/expiry、error codeだけを保存する。Backoffは5秒、30秒、5分、その後15分上限でAPI session expiryまで継続する。
成功または保存済みAPI session expiry経過確認後にrowを削除する。Table/outbox/logへraw/hashを出さない。

## 11. Key・credential rotation

| Key | Scope | Credential名 | Rotation |
|---|---|---|---|
| API context AES | APIだけ | `api-context-aes-vNN` | Current＋previousを読取、currentだけwrite |
| Web session AES | Webだけ | `web-session-aes-vNN` | 同上。読取成功時にcurrentへ再暗号化可 |
| Web revoke AES | Webだけ | `web-revoke-aes-vNN` | Session keyと分離 |
| Operation HMAC | APIだけ | `operation-hmac-vNN` | Inboxにkey version。保持期間中previousを保持 |

各keyは256 bit、systemd credential 0600/root-managed、Git/DB/env command line禁止。Key IDは非秘密だがkey内容・credential path詳細を
利用者errorへ出さない。Previous key削除前に対象ciphertext/inboxの最長保持期間を満たす。

## 12. Security log

| Event | 必須field | 禁止field |
|---|---|---|
| Login success/failure/lock | request ID、username入力のbounded識別、remote、reason code、result | Password、hash、context |
| Session issue/revoke/expiry | actor/対象user、message/correlation、reason、時刻 | session ID/internal UUID/raw/hash/ciphertext |
| CSRF/authorization deny | actor optional、method/path、request ID、rule ID | CSRF token、query値 |
| User status/role/password | actor/target、before/after（password除外）、token fingerprint ID | Password/hash/token raw |

Username不存在は内部reason codeを権限制限logへ記録できるが、利用者messageとmetric labelでは区別しない。

SSC-010: Session識別子の機密除外は351 §4を正とする。Login発行はLOGIN_SUCCEEDED、最大2件制御の各REPLACEDはSESSION_REVOKEDを同じtransactionで保存する。Logout/管理全失効もSESSION_REVOKEDと閉じたreason、結果codeで記録し、失効日時はDB列に保持する。新規失効1行につき監査1行、冪等Logout要求は0200監査1行（Inbox再送は元結果のみで重複監査しない）。監査失敗時にsessionだけcommitすることは禁止する。

## 13. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-010 | Password hashは`{pbkdf2-v1}`（PBKDF2-HMAC-SHA256、salt 16 byte、310,000 iteration、256 bit）を初期値とする | UI 225/226の最大256 byteを全長で処理し、Java標準JCAとDelegating形式で世代管理できる | PGでbenchmark、PTで256 byte全長差・hash/rehash/redaction |
| SS-D-011 | 初期releaseではcommon-password listを採用しない | UI 225がSS判断。出典/version未管理の拒否挙動を追加せず、12文字・rate limit・hashを適用 | 将来採用はlist/version/差異を変更管理 |
| SS-D-012 | Custom encrypted Spring Session repositoryを使用する | UI 226が任意Java serialization禁止・allowlist/AES-GCMを要求 | Session repository/crypto PTが必須 |

## 14. 実装・試験禁止事項

- Password照合、role決定、owner最終判断をWebだけで完結させること。
- HTTP sessionのJava native serialization、cookieへの認証context/role本体格納。
- CSRF除外によるLogin/Logout/更新POSTの通過。
- Raw context、hash、ciphertext、password、tokenをlog/metric/DLQ propertyへ出力。
- USER用検索で取得後にJavaで他人行をfilterすること。SQL predicateでscopeを限定する。
- Active ADMIN 0人化を画面button非表示だけで防止すること。

## 15. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | 認証、session、CSRF、認可、暗号・rotationを初版作成。 |
| 2026-08-31 | 横断監査でLogin lock順をUser→IPに統一し、UIにない絶対24時間上限を削除。Idle更新を毎requestに統一。 |
| 2026-09-01 | QA-044/UIC-004を反映。現行の3 session継続を`DIF-016`とし、NKはtransactionで最大2 session・最古revokeを必須とするoracleを固定。 |
