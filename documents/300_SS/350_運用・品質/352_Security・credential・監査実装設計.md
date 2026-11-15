# Security・credential・監査実装設計

SSC157（2026-10-02）：未実装QSS/QSD新writer限定の取得scope frame `NKQRY1` を追加する。暗号平文offset0～6はhex `4e4b5152593100`、offset7はUSER=`55`/ADMIN=`41`、offset8以降は従来fixed response wireをそのまま置く。成功と確定error双方、scopeは取得時roleで固定する。外部fixed wire/error filler/NONE、NKENC1暗号外側・AAD message/layout/version/owner、鍵/圧縮/保持期限は変更しない。既存認証・Scenario/Media/User/Log・更新NKREF1とNTS/NTDの平文profileは完全不変。保守は新frameをQSSRSP01/QSDRSP01/version001にだけ許容し、scope字節/短縮/別layout/固定wire/相関/保存codeを独立検査、既存rawの保守検査も維持する。通常replayは無scopeを拒否し、scope=ADMINからUSERへの降格では元保存を変更せずQSS0103/QSD0104を非保存で返す。User→Adminは元の狭いsnapshotのみ返す。平文frame/wireの一時owned bufferはfinally zero-fill、scopeや本文をraw logへ出さない。SS324§6/12.8・SSC157/013001/014001、内部frame golden・独立JCE・旧profile非回帰で検証する。

SSC056/PG160（先行8002b28b・3cf06b00、BUG167/YKT128）: session期限・revoke・認証retry・監査・Inbox/OutboxのDB時刻を332のJDBC4.2 UTC境界へ統一する。歴史暦ずれで期限/参照一致/署名に使うInstantを変えない。NULL/不正/範囲外は既存error契約を維持し、日時補完・許容年縮小・保存暗号/Current期待値の変更をしない。SQL原本と独立epoch/vectorで両方向を照合し、raw session/token/秘密を診断へ出さない。

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
| `Content-Security-Policy` | `default-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'` |
| `Strict-Transport-Security` | `max-age=31536000`。Initial certificate警告があってもHTTPS維持 |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY`、CSP frame-ancestorsと二重化 |
| `Referrer-Policy` | `same-origin`。Caddy/Webで同値とし、実応答をPGで照合 |
| `Permissions-Policy` | camera/microphone/geolocation/payment等を空allowlist |
| `Cache-Control` | 認証済HTML/error/media descriptorは`no-store`、static hash assetだけversioned cache可 |

CaddyとWebの二重headerが相反しないよう、ITで実応答値を1件ずつ照合。
Inline script/style/event handlerは使わず、same-origin外部JS/CSSへ分離。

SSC-182/BUG-688：上のCSP値・directive順序はSS355のCurrent CHR-A01基準と完全一致させる。script-src/connect-srcはdefault-src selfを継承するので同じ実効制限を維持する。inline/eval/external originを許可せず、比較時のheader正規化・DIF未登録差分の免除・Current基準改変は行わない。独立固定文字列による全応答PTと実NK同source Characterizationで確認する。

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

SSC-073: LogSearchFormのCurrent検索文字列trimとUI222§6の0以下page補正は上記一般規則の限定例外とする。処理順・8field allowlist・DIF010日時のstrict JST/millisecond/31日境界はSS313§5.2追補に従う。trim前のCR/LF/TAB/NUL・不正surrogateは拒否し、未知/複数field・byte超過・enum未知は引き続き拒否する。他の数値やPassword/質問の末尾space禁止を緩和しない。

SSC-072: 上記一般規則よりUI222§5/6・223§3の検索固有規則を優先する。ScenarioSearchFormの検索文字列はcontrol検査後NFC/trimするため前後ASCII spaceをerrorにしない。pageのみ負ASCII整数を1へ補正する（int範囲内）。その他の数値のminus禁止、Password/質問の末尾space禁止は変えない。詳細はSS313§5.2追補。未知・複数parameter、plus、非ASCII数字、overflow、正数上限超過は引き続き拒否する。

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

### 11.2.1 更新対象の暗号認証binding（SSC-052、PG-D-140）

取消/削除成功wireに対象IDが無いため、確定日時だけでresult refを照合してはならない。新たに実装するQSB/NTC/QDLの成功0000/0200 snapshotは、fixed response wireの前に次の内部metadataを連結し、全体を従来のDeflater3→NKENC1/AES-256-GCMへ渡す。外側magic/version1/AAD/nonce/tag/key配布は変更せず、新たなHMAC keyも配布しない。HTTP/JMS電文へこの内部prefixを送信しない。

| 0開始offset | byte長 | 形式 |
|---:|---:|---|
| 0 | 6 | ASCII NKREF1 |
| 6 | 1 | 参照kind: QUESTION=1、JOB=2、他は禁止 |
| 7 | 8 | unsignedではなく正のbig-endian int64、ID1..999999999999 |
| 15 | 16 | operation token UUIDのMSB64/LSB64 big-endian |
| 31 | 4 | 後続wire byte長、big-endian int32 |
| 35 | wire長 | UI236のfixed response wire、header256を含む |

対応はQSBRSP01/QUESTION/320byte、NTCRSP01/JOB/288byte、QDLRSP01/QUESTION/280byte、version001・ownerありだけ。ResultBoundResponseSnapshotCodecは既存ResponseSnapshotCodecを借用し、encodeで内部prefixとwireをcopy、decodeで復号後の全長と期待prefix35byteをMessageDigest.isEqualで比較した後だけwire copyを返す。prefixはcallerのlock済DB ref/tokenから構成し、暗号内の値を正しい参照として逆採用しない。unknown magic/kind/ID/token/length、legacy unbound body、末尾追加/欠落は拒否。

この部品は固定長header/semanticや実DB参照・業務UKの正しさを単独では保証しない。後続のreplay/保守検査は返却wireを既存構造検査相当と実参照検査へ渡し、全検査後にだけ利用/削除する。入力wireはcaller所有、作業prefix/復号包絡はfinally消去、返却wireもcallerが使用後消去。基礎codec/鍵を本wrapperからcloseしない。null/不適切route/長さは境界契約違反、暗号不正は固定ResponseSnapshotException、raw値を例外/log/toStringへ出さない。

既存認証・照会・User更新snapshotの平文profileとNKENC1 goldenは完全不変。確定errorのNONE/fixed-error profileも変更しない。新3成功にunbound旧bodyを見つけてもtargetを推測して再暗号化せず保護し、運用調査へ回す。未実装更新Programの初回保存とreplay/DB照合への結線は別gate。043/PT169～176で独立binary/JCE vector、3route/全metadata変造/同時刻別target・token、旧形式不変、鍵世代/100並行/所有消去/NULLを確認する。

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

## QA-050承認反映：revoke鍵の退役条件（2026-10-03）

期限不明/一般0102/復号不能の失効再試行rowを保持するため、当該rowの復号に必要な旧revoke keyは参照rowとborrowerがともに0と確認できるまで退役しない。100回飽和や推測期限経過を退役proofにしない。正常復号時のcurrent再暗号化は既存NKENC1/AAD契約と短transactionを守り、復号不能時に別contextを生成/送信しない。有限自動鍵退役は保証せず正規復旧・運用確認を行う。Web session/API contextの鍵と混用しない。独立rotation/lease/close/停止順/restore試験まで完了認定しない。

## SSC-418 保護読取の一時context buffer所有・例外消去（2026-11-15）

ProtectedReadWireClientの既6引数package-private構築口と全public facade APIを維持し、defaultはprivate stateless JDK操作実装に固定する。ASCII変換はAuthenticationContext.wireValueからUS_ASCIIの新規64byte、比較は既MessageDigest.isEqualでありalgorithm/認証/権限/電文/画面/再送/期限/queueを変更しない。外部設定・HTTP選択・動的loadingで切替えない。新しい7引数package-private口は内部ContextOperations（encodeとsameの二操作）を受け、operations nullをconstructorの明示nonnull preconditionで拒否する。標準実装は状態/credentialを保持しないprivate static final class、操作interfaceはpackage-privateでbinary Code0を実証し除外としない。

encodeの戻りはnullable boundaryとして宣言し、contextBytesがnull又は64以外を固定IllegalStateExceptionで拒否する。nullは未取得、非null返却時にownedとなる。長さ不正の返却bufferはhelper自身が消去してから失敗し、呼出側へ返した正規bufferだけが次の所有へ移る。第一bufferを取得した直後に外側try/finallyへ入り、その中で第二を取得して内側try/finallyへ入る。第二の取得/検査に失敗すれば取得済み第一だけを消去、比較失敗なら第二→第一をそれぞれ一回消去する。JDK内部の返却前の未到達allocationまでを消去保証したと主張しない。実OOM/Thread操作/JDK差替えで故障を誘発しない。

decodeはinstance内でこの既owned比較を使う。既catalog catchの固定INVALID_RESPONSEは保持し、変換前に既JmsRequestReplyException.preserveFatalでcause/suppressed/SQLnext/JMSlinkedのError identityを保存する。新package-private口の非fatal/不正結果だけが従来の閉分類へ落ち、Errorを通常結果へ変換しない。Root/VM/DB/SDKbackend/actual4/Root2/拒否fixtureへの代替口ではなく、元から許可された同memory-only componentの例外消去を検証する。public synthetic contextだけを用い、実token・session・鍵・原本にアクセスしない。

PTは既58全本文/独立wire/golden/timeout/並行/secret-wipeを保持し、新whole ProtectedReadContextOwnershipTestの6methodを追加する。CONTEXT001 first/second/compareの合成Errorで取得済み全buffer消去とError同一、002比較RTE内Errorの同一伝播、003通常RTEの固定INVALID_RESPONSE/消去/秘匿、004null operationsの構築前拒否、005null encode第一/第二で既取得分消去と固定分類、006不正幅0/63/65を第一/第二で与え返却済み全bufferの消去と後続comparison0。正常/不一致のdefault JDK動作・全8旧クラスは既58で再資格し、必要な同source whole64・全physical数等を推測せず新compile実物から確定する。new6と旧58を区別し、old58成功を新sourceへ流用しない。

原58群の未達carry.2/.6/1.8ppを保持し、新Source製造/SS補足/六PT分だけ.4/1.2/2.4pp追加、当群合計.6/1.8/4.2pp cap6。元群.8/2.4/7.2/cap8・元P005費・元904.85/SV各上限は不変更、carryを二重追加しない。新13Mainは変更sourceなのでRoot compiler/NullAwayでfresh compile、全9wholeTestと静的、同一64execのdefault及びunfiltered全命令/行/メソッド/クラス/分岐、CRC/init/sourceを確認する。各naturalB0/Code0は明示、全Protocol依存を含む全物理scopeの未達を保存しown/source/全194等を混同しない。global451/正式/工数/CHR/native/ITSTを受入にしない。

## SSC-419 Release署名検証の取得直後clone所有（2026-11-15）

ReleaseSignatureVerifier.verifyは既null/長さ検査とpublicDER/元manifest/signatureの同byte clone・既Crypto/JDK Ed25519を維持する。key clone直後に外try、その内でmessage clone直後に中try、signature clone直後に既Crypto try/catch/finallyを置く。finallyはsignature→message→keyの逆取得順で一回ずつ消去、既GeneralSecurityExceptionのfatal graph/Error identityと固定IOExceptionを維持する。返却前のJDK未取得allocationの消去は保証せず、実OOMを起こさない。原public API/constructor/認可/署名format/鍵の固定根/結果/期限/電文は不変更、新operation portやprivate key/実署名/配備を追加0。既9Test全文は保持、新SIGN010だけ合成RuntimeException後に同instanceを正常再利用し、三copy消去/caller不変/pinned再利用/次回独立copy/call数2を固定publicRFC vectorで確認する。同source全10、RootNullAway/静的、sameexec default/raw target全命令行methodclassbranchを照合し、StorageIoException依存の未網羅を隠さずglobal451/正式へ算入0。

BUG3015/YKT2542、状態:設計確定・main反映前、PG/通常PT未完、globalHOLD保持。

## SSC-420 Web暗号化二codecの機密取得保護（2026-11-15）

WebLogPayloadCodec.encryptとRevocationPayloadCodec.encryptで取得済みplaintext/candidateの後にnonce/AAD/emptybuffer初期化がtry前にある取得漏れを是正する。placeholderの非秘密空配列だけをowned機密取得前に準備し、既try内でplaintext copy→nonce→AADを順に取得する。従来finallyで返却済みowned全配列を消去し、返却前のJDK内部allocationは保証せず実OOMを誘発しない。既lock/ensureOpen/null/鍵version/固定AES256GCM128/nonce12/AAD/format/過去鍵/再送結果/例外catalog/既fatal guard/外部APIを保持、新provider/新crypto切替口/権限/実鍵/DB/実nonceを追加0。既Revocation7＋FailureGraph1＋JdbcGraph3＋Fatal5＋WebLog9=25Test本文と独立DataOutput/JCA goldenを保持し、新各1Testだけpublic固定鍵/nonceで初回乱数故障→別worker正常と元caller/nonce消去/既独立golden/call2を検証する。workerはFutureget5s、finallyshutdownNow/await10s確認後codecclose、process隔離内の旧JCA provider復元fixture以外のsystem操作なし。新27は当source一singleexecでfreshMain13 RootNullAway/静的/CRC/init/default及びrawを確認、対象二codecの全Codeと全191等依存scopeの未達を区別し数を実compileから確定する。旧成功/Protocol130は確認再演せず当sourceへ合算しない。

BUG3018/YKT2542、状態:設計確定・main反映前、PG/PT/全451未受入。

## SSC-421 API認証context取得保護と有限単体fixture（2026-11-15）

AuthContextCodec.encryptでplaintext取得後のnonce生成、decryptでnonce取得後のencrypted生成が既try前にある所有保護漏れを是正する。機密取得前に非秘密の空placeholderだけを準備し、実plaintext/nonce又はnonce/encryptedを既try内で順に取得する。取得済みownedだけが既finallyへ必ず届くようにし、JDK内部返却前allocationや実OOMの消去を保証したとしない。既stateLock/close/nonnull/鍵version/前鍵/固定AES256GCM128/nonce12/NKENC1/identityAAD/例外分類/public APIを保持し新crypto/provider/権限/secret口0。全MainはAuthCodec/Identity/Encrypted/CryptoException/package-infoの5sourceと現在Protocol同byteだけ、Actual4/Root2/実DB/実鍵/SDKbackendの代替口を作らない。原whole7の独立DataOutput/JCA expectedと業務assertを維持し、caller-monitorと100nonce並行TestのExecutorService.close/Future.get無期限だけをstop→Futureget5s又は元10s/await10s明示assert→worker確認後codec.closeへ直す。元nonce数100/identity/mutation/null/provider復元契約を弱めない。新AUTHCTX-OWN001はpublic deterministic nonceの初回直接Error同一/nonce消去、別workerで同codec正常と独立envelope一致/元context不変/call2を検証。変更後whole8一singleexec、freshRootNullAway/静的、CRC/init/default及び無filter必須LINE/METHOD/CLASS/BRANCH整数100を対象Codecで確認する。補助Instruction/Complexityも全保存し未実行を隠さず、全物理依存scope/他Main/全例外/全命令のPASSへ拡張0。原7成功は確認再演せず当変更の必要再資格だけ行う。

BUG3021/3022・YKT2542/2546、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-422 API認証暗号化値の内部構築境界とfinally試験（2026-11-15）

AuthContextCodecのpublic4引数/既package-private5引数を維持し、新package-private6引数へ内部EnvelopeFactoryを受ける。旧5はprivate static finalのEncryptedAuthContext::newへ固定委譲し、全通常Production組立は既record構築/防御clone/同byte/同例外を維持する。外部設定・HTTP・service loader・反射でfactoryを選択しない。追加interfaceはpackage-privateのcreate(version,storedCiphertext)一操作だけ、鍵/平文/nonce/Cipher/JCAprovider/認証/権限/DBには触れない。factory引数nonnullは既鍵/version/random検査後・機密copy前にconstructorで確立する。createの戻りはnullable境界として明示し、nullなら既CRYPTO_UNAVAILABLE固定例外へ拒否する。factory呼出しは既stored及びencryptedの二finally内に置き、Error/RTEがそのまま伝播してもowned二配列とplaintext/nonceが消去されprivate lockが解放される。実OOMやprivate reflection/JCAprovider差替え/拒否試験の代替を行わない。default record生成の内容/size/暗号/version/AAD/保持/再送/publicAPI/承認済DIFを変更0。

既whole8の全本文/期待値と有限workerを保持し、新AUTHCTX-FACT001..003の3methodを同wholeTestへ追加する。001はpublic組立ciphertextを受け取った直後の直接AssertionErrorとIllegalArgumentExceptionの二caseで元throwable同一、stored全zero、次の別worker正常・独立DataOutput/JCA envelope一致・copy別identity/call2を確認する。002nullfactoryの構築前提拒否とnonce呼出0/元public key不変。003nullable factory結果nullを固定CRYPTO_UNAVAILABLE/原因抑制初期0へ拒否しstored消去後に同codecの別worker正常と独立goldenを確認する。全worker Future5/stop-await10assert後close、入力は既公開a64/keysequence/nonce2Aだけ、expectedにProduction生成を使わない。新sourceはMain5をRootNullAwayでfreshcompileし、増えたinterface含む物理数/Code数を実測、自然Code0を除外扱いしない。必要同source whole11を一singleexec、静的/CRC/init/XML/defaultと無filter必須LINE/METHOD/CLASS/BRANCH整数100を照合し、補助Instruction/Complexity/close例外未実行は全数保持し全命令/全例外をPASSにしない。旧8成功を足して11とせず旧8は新source必要再資格で新規0、新3だけ別計上する。全依存scope/正式451/CHR/native/ITST/HOLDは未受入。

BUG3023/3021・YKT2541/2542。状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-423 API context hashの内部計算境界と機密消去試験（2026-11-15）

ContextHashのpublic noargs/checked NoSuchAlgorithmException/calculate(AuthenticationContext)と既private stateLockを維持する。package-private DigestOperations（digest(rawASCII)、format(hashed)の二操作）とpackage-private constructorを追加し、public constructorはprivate JdkOperationsの既SHA-256 MessageDigestとHexFormat.of().formatHexだけへ固定委譲する。外部設定/HTTP/ServiceLoader/反射/DBからOperationsを選ばず、通常production組立の認証判定・rawASCII64→SHA256→lowercase hex64・借用context・例外identity・provider選択・共有digestの排他を変更0。Operationsのnonnullを機密取得前constructorで確立、二戻りは内部nonnull契約、所有raw/hashedの各既finallyを維持し、digest/formatから直接Error/RTEが伝播しても取得済owned配列を消去しprivate lockを解放する。private stateへの反射/実OOM/独自provider/権限操作/拒否試験の迂回を行わない。

原ContextHashTest全三の有限worker/固定Python hashlib vector/100並行/null/未知/元provider unavailable復元の全本文と期待値をexact保持、新HASH-OWN001/002/003を同wholeTestへ追加する。001はdigestとformatの各段階で直接AssertionError/IllegalArgumentExceptionを一回だけ発生させ、原throwable同一、captureしたowned raw及び生成済hashed全zero、次の別workerによる同hashの固定既vector成功/call2/borrowed context不変を確認する。002はnulloperationsの構築前提拒否（機密入力なし）。003は通常委譲のrawASCII長64/byte a、32byte公開固定SHA値、独立lowerhex string/copy所有/zero/otherworker及びprivate lockのcaller-monitor非干渉を確認する。期待値をContextHash.calculateから作らず元固定二vectorとJDK明示SHA-256のactual処理だけ使用。新sourceMain/内部adapter/抽象interface実Code0をRoot25/NullAway/staticでfresh構築し、必要同source全六一singleexecの真正XML/source/CRC/initと無filter実Code必須四を照合、自然Branch0/Code0を人工100/除外にしない。元三を新規定義へ加算0、補助Instruction/Complexityや全178/451/leaf/CHR/nativeは未受入を保持する。

BUG3027・YKT2541/2550。状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-424 JDBC資源nonnullと発行・監査の明示終了（2026-11-15）

AuthSessionService.issue及びSessionAuditWriter.writeの全owned PreparedStatement/ResultSetは取得直後に既RequiredColumn.requireValueを通しnonnullを確立する。provider返却nullは既22004 SQLDataExceptionとして拒否し、発行側は既9000固定AuthenticationInfrastructureExceptionへ変換する。正常SQL/順序/binding/lock/rowcount/時刻8時間/microsecond/DIF016/監査JSON/role/owner/暗号/format/public API/呼出元TX所有を変更しない。Connectionは借用でcommit/rollback/close/setAutoCommitを行わず、取得できたstatement/rowだけを一回逆順にcloseする。各nonnull資源の本体を明示try-catch(SQLException|RuntimeException|Error)-finallyで保護、catchはnullable primaryへ同一failureを保存して再throwし、finallyはAPI database内の小さいstateless JdbcResourceCleanup.close(primary,SqlClose)でcloseする。SqlCloseはthrowsSQLExceptionに限定したfunctional interface、cleanupはstatic操作だけを持つ非生成可能interfaceで余分なconstructor/instance状態を持たない。action nonnullは呼出前提。close成功はprimary graphへ変更0、primary無しclose失敗は同一SQL/RTE/Errorを伝播、primary有りclose失敗は元primary.addSuppressedで元graphを保持、同一instance self-suppressionはJDK IllegalArgumentException/causeをTWR同様に維持する。Batchの別failure precedence helperを流用せずAPI→Batch依存0、fatal分類の追加/変更も0。INSERT ciphertextはprepare/nonnull検査まで含む最外側の既finallyで必ずzeroにし、取得失敗を保護域の外へ出さない。resource nullは取得無しでrelease0、row nullでも既statementは一回closeする。外部設定/provider/driver接続/資格/権限/秘密/DDL/電文/承認済DIFを追加変更0。

原issue8/audit9の全Test本文・独立三AESgolden/固定hash/完全SQL/UTC/JSON/alias/error/所有/finite workerを保持し、Issueの既純粋Proxy FixtureへnullStatementAt/nullRowAtのdefault空値controlだけを追加する。新AUT-ISS-RESOURCE001/002はstatement五箇所(USER/INSERT/ACTIVE/REPLACE/AUDIT)とrow二箇所(USER/ACTIVE)のnull返却を独立に与え、9000固定/cause-suppression初期0/owned row-statement一回close/借用TX変更0/entropy-nonce-ciphertext全zeroを確認する。新JdbcResourceCleanupTest全五はaction null前提、通常closeの呼出一回/primary不変、primary無しSQL-RTE-Error同一、primary有り各closefailureの正確なsuppressed identity、selfaliasの元IllegalArgumentException causeを固定graph期待で検証。期待をproduction cleanup/hash/codecで作らず元literalと独立公開objects/countersだけを使う。新七だけ新定義、旧十七は新Main必要再資格で新規加算0、全二十四を当source一singleexecにしてfreshRootNullAway/static/Code物理実測/CRC-init/XML/default+raw必須四を照合する。新interface/SqlClose/package Code0は自然値、未実行をcompiler除外/到達不能/旧exec合算へしない。実DB/生session/Root/cohort/VM/native/aru/actual4/Root2/SDKbackend/HOLDは未受入を維持する。

BUG3033・YKT2553/2546。状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-425 JDBC型付き終了所有契約（2026-11-15）

SSC424のcallback越しclose所有がSpotBugs OBL一件として未確定となったため、JdbcResourceCleanupへStatement専用closeStatement(primary,statement)とResultSet専用closeRows(primary,rows)を追加する。両者はnonnullを明示検査し、直接resource.closeを一回呼び、SQL/RTE/Error失敗はprimary無しで同一throw、有りで元primary.addSuppressed、自分自身の場合も元JDK IllegalArgumentException/causeを維持する。既close(primary,SqlClose)及び原五testは保持する。親Issue/Auditは型付きadapterへ変更するだけで、SQL/binding/8h/DIF016/暗号/borrowed Connection/TX/INSERT最外側消去/既例外graphを変更しない。実漏れは未確認で、抑制/除外による静的合格にはしない。既取得SDK com.google.code.findbugs:jsr305:3.0.2 の実在javax.annotation.WillClose（RUNTIME retention、通常parameter所有契約）をAPI provided依存として宣言し、各typed parameterへ付与する。注釈はclose責任の宣言でありSuppressFBWarnings等の抑制ではない。SDK変更/ダウンロード/実DB/driver/権限/外部経路追加0。原SpotBugsannotations4.10.4に同annotationがあるとのBUG3034初記述は誤認であり、実SDKメタデータの照合で訂正する。新二testは両adapterごとにnull前提/正常/SQL-RTE-Error/primary/alias/一回closeをJDK純粋Proxyと独立identityで検証し、新合計九＋既十七の必要全二十六をfresh同source compile/NullAway/static/CRC/XML/必須四rawで測定する。原二十四未実行をPASSへ加算0、旧compile/static一件は歴史証拠として保持する。

関連BUG3033/3034・YKT2553・SSC424。状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-426 API取消JDBC資源nonnullと明示終了（2026-11-15）

AuthSessionRevocationServiceのlogoutCurrent/revokeAll/updateにおけるowned statement五取得/row四取得を取得直後RequiredColumn.requireValueでnonnullに確立し、既SSC425 JdbcResourceCleanup.closeStatement/closeRowsと明示primary(SQL/RTE/Error同一再throw)-finallyで一回終了する。SQL文字列/binding/order、User/session lock後clock採取/microsecond、期限境界、既取消済idempotent/監査理由/ADMIN認可/N12/allowed-reason/rowcount/例外分類/元graph/selfalias/borrowed Connection/TX所有を変更しない。悪いnull providerは既22004に統一、resource無しをcloseしない。Audit/Hash/helperは既同byte、実DB/driver/Root/サービス/VM/鍵/権限/HOLD変更0。原SessionRevocationJdbcPortTest8の完全SQL/固定SHA/JSON/UTC/lock後時刻/全null/role/owner/理由/再送/rowcount/cleanup/並行期待を保持し、無期限pool closeだけshutdownNow→await10assert/classTimeout30に是正する。既fixtureへnullStatementAt/nullRowAtのdefault空controlを追加、新二件はLogout U/S/X/LとADMIN T/A/X/L statement及びU/S/T/A rowのnullを独立入力して固定9000/owned一回/borrowedTX0/後続処理非発行を検証。原八＋新二全十をfresh閉じたMain/RootNullAway/static/CRC-init/XML/実Code必須四で測る。旧DBfixture/旧012全APIjarを流用しない。

BUG3035/3036、YKT2546/2553、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-427 認証検証のnonnull終了とprivate carrier（2026-11-15）

AuthenticationContextVerifier.verify/readSessionの三owned statement/二row取得へ既RequiredColumn.requireValueを置きnonnull・22004を確立し、既typed JdbcResourceCleanupとprimary SQL/RTE/Error同一再throw/finally一回終了を使う。verify/inspectReadOnlyの公開signature、SQL literal/順序/User→session lock/currentActor/role/期限/readonly非lock非touch/UTC/8h greatest touch/rowcount/固定失敗分類/borrowedTX/秘密/電文は不変。private VerifiedSessionは二fieldを当class内のreadSession→verify/inspectだけへ運ぶ非公開carrierであり、参照するのはid()/actor()だけ。recordの値同一性・自動表示・hashを業務契約として使わないため、private static final classへ整理しfinal UUID sessionId/final AuthenticatedActor authenticatedActor、constructorでObjects.requireNonNull二つ、同名二accessorだけを持たせる。外部型/serialization/wire/public値契約の変更0、不要なprivate値操作やテスト専用口を追加せず、全残Codeを通常公開業務経路で意味ある期待により検証できる形にする。測定から既Codeを除外/到達不能認定せず、旧record形状は歴史として保持し新形状を独立測る。原AuthenticationVerifierJdbcPortTest6のSQL/hash/currentDB actor/readOnly/拒否/nullcolumn/rowcount/cleanup/未知RTE/並行全期待を保持、workerのみshutdownNow/await10assert/Timeout30へ有限化する。既FixtureのnullStatementAt/nullRowAt default空controlとacquired記録を追加、Mapのnullable要素とruntimeFailure nullableをJSpecifyで明記する。新資源null二はverify User/Session/Touch及びinspect READ statement、verify User/Session及びinspect Session rowのnullで固定9000/取得済一回close/borrowedTX0/最後SQL一致を独立検証。原六＋新二の全八、Main閉包11（SDKjsr305だけ追加で既取得/全Protocolは同byte）/freshRootNullAway/static/全物理CRC/XML/default及びraw必須四を照合。実DB/driver/旧全APIjar/Root2/Actual4/VM/native/aru/HOLD操作0。

BUG3039/3040、YKT2546/2553、状態:設計確定・main反映前、PG/PT/正式未完。

2026-11-15 SSC427継続補足（BUG3041）: private field名のみsessionId/authenticatedActor、既id()/actor()/nonnull invariant/SQL/public結果は不変、新fixture user labelは新側constant化・元6期待除去inverse保持。初回static32/未実行8を保存しfresh必要資格へ。

## SSC-428 ADMIN前処理資源nonnullと明示終了（2026-11-15）

AdminCommandAuthenticator.verifyIdentity/owner/lockUsersの三owned statement/三row取得へ既RequiredColumn.requireValueを置きnonnull・22004を確立し、既typed JdbcResourceCleanupとSQL/RTE/Error primary同一再throw/finallyで一回逆順終了する。advisoryの二資源TWR headerは同じ取得順/逆順終了のnested単一資源へ正規化してから明示終了にする。SQL全文/7mutation集合/target presence-N12/候補owner単一行と範囲/減少系だけadvisory一行/候補target現ACTIVE ADMINの昇順lock/locked owner再照合/最新Verifier/currentADMIN/Inbox前段/rowcount/UTC8h/既失敗分類/primary-suppression-selfalias/borrowedTX所有を変更しない。実advisory lockや利用者更新は発行せず、元091 PT_DEFAULTの既hardcoded JDBC-interface fixtureだけを使う。原AdminPreludeJdbcPortTest8の完全SQL/固定hash/UTC/Mapbindings/全7Mutation lock有無順序/cardinality/owner非権限/拒否/rowcount/資源/並行全期待を保持し、poolだけfinally shutdownNow/await10assert/Timeout30へ有限化する。fixture runtimeFailureのnullable契約とdefault空nullStatementAt/nullRowAtを明記、新null二はstatement全7label(candidate/advisory/users/locked/auth-user/auth-session/touch)及び非touch row全6labelを固定DISABLE入力で試し、固定9000/cause-supp0/最後label/owned一回/borrowedTX0を検証する。下位Verifierは同byte既qualified12を依存としてfresh Root閉包へ含めるが成功件数へ加算しない。新Mutation閉集合一は固定CREATE/ENABLE/DISABLE/PROMOTE/DEMOTE/RESET_PASSWORD/UNLOCK順序とidentity/valueOf/防御values/unknown-empty-case-space-null、membership減少はDISABLE/DEMOTEだけと明示期待で検証する。元八＋新三全十一、Main14/全195physical/RootNullAway/static/CRC-init/XML/default及びraw対象Admin本体とMutation全Codeを照合する。旧012全APIjar/realDBfixture/Root/VM/native/SDKbackend/aru/四held/HOLDへ拡張しない。

BUG3044/3045、YKT2546/2553、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-429 Login JDBC資源nonnullと有限worker寿命（2026-11-16）

LoginAttemptRepositoryの五statement二row、LoginAuditWriterの一statement取得へ既RequiredColumn.requireValueを置きnullをSQLSTATE22004とし、既JdbcResourceCleanup.closeStatement/closeRowsとnullable primary、SQLException/RuntimeException/Error同一再throw/finallyでTWRと同じ一回逆順終了を保持する。SQL文字列/取得lock User→IP/username NFCと長さ/role-status/count/USER5-IP10/15分/window境界/成功失敗更新/rowcount/UTC/borrowed connection所有/監査列-action-details値/秘密非保存/固定9000-fatal-preserveを変更しない。AuthenticationService本体に仕様変更を加えず、その通常全体を既API Memory16で検証する。既in-memory JDK Connection/Statement/ResultSet proxyと自身の未発行zero-key AuthContextCodecだけを使い、実DB/driver/サーバLogin/VM/Root/Actual4/HOLDへ拡張しない。元16全入力・独立固定期待をinverse exact保持し、Memory016はpool明示stop/await10assert後だけ二fixture close、await失敗時codecを稼働workerへ残し成功扱いしない。classTimeout30。新null二はUSER/CREATE_IP/IP/UPDATE_USER/UPDATE_IP/LOGIN_AUDITの六statement、USER/IP二rowの固定9000/cause-supp0/最後取得位置/取得済owned close一回/未取得資源無し/秘密配列消去/borrowedTX0を検証する。元16＋新2全18、freshMain閉包/RootNullAway/静的指摘適用性全件/物理CRC-init/XML/raw四counterを三target AuthenticationService/LoginAttemptRepository/LoginAuditWriterについて確認し、未達を明示する。旧全APIjar/原realDBfixtureのcopyや抽出は行わない。

BUG3047/3048、YKT2546/2553、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-430 Web form分類のfatal保全と有限単体試験（2026-11-16）

LoginFormAuthenticationConverter.convertの既catch(IllegalArgumentException|IllegalStateException|NoSuchElementException)では、固定LoginFormRejectedExceptionへ変換する前に既SessionStoreException.preserveFatal(failure)を呼ぶ。元Error/cause/suppressed/SQLnextをidentity seenで有限走査する既helperを再実装せず、Error無しの例外は原因/診断を保持しない同じ固定input rejectionを返す。通常POST/login/UTF8/contenttype/charset/query予約名/parameters多重-null/数値proxy信頼/非認証token/char[]受渡し/CSRF前提/公開API/400入力拒否と403proxy拒否/ログ秘匿/上位503分類/承認DIFを変更しない。外部設定/provider/資格/権限/実認証/DB/MQ/鍵/Root2Actual4/VM/native/aru/HOLDを追加しない。元LoginFormConverterPortTest全13の全入力/独立HTTP・token・配列消去期待はinverse exact保持、八task/二worker/既Futureget10を保ちfinally shutdownNow/await10assert/classTimeout30へ有限化する。新FORM014は三分類例外それぞれcause/suppressed内の公開合成AssertionErrorをgetMethod/getParameterValuesから与え元Error同一/固定正常結果0を検証、新FORM015はError無しcause循環/共有suppressedの固定秘匿分類と未分類RTE同一を確認する。既JDK Servlet-interface proxyだけを使いMockserver/actualcontext/key/native/JDBCを起動0。safe MainはConverter/CaddyResolver/LoginClientAddress/FormRejected/CaddyRejected/SessionStoreException/InvalidSessionRowExceptionの七source、SDKは既qualifiedServlet6.1/Spring7標準libの明示hashだけ、旧全Web/APIjarを読取・hash・抽出・定義しない。原13＋新2全15、一source/runのfreshRootNullAway/静的全site/物理CRC-init/XML/default及び無filterConverter必須四整数100、依存七全体の未達を隠さない。

BUG3063/3064、YKT2546/2556、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-431 Login現在context probeのfatal保全（2026-11-16）

MqLoginContextProbe.isActiveの既七catch(JMSException/JMSRuntimeException/JmsRequestReplyException/PermanentProtocolException/IllegalArgumentException/IllegalStateException/DateTimeException)は固定UNAVAILABLEへ変換する前に既JmsRequestReplyException.preserveFatal(failure)を呼び、cause/suppressed/SQLnext/JMSlinkedの元Error identityを有限に保存する。header/IF003現在context再確認/UUID freshness/256byte request/全reply検査/0102 false/他非success固定例外/timeout1ns..2s/12wait/再Login禁止/所有request-sendercopy-reply-data-records全消去/正常認証ロール/公開API/秘密非保持を変えない。Provider本体は変更しない。catch唯一のfinal MqLoginExchangeExceptionはsuper(message,null,false,true)によりcause/suppressedを保持できず今回のmissing-guard条件に非該当、固定reason INVALID_INPUT/UNAVAILABLEと例外秘匿を独立回帰契約にする。新PROBEGRAPH001は各七catch族の公開合成Error graph（JMSlinked→SQLcause含む）を既memory senderから与え元Error/256ownedcopy全zero/pending0と同one-slot clientで別freshID正常復帰を検証する。新LOGINFAILVALUE001は二reasonの固定message/nullcause/disabledsuppression/initCause拒否/null constructor/enum閉集合lookup/values防御を独立literalで確認する。元MqLoginClientTest8/ProbeTest3/ProviderTest5の全16本文・独立wire・100並行/get10/stop-await5及び既固有例外/消去期待は保持、compile依存するfixture helperは抽出せず元whole class全実行する。新2＋旧16全18を一source/run、既明示safeWeb18sourceと現在Protocol176だけfreshRootNullAway/static/物理CRC-init/XML/default/raw対象Probe/Provider/ExchangeException全sourceで照合する。旧162/166/Protocol130は確認再演0、実JMS broker/socket/DB/auth session/鍵/Root2Actual4/VM/native/aru/HOLDや旧全WebAPIjar読取抽出を行わない。

BUG3065/YKT2556、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-432 認証Providerの資格消費契約を一箇所へ集約（2026-11-16）

MqAuthenticationProvider.authenticateの既finally二guard（captured credentialsがchar[]ならzero、その後authenticationがUsernamePasswordAuthenticationTokenならeraseCredentials）を、同じclassの一つのprivate static consumeCredentials(Authentication,@Nullable Object)へ同順・同条件で集約する。finallyはこのhelperを一回呼ぶだけとし、正常/拒否/例外で資格消費の実装を一箇所へ統一する。authenticationの既nonnull前提/getCredentials一回をtry前に採る順序、nullable credentialsを含む不正型/unsupported subclassの拒否、公開API/認証成功条件/closedprincipal/Role/Probe/再送/014/0101/0106/9000分類/char配列zero後tokeneraseの順序・回数/cleanup例外の既優先を変えない。helperを公開・port・外部設定化せず、private reflection/SDK型偽装/到達不能扱い/除外/閾値緩和で分岐を隠さない。PG34545の通常return/例外の二重生成cleanupに対し、既通常API試験が持つ成功・不正token型・null/非char資格・派生型・transport失敗の実入力で単一helperの両guardを検証する。元Client8/Probe4/Provider5/closedfailure1全18の全source/期待/fixtureはbyte exact保持、新Test定義0。fresh safeMain18/RootNullAway/静的/現在SDK-JDK/protocol/物理CRC-init/XML/default及び無filter対象Probe/Provider/ExchangeException全Codeの必須四100を同一source/runで確認、旧18成功/defaultを新sourceへ転用0。外部権限/認証経路/実JMS-DB-session-key/Root2Actual4/VM/native/aru/HOLDを変更0。

BUG3067/YKT2431/2556、状態:設計確定・main反映前、PG/PT/正式未完。
