# Security・credential・監査実装設計

## 1. 目的・追跡

Browser/Caddy/Web/Artemis/API/PostgreSQL/file/systemdの信頼境界ごとに、認証・認可、CSRF/session、
入出力検証、credential/暗号key、固定長電文、SQL、path、監査log、dependencyの実装規約を定める。

- 上位設計: UI 222、225～226、231～237、241～243、253
- 関連RD: AUT-001～AUT-004、SYS-012～SYS-014、MON-003～MON-004、OPS-005、
  MQ-003～MQ-010、MSG-001～MSG-011、FIL-003～FIL-007
- 関連SS: [314_認証・認可・session・CSRF実装設計](../310_アプリケーション/314_認証・認可・session・CSRF実装設計.md)、
  [322_固定長電文codec実装設計](../320_メッセージング/322_固定長電文codec実装設計.md)、
  [333_大容量結果file・media・Range配信設計](../330_データ・ファイル/333_大容量結果file・media・Range配信設計.md)
- 関連QA/RDF/UIC: QA-006～QA-007、QA-017～QA-023、QA-030、QA-040、QA-043、RDFなし、UIC-003

## 2. Trust boundary・deny default

```text
Untrusted Browser
  -- HTTPS:55160 --> Caddy（TLS、forwarded header再構成）
  -- loopback HTTP --> Web（CSRF、HTTP session、form/view）
  -- loopback JMS + fixed bytes --> Artemis（service別ACL、durable）
  -- consumer --> API（context再検証、role/owner、business/DB transaction）
  -- loopback JDBC --> PostgreSQL（role/schema/constraint）
  -- logical descriptor --> local asset/transfer（secure relative open）
```

各境界は前段の検証済みflag/role/pathを信用して後段の検証を省略しない。未知URL/method/layout/role/state/
MIME/path/config keyはdeny。DB/MQ/key障害時は権限を緩和せずdeny closed。

## 3. Spring Security chain

### 3.1 HTTP filter順

1. Caddy loopback/source header検証・request ID発行。
2. Security header/cache filter。
3. Encrypted session repository読取、cookie hash lookup、AES-GCM/allowlist/type/version/expiry検証。
4. CSRF token repository。GET/HEADは検証なし、Loginを含む全POSTは必須。
5. Authentication principal形成。Raw API contextはprincipalの秘密field、`toString`をredact。
6. Route role/HTTP method認可、form binding/validation。
7. Controller→JMS。APIがcontext hash/expiry/account/role/ownerを毎回再検証。
8. Response header、REQUEST event、session save。

Public allowlistは`GET /login`、`POST /login`、version非表示のerror asset、loopback management healthだけ。
Static CSS/JS/fontもextensionではなく正規resource path allowlist。他はauthenticated、ADMIN routeはrole ADMIN。

### 3.2 Cookie・session

- Cookie nameは`SCHUBERT_NK_SESSION`、128 bit以上CSPRNG opaque ID、BrowserにはIDだけ。`Secure; HttpOnly; SameSite=Lax; Path=/`。
- DBは`SHA-256(cookie ID)`でlookup、raw IDを保存/logしない。Login成功時に新ID/CSRF・新row、旧rowを同一transactionで失効。
- Attributeはusername、role、raw API context、login/last access、CSRF、safe GET SavedRequest、用途/時刻付きoperation token最大10件。
- Java serialization、request/form/body/password、任意class名を保存しない。Deserializeはversion付きの固定JSON/CBOR schemaへbound。
- Idle 8時間、同一account 2 session。Web/APIのどちらか一方が無効・復号不能なら両方を無効扱いしLoginへ。

SSC-047/BUG-074: 314 §3.2の内部ERROR+/error専用非業務branchは表示だけで、外部REQUEST/ASYNC/FORWARDや別pathの認証除外に使用しない。Caddy/header/server UUIDは共通必須、通常要求の単一business FilterChainProxy/StrictHttpFirewallは維持する。元method/headerのfirewall拒否を内部errorへ反復せず、DB/JMS/sessionを再読しない。表示snapshotは要求内のみの閉TopBar＋解決済CSRF、失効時clear、秘密値のDOM data属性/診断出力禁止を維持する。通常POST/login/logout/管理/媒体の認証・CSRF・API最新role/owner検証を緩和しない。

## 4. Authentication・Password

| 項目 | 実装規約 |
|---|---|
| Username | NFC→前後trim→Unicode lowercase比較key、displayはNFC、1～64 UTF-8 byte |
| Password input | 自動trimは行わず、入力値をNFC化後に検査。Loginは1～256 UTF-8 byte、作成/resetは12～128文字かつ256 byte以下。NUL/control文字と末尾ASCII spaceを禁止 |
| Hash | Spring `DelegatingPasswordEncoder`の`{pbkdf2-v1}`。PBKDF2-HMAC-SHA256、salt 16 byte、310,000 iteration、derived key 256 bit、hex出力。平文/可逆暗号/独自pre-hash保存なし |
| Timing | User不存在でも現行IDと同一parameterの固定dummy PBKDF2 hashを照合し、外部message/statusは同一 |
| Memory | HTTP Stringへ長期保持せず`char[]`/限定buffer、照合/HMAC後zero fill、log/debugger出力なし |
| Rehash | Login成功時にencoder IDが旧世代なら同一transactionで再hash。Parameter変更は新IDとして登録し、監査にはalgorithm IDだけ |
| Lock | User 5回/IP 10回、15分窓・15分lock、DB row lock、API再起動でclearしない |

Password resetは新password hash更新と対象auth session全revokeを同一transaction。
Admin画面へhash/algorithm/cost/過去passwordを表示しない。

## 5. API認証context・認可

- Context rawは32 byte CSPRNGをlowercase hex 64文字。DB lookupはSHA-256 hash、Login replay用だけAES-GCM ciphertext。
- 全利用者起点requestのheaderにraw contextを設定。APIはhash、revoked/expiry、account ACTIVE、DBの現在roleを毎回取得。
- Wire role/username、Webのbutton非表示、URLの難読性を認可根拠にしない。
- USERのQuestionはowner predicate、ADMINのQuestionはrole再検証。Notification取消はADMINでも本人だけ。非scopeは不存在と同じ`0104`。
- User管理/LogはADMINだけ。自己無効化/自己role解除/active ADMIN 0化をDB transactionで拒否。

ControllerのannotationとApplication Serviceの`AuthorizationPolicy`の二層、Repositoryの`ActorScope`でownerを三重保護。
Domain serviceにactorのない公開methodを作らない。

## 6. CSRF・operation token・replay

| Control | Scope | 失敗 |
|---|---|---|
| CSRF synchronizer token | Loginを含む全POST | MQ送信前403、利用者値をlogしない |
| SameSite=Lax | Session cookie | CSRFの補助、代替にしない |
| Operation token | User更新/質問/取消/論理削除 | Owner/token/HMAC一致は0200、異なれば0105 |
| Message ID/inbox | 全MQ request | 同ID異payloadは恒久整合error、保存結果なし |

CSRFとoperation tokenは目的が異なるため両方必須。Token/HMAC canonicalは324を正とする。
Password/質問本文をHMACに含める場合も、平文/canonical/単純hashをDB/logへ保存しない。

## 7. Browser output・security header

### 7.1 Output encoding

- Thymeleaf等templateのescaped text attributeを使い、unescaped HTML出力、HTML文字列の連結、利用者入力のJS/CSS context埋込みを禁止。
- URLはroute builderと許可済みlogical IDだけ。`javascript:`、scheme-relative、external redirectを拒否。
- Errorはcatalog message、request ID、再操作案内だけ。Exception、SQL、stack、path、layout body、secretを表示しない。

### 7.2 Header

| Header | Value/policy |
|---|---|
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'; connect-src 'self'` |
| `Strict-Transport-Security` | `max-age=31536000`。Initial certificate警告があってもHTTPS維持 |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY`、CSP frame-ancestorsと二重化 |
| `Referrer-Policy` | `same-origin`。Caddy/Webで同値とし、実応答をPGで照合 |
| `Permissions-Policy` | camera/microphone/geolocation/payment等を空allowlist |
| `Cache-Control` | 認証済HTML/error/media descriptorは`no-store`、static hash assetだけversioned cache可 |

CaddyとWebの二重headerが相反しないよう、ITで実応答値を1件ずつ照合。
Inline script/style/event handlerは使わず、same-origin外部JS/CSSへ分離。

## 8. Input validation pipeline

```text
HTTP content-type/size/method
 -> form bind allowlist（unknown field拒否）
 -> Unicode/control/NFC/trim policy
 -> character count + UTF-8 byte count
 -> enum/numeric/date/cross-field validation
 -> fixed-width encoder
 -> API fixed-width decoder（byteから再検証）
 -> domain validation/authorization
 -> prepared SQL / secure file resolver
```

- Request bodyは2MB、fixed bodyは1,000,000 byte、layout/record個別上限。Multipart/upload endpointは作らない。
- Content-Typeはform URL encodedまたは設計済みGETのみ。JSON/XML/object serialization endpointをBrowser向けに追加しない。
- Unknown form parameter、配列型の複数値pollution、未定義enum、制御文字、末尾ASCII spaceはfield error。
- 数値はASCII digitだけ、先頭+/minus/小数/指数なし。日時はstrict parser、JST wire→`Instant`の一義変換。
- Validation messageへraw入力を反射しない。

## 9. Fixed protocol・JMS security

- `BytesMessage`以外、body 1,000,000 byte超過、property/header/layout/version/length/UTF-8/padding不整合は業務handler前に拒否。
- 恒久protocol errorはbodyを画面/logへ出さず、DLQ send＋元ACKをJMS commit後、process非0終了。
- Artemisはloopback、service別user、Address send/consume/browse/manage最小権限、auto-create/delete false。
- JMS ObjectMessage/Java serialization、dynamic destination、任意`JMSReplyTo`、利用者指定Addressを禁止。
- DLQはpasswordを含むLogin bodyの可能性があるため運用アクセスを特に制限、body dumpなし、自動再投入/削除なし。

## 10. DB・SQL・file

- DB roleは331、Webはtechnical schemaだけ、application superuser/DDLなし。Loopback SCRAM、prepared/named parameter。
  QA-043/UIC-003承認に基づきdump全SELECTを`schubert_backup`へ分離し、`schubert_batch`へ業務/technical table SELECTを与えない。
- Dynamic table/column/orderはenum allowlistから固定fragment。任意入力のschema/table/SQL挿入、native query logを禁止。
- Owner predicateはSQL内、論理削除predicateはRepository共通・負test必須。Constraint名→domain errorはallowlist。
- Fileはlogical ID→API descriptor→Web secure open。`SecureDirectoryStream`/NOFOLLOW、root配下通常file、size/hash/MIME、権限を毎回検証。
- Caddy static file、physical/storage path開示、任意file name/header反射、file全memory読込を禁止。

## 11. Credential・暗号形式

### 11.1 配布・使用

- Secretは`/etc/schubert-nk/credentials`のroot:service 0600をsystemd `LoadCredential`でprivate runtimeへ渡す。
- Secret fileは1 credential/1 file、末尾改行を除いたbinaryまたはUTF-8、size上限64KiB、symlink/hard-link/不正owner/mode拒否。
- Applicationは起動時に必須ID/key length/versionを検証。不足はreadiness false。SecretをSpring environment/Actuator/JMX/thread name/argvへ登録しない。

### 11.2 AES-256-GCM envelope `NKENC1`

```text
magic 6 bytes "NKENC1"
format version 1 byte = 1
key-id length 1 byte + ASCII key-id 1..16
nonce 12 random bytes
ciphertext N bytes
authentication tag 16 bytes
```

- Key 32 random byte、暗号化ごとのnonce 12 byte CSPRNG、同keyでnonce再利用禁止。
- AADはpurpose/table、logical primary key/message ID、format versionをlength-prefixed canonical化。Row間ciphertext移植を拒否。
- Decryptはformat/key ID/AAD/tag/maximum plaintextの順で検証。Tag不一致は平文を返さずdeny closed/SECURITY alert。
- Current keyでwrite、current/previousでread。Unknown versionを自動推測しない。Rotationは343に従う。

Operation fingerprintのHMACは324 `NKOP1`を正とし、AES keyとHMAC key、Web session/API inbox/Web logのkeyを共用しない。

### 11.3 Inbox保守検査のcredential境界（SSC-049/QA-046）

UIC-006で承認された非公開検査processだけに、必要なAPI Inbox response/contextのcurrent/previous keyを限定配布する。batch/backup/Webへは配布しない。専用OS identity、外部credential、読取り専用mount/限定DB roleを用い、argv/環境平文/ログ/Gitへ鍵を出さない。unknown key/復号不能/参照不整合は削除許可へ補完しない。保存応答の構造検査はbooleanのみ返し、平文bufferとDATA/record copyを全経路で消去する。DB参照検証・停止/lock条件を別途必須とし、構造検査だけで削除を承認しない。

## 12. Audit・redaction

| Event | DB audit | 必須field | 除外 |
|---|:---:|---|---|
| Login success/failure/lock/logout/revoke | yes | request、actor/display username、IP、result/reason code | password/context/cookie/CSRF |
| Role/owner deny | yes | actor/role、operation、target type、result | 非scopeの機密内容 |
| User create/status/role/reset/unlock | yes | actor/target、before/after、operation result | password/hash/token |
| Question submit/cancel/delete/state | yes | actor、receipt/job/question ID、before/after | question/answer body |
| DLQ/replay/protocol error | yes | IDs、layout、count、error、approval | fixed body/password |
| Backup/restore/cleanup/config drift | yes | run/version/hash/count/result | secret/archive plaintext/path全文 |

Critical DB audit INSERT失敗は対応業務transactionをrollback。Web REQUEST投影はbest effortだがlocal JSON/outboxで復旧する。
351のcanary試験でlog/metric/DLQ/property/DBの機密漏えい0件を確認する。

## 13. Build・dependency・artifact

- Maven Wrapper/Java toolchain/Dependency BOM/plugin versionを固定、dynamic/range/SNAPSHOT dependencyをreleaseで禁止。
- CIでunit、static analysis、known vulnerability、secret、license、artifact hash、SBOMを生成。開発中の検出を無根拠でsuppressしない。
- Release jar/migration/config/systemd/operation documentは同じversion/commit/manifest、SHA-256照合後だけ配備。
- Deserialization gadgetを避け、Java native serialization・ObjectMessage・任意polymorphic JSONを使わない。

## 14. Security PT/IT必須観点

- Login存在/不存在timing、5/10回・15分境界、2/3 session、rehash、reset/disable/role変更revoke。
- Session fixation、cookie改ざん、DB ciphertext/tag/AAD/key version改ざん、期限・復旧、SavedRequest open redirect。
- CSRF欠落/異なるsession/重複、operation token同/異payload、HMAC current/previous/unknown。
- USER→ADMIN URL、他人Question ID、ADMIN notification取消の他人分、自己/active ADMIN保護、Web DB grant。
- XSS payload、CRLF/header、SQL wildcard/injection、unknown field/enum、Unicode正規化・byte境界、fixed padding/UTF-8。
- Path traversal、all symlink segment、hard link、TOCTOU、MIME/file name、Range overflow、Caddy direct file不可。
- MQ user別send/consume/manageの負test、dynamic Queue/ObjectMessage、DLQ body非出力、protocol exit/restart。
- Secret permission/symlink/argv/env/log/Actuator漏えい、key rotation/tag改ざん、backup encrypted archive復号権限。
- `db-backup`をbackup unit以外から取得できないこと、`schubert_backup`のDML/SET ROLE/AES key取得拒否、`schubert_batch`のdump/任意SELECT拒否。

## 15. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-045 | Session/ciphertext共通envelopeを`NKENC1`、AES-256-GCM、12-byte nonce、16-byte tag、purpose/ID AADに固定 | UI 226/241の外部key暗号を改ざん・row移植防御まで具体化 | Crypto golden vector/key rotation PT |
| SS-D-046 | Browser向けはform/HTMLのみ、JSON/XML/upload/Java serialization endpointを作らない | 初期外部仕様に不要な攻撃面を増やさない | Controller mapping/security scan |
| SS-D-047 | CSPでinline script/style/event handlerを許容せず、same-origin static assetに分離 | UI 222のCSPとCHR-S02/DIF-013を実装で強制 | Template PT/browser IT/CHR |

## 16. 禁止事項

- Security障害時のfail open、ADMIN固定backdoor/default password、role/owner検証のWebだけへの集約。
- Password/context/cookie/token/key/bodyの平文永続化、単純hash、再利用nonce、自動key推測。
- CSPの`unsafe-inline`/`unsafe-eval`、任意external origin、unescaped HTML、任意redirect。
- Webの業務schema参照、SQL文字列連結、path normalizeだけの認可、Caddy直接asset配信。
- Security testのためにproductionのredaction/authorization/validationをprofile分岐で無効化すること。

## 17. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Trust boundary、Spring Security、crypto/credential、入出力、MQ/DB/file、監査を詳細化。 |
| 2026-08-31 | 横断監査でPasswordの取扱いをUI 222/225/234/236に合わせ、非trim・NFC後の文字/byte・末尾space検査へ統一。 |
| 2026-08-31 | Password hashを最大256 byte全長に対応する`{pbkdf2-v1}`へ是正し、世代IDとparameterを固定。 |
| 2026-08-31 | Dump用DB role/credential分離案と権限負testをQA-043/UIC-003回答待ちで追加。 |
| 2026-09-01 | QA-043/UIC-003承認を反映し、dump専用role/credentialとbatch roleの相互権限拒否を確定。 |
