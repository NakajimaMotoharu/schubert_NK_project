# 認証・認可・session・CSRF実装設計

## SSC413 初期ADMIN内encoding失敗の消去試験口（2026-11-15）

SSC412に続くBUG2993/YKT2522の内部testability補足。PG33556全28FES0/既定四100とPG33560無filterbranch-line-method-class100は保存するが、BootstrapAdminService.createのencode例外finally 6instruction未達なので全Code未資格。到達不能扱い/coverage除外/合成PASSで閉じない。

BootstrapAdminServiceのprivate final PasswordHasher fieldをprivate final Function<char[],String>境界へ変え、既public noarg descriptor()Vを明示public constructorで保持し this(new PasswordHasher()::encode)へ固定bindする。package-private BootstrapAdminService(Function<char[],String> encoder)だけをnon-null内部試験口としObjects.requireNonNullでinvariant確立。外部設定/HTTP/DB/bean/roleからencoderを選択する経路を追加しない。既Productionは全て引数0呼出を維持し、PasswordHasherの公開default pin/PBKDF2-v1/validation/SQL/認可/owner/再送/正常戻り値を不変更。create内passwords.encode(normalized)を同じ引数のFunction.applyへ結ぶだけで二段のfinally消去を維持する。

新BOOTBOUND019はメモリ内throwing FunctionのRuntime/Errorを各独立に作り、NFC前24charのcaller入力、観測NFC後12charのnormalized配列の全0、同一failure、SQLがexistsまで4文でinsert/audit0、取得済resource終了/caller非操作を確認。null Function ctorはfailfast拒否。実provider/algorithm/credentialを操作せず、成功暗号期待は旧独立JCA三Testを保持する。旧18Boundary/4Hasher本文はbyte保持＋新1、定義は新群合計20/既security9、全29/5Main6physicalを同source一exec、RootNullAway/lint-Werror/CS/SB/PMD全site、CRC-init/既定・無filter全Codeの四100（instructionもmiss0）で検証する。元27/28は未資格として保全し新29へ加算しない。

費用は元開始.9/2.7/6.0と追補.9/2.7/3.9、現群計1.8/5.4/9.9 cap10を据置き。追補の内訳をresource .6/1.8/2.4、Hasher fault .2/.6/1.0、ADMIN direct fault .1/.3/.5へ再配賦（合計同じ）、今回追加予算0・手戻り実費/token不明。追加発見と再認証を完成率へ変換しない。原費用/SV/原904.85等/正本625・元190・正式1964/53・工数null、実DB/BootstrapAdminMain/native/RootActual4/VM/aru/全PGPT/ITST/HOLDは維持。

## SSC412 初期ADMIN資源終了と暗号失敗（2026-11-15）

SSC411/BUG2983のnull境界は保持し、PG33510全27FES0/default四100に対するPG33514無filter48instruction/20branch/1line未達を解消する内部補足。原Unit23bb667e/Core29e32fb7/PG33510-33514は成功試験27件だが全Code未資格として保存し、受入/正式/工数へ加算しない。

BUG2989/YKT2518: BootstrapAdminServiceのnull検査済みStatement/ResultSetはTWRの重複close-null分岐を残さず、明示primary+finally closeへ構造化する。shared lock→membership→tablelock→exists→insert→ACTION/SECURITYのSQL文字列・getter/setter順・normal result・消去を保持。preparedとresultのtyped null guardはそのまま使用。query/read/lockとcloseStatement/closeResultのprivate helperで、取得済み資源を一回だけ逆順にclose、SQL/Runtime/Errorは元primaryを再throwし、別secondaryだけaddSuppressed、同一objectはself-suppressionせずprimary identityを維持。primaryなしのclose故障は当故障をそのままthrow。Exception graphを通常catalogへ分類する責務は既BootstrapAdminMain側に残し、そのHOLD実class/原fixtureを実行しない。caller Connection/commit/rollback/closeを所有せず、再取得/再送/rollback新発行をしない。readはprivate固定modeによりshared Boolean(true必須)、membership void単一行、exists Boolean、ID long(N12)の既wasNull/境界/余剰行検査順を維持。到達不能として除外せず実際の全条件を独立試験で測定する。

BUG2990/YKT2519: PasswordHasher公開noargは既Pbkdf2PasswordEncoder.defaultsForSpringSecurity_v5_8()/hex/DelegatingPasswordEncoder pbkdf2-v1の固定factoryへdelegateし、default behavior/生成・読取algorithm/ID/公開APIを変更しない。package-private PasswordHasher(PasswordEncoder)だけを内部testability境界として設け、nonnull invariantはObjects.requireNonNull。外部設定/HTTP/DB/bean/role/provider登録からencoderを選ばせず、既Production呼出は全てpublic noargを維持。新独立PasswordHasherTest追加一件(PT-AUT-HASHFAULT001)はthrowing encoderのencode/matchesで同failureとcaller入力/観測CharBufferのNFC12char消去を確認する。SDK/provider実設定や暗号期待値の変更を行わず、null port拒否も確認。旧三Hasher Test本文・他既security六本文を保持する。

BOOTBOUND016はmanual cleanupのprimary/secondary三型全組合せをStatementとResultSet各ownerで照合し、同一Errorは従来のTWR self-wrapperではなく元object直接伝播を独立期待とする（Mainの既固定failure結果/graph責務を変更しない）。他17Boundary本文/固定SQL/normal binding/JCA期待は保持。追加new1により独立定義は新19/既security9、同source全28/5Main6physical。RootNullAway/lint-Werror/CS/SB/PMD全site/CRC-init/既定と無filter全Codeのline-method-class-branch100、例外/null/資源後条件を照合する。coverage除外/抑制/旧exec合算/合成PASSなし、実DB/ADMIN作成/BootstrapAdminMain/native/原DBfixture/RootActual4/VM/aru/全PGPT/ITSTは未受入/HOLD継続。

群PGPT-WBS65-SSC411-ADMIN-BOUNDARY18-SECURITY9-HOST27-20261115の開始.9/2.7/6.0ppと5389 eventを凍結。新発見の上記二依存に.9/2.7/3.9ppを追補し、現群合計1.8/5.4/9.9pp/cap10へ改訂、初回見積りを書換えない。前提となる自動生成分岐/消去失敗の不足のためで、原P01005/P00701費/SVを重複消化せず当追補だけ追加する。共有消費/専有実費/tokenは別記、欠測null。通常小群で停止せず現接続経路を閉じる。原904.85等/正本625受入184・元190受入17/正式1964-53/工数nullを保持。

## SSC328 ordinary認証/sessionのfatal JDBC graph（2026-10-21）

横展開追補（同日・PG前）：RevocationRetryCoordinator.transactionの固定catalog化前にも同じcause/suppressed-only helperがあり、SQLException.nextのfatalを見落とす。ここもsession側と同じ既cause→suppressedの後にnextを追加する。wire送信自体や再送間隔・DB commit/rollback/close順は不変更。対象を三Main/新九Testへ確定し、PT-REVOCATION-GRAPH328001..003でnext fatal・混合cycle・既fatal優先を独立検査する。初期の二Main/六Test計画は履歴、実Root/nativeの保留は不変更。

既BUG622/628のfatal cleanup保持を、同じ認証/sessionのtransient JDBC例外graphへ明確化する。cause、suppressed、SQLException.getNextExceptionの全reachable Errorは同一objectのまま伝播し、固定AuthenticationInfrastructureException/SessionStoreException又は通常の再送/9000/503へ縮退させない。Error無しのgraphはobject identityで訪問済みを除き有限帰還し、SQL/provider text/cause/suppressedを固定catalogへ保持しない。JMS linkedは当JDBC境界の入力契約ではなく、送信境界SS312の別契約のまま。

既直接primary Errorを最優先にし、既edgeのみの順位は不変更。認証は従来のsuppressed順の後にcause/SQL next、sessionは従来のcause→suppressed順の後にSQL nextを追加する（各nodeのFIFO探索）。新edgeを先に回して既fatalの選択を変更しない。正常/非fatal時の業務結果・認証/session/SQL/transaction/最大2session・DIFは不変更。BUG1591/YKT1344、PT-AUTH-GRAPH328001..003/PT-SESSION-GRAPH328001..003で、pure固定Throwableのcause/next fatal・混合cycle・Error無し・既順位を独立検査する。実Root/Unit/DB原本/keys/cohortへの操作・権限を追加しない。設計補足確定とPG/PT/native/正式品質の完了を区別する。

## SSC267 Login単体試験の独立境界（2026-10-12）

§5.1のUser→IP lock順、locked時hash省略、PBKDF2-v1 310000 iteration、最大2session・最古revoke、DB/MQ timeout9000・失敗counter不増を維持する。承認roleのstatement1500ms/lock500msを、実機CPUや並列request数を理由に延長しない。同user8並列12requestが全件一度でcommitすることは外部保証ではない。

PTでは実DBの同owner並行session/失敗窓/監査のSQL invariantと実cryptoを分割する。並行DB試験のpassword判定doubleは合成固定fixtureへ独立に限定し、全12成功・20失敗のDB事後条件を維持する。実PBKDF2は別JCA golden/正常/誤password/no-account/disabledの試験を維持する。別DB timeout負例では固定role設定を先に確認し、独立transactionでuser行を保持、Infrastructure境界/rollback後のsession・counter・audit不変とpassword消去を検証する。double試験を実crypto並行性能、timeoutをLogin成功、旧失敗をflaky/合格へ読み替えない。PG/PTは本条件の実装整合性のみ、性能p95及びIT/ST受入は後続実機で別確認する。関連BUG1108/YKT877/SS332353/PT-AUT-004。

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

通常要求は単一business `SecurityFilterChain`とし、順序を固定する。SSC-047として、container内部の`DispatcherType.ERROR`かつ`/error`だけは、その手前の非業務error chainへ限定分離する（§3.2）。

1. Forwarded headerはCaddyからのloopback接続だけを採用し、外部値を上書き済みとする。
2. Request ID/filter、security header、session repositoryを適用する。
3. CSRF tokenを全POSTへ検証する。Login POSTも例外にしない。
4. `/login`、static CSS/JS、`/error`だけpermitAll。Actuatorは別loopback port＋OS/network制限。
5. `/admin/**`と`/logs`は`ROLE_ADMIN`、その他保護URLはauthenticated。
6. Form loginは`MqAuthenticationProvider`、success/failure handler、safe SavedRequestを使用する。
7. LogoutはPOST `/logout`だけ。API revoke coordination後にcookie削除・session invalidateを行う。
8. 401/403はHTML/media/POSTごとのhandlerでUI 221の遷移へ変換する。

`ROLE_` prefixはWeb framework内部だけとし、wire/DBのroleは`USER`/`ADMIN`を正とする。

### 3.1 Login providerと再送時の現在認証（SSC-043）

SSC-043（§3のprovider詳細）: MqAuthenticationProviderは未認証のusername/消費char[]/trusted Caddy由来numeric IPだけを入力とし、IF-001の0000または現在context確認済み0200だけからROLE_USER/ROLE_ADMINと閉SessionPrincipalを返す。0101/入力不正、0106、9000を混同しない。0106の後段表示へ渡す追加値は0..900秒のみ。失敗例外へpassword/元cause/wire本文を保存しない。全終了でchar[]をzeroしinput tokenのcredentials参照を外す。Session保存はcustom fixation strategyの短transactionへ分離する。

Login replay0200の現在context確認は324 §6.1を具体化し、新UUIDの既存IF-003 GAMREQ01を1回実行する。APIの通常context検証とgame readが成功した応答だけを認め、0102は未認証、その他error/timeout/不正応答は一時障害にする。Responseの相関/context/layout/総長/DATA/record全検査を必須とし、取得したgame内容を画面やcacheへ流用しない。これはLogin再送/新session発行ではなく、既存保護readによる最新認証確認である。role/status/password変更の既定全session失効を維持し、以後の業務API再認証も省略しない。元snapshotの初回expiresAtを現在idle期限と混同せず、現在有効性はAPIを正とする。Wire/DDL/外部画面仕様は不変更。

### 3.2 内部error dispatchと依存障害（SSC-047）

UI221/222のMQ/DB一時障害503共通errorを、失敗したsession/DB/keyへ再依存せず表示する。BUG-074/YKT-066の是正として、InternalErrorDispatchRouterを単一business FilterChainProxyの手前へ置く。実containerのDispatcherType.ERRORかつrequest URI exact `/error`だけを、UTF8と解決済表示snapshot/CSRF再投影の非業務filterへ渡す。外側Caddy検証・server request UUID・security headerは共通必須。StrictHttpFirewallは通常business要求の必須検査として維持し、拒否済み元method/headerを内部error表示へ再適用しない。通常REQUESTの`/error`、外部POST/PUT、ASYNC/FORWARD、ERRORの別URLはbusiness chainを通り、認証・CSRF・URL roleを省略しない。HTTP header/query/attributeの偽dispatcher値を許可条件へ使わない。両分岐の終了でSecurityContextをclearし、内部error branchの表示以外のhandler/JMS/DB/更新への利用を禁止する。

通常chainで閉principalを復元した後、要求内の表示用TopBar（brand/username/roleだけ）と解決済CSRFのimmutable snapshotを取得できる。これはrequest scopeだけ、閉session JSON/DBへ属性を追加しない。Error chainはこの表示snapshotだけを使い、HttpSession/getUserPrincipal/SecurityContextの再読、DB/JMS、CSRF再生成を行わない。取得前に障害となった要求は匿名error表示とし、認証済みと推測しない。API0102等の明示失効時にはsnapshot/CSRF表示をclearする責務を後続handlerへ持たせる。raw認証context/password/session IDはsnapshot/modelへ入れず、CSRFは正規POST formのhidden inputだけに使用する。

session repositoryの固定SessionStoreExceptionは外側境界で未commit応答を503 sendErrorへ変換する。すでにcommit済み、またはerror dispatch自体の失敗は再dispatchせず不成功として伝播する。NPE/任意RuntimeExceptionをcatchして成功へ変換せず、containerが未commitの未知障害をerror dispatchした場合は安全な503画面へ分類する。Proxy不正は既存BUG070方針どおり403空bodyで終端しerror chainへ入れない。

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

SSC-014: Usernameの表示入力はNFC/trim後1..64 UTF-8 byte、比較keyはLocale.ROOT lowercaseで生成しDB上限96byteとする（331）。U+0130×32は表示64byte/key96byteとなるため、比較keyのbyte数を表示制約へ代用しない。Login照合はkey、監査は元の正規化表示入力を使用し、wire/auditの64byteを維持する。User作成も同じ正規化factoryを使用する。JDK更新時はUnicode scalarの最大増幅3/2と文脈依存lowercaseを回帰する。

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

SSC-046: Form Loginの失敗/lockは351 §5.1の補足どおり現行302 `/login?error`または`/login?locked`を維持し、lockのRetry-AfterはAPI確定値だけを使用する。Webで失敗counter/lock時刻を再計算しない。成功handlerはcustom fixation後の永続principal同値を検査し、閉SavedRequestまたは`/`へ302する。汎用Spring認証例外のsession保存やURL session rewritingを使用しない。QA-055/UIC-012/SSC-338（2026-11-06承認）: GET `/login?locked`はCurrentと同じ固定文「ログイン試行回数が上限に達しました。15分ほど待ってから再度お試しください。」を表示し、実残秒は画面へ引き渡さない。実残秒は既存の失敗応答HTTP `Retry-After`（API確定0～900）だけに返す。新たなsession属性・query parameter・残秒計算・動的表示を設けない。固定文のHTTP/DOMとheader境界の個別試験を行い、handler単体の成功だけで画面/CHR完了としない。

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

SSC-015: Logoutのowner付きInboxと保存snapshot/元失効参照は324 §6.2を正とする。Wireにclient IPがないLogout/管理失効ではAPI監査remote_addressをSQL NULLとし、Login時の過去IPやloopbackを現在のremoteとして捏造しない。Loginとそれに伴うREPLACEDは当該Loginの検証済みIPを保存する。remoteは351 §3.1の任意項目であり、HTTP側の現在IPはWeb REQUEST/SECURITY logの責務とする。いずれもsession識別子を監査へ出さない。

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
| operationTokens | pending＋consumed合計10件の用途、UUID、発行時刻、任意の初回完成時刻 | 更新timeout/PRG・QA049保持窓 |

Password、質問/回答本文、検索結果、固定長body、DB rowをsessionへ保存しない。Envelopeは`formatVersion`、`keyVersion`、12 byte nonce、
ciphertext/tagを保持し、AADはsession ID hash＋created_at。復号後の未知field/type/上限超過はdeny closedでsession失効。

#### 7.2.1 保存JSON version 1（SSC-038、QA-049後はlegacy readのみ）

以下は旧version 1の厳密read互換契約であり、現writeは末尾QA-049補足のversion 2へ移す。UTF-8 JSON objectとし、`formatVersion`（数値の整数表記1）と`operationTokens`（配列、0～10件）を必須にする。その他の許可keyは下表だけ。任意Spring Security/Session objectやclass名をJSONへ保存しない。Encoderの順序はformatVersion、認証4field、csrfToken、savedRequest、operationTokens。Decoderはkey順序/通常JSON whitespaceを許可するが、重複key（nested含む）、unknown key、JSON null、型違い、末尾別document、不正UTF-8/BOMを拒否する。

| key | JSON型 | 欠落・制約 |
|---|---|---|
| username | String | 以下4項目が全部欠落なら匿名session。存在時NFC/1～64 UTF-8 byte、control/不正Unicode/末尾ASCII space不可 |
| role | String | 認証4項目all-or-none、USER/ADMIN |
| authenticationContext | String | 認証4項目all-or-none、64 lowercase hex |
| loginAt | String | 認証4項目all-or-none、Instantのcanonical UTC ISO表記。現在権限やexpiry判断は外側責務 |
| csrfToken | String | 未発行は欠落、存在時64～128 ASCII base64url文字。標準発行は32 random byteの64 hexで満たす |
| savedRequest | String | 未保存は欠落、同一originの安全なGET path/query合計2048 UTF-8 byte。PG-D-093 value検証＋後段route allowlist |
| operationTokens | Array of Object | 各要素はpurpose/token/issuedAtだけを全件必須。purposeはUCRREQ01/USTREQ01/URLREQ01/UPWREQ01/ULKREQ01/QSBREQ01/NTCREQ01/QDLREQ01、tokenはcanonical UUID、issuedAtはcanonical UTC Instant。最大10件、同用途複数可、同UUID重複不可。順序を保持 |

未認証sessionにもLogin前CSRFとsafe SavedRequestを保存できる。認証4項目の部分存在は不正とし、role/contextだけの偽principalを作らない。Cookie ID、password、request body、検索結果、tokenに対応する入力本文は保存しない。last_accessed_at/expiry/versionは331のrow metadataを正とし、このJSONへ二重保存しない。

Plaintextは16KiB以下・JSON nesting最大3（root→array→token object）とする。この内部上限は許可field全最大値を包含することをPTで証明し、上位input上限を狭めない。復号/schema不正は外側repositoryが失効させる。平文codec部品はDB保存・認証・CSRF照合を行わず、永続化は必ず352のNKENC1/AES-GCM、session ID hash＋created_atに結合したAADを通す。

#### 7.2.2 Session NKENC1のAAD（SSC-039）

352 §11.2の共通NKENC1を使い、JSONは圧縮しない。AADは下記7fieldへ各々unsigned lengthの32bit big-endian prefixを付けて連結する。Callerはcreated_atをDBのmicrosecond精度へ事前確定し、codecはsub-microsecond入力を拒否して暗黙丸めをしない。

| 順序 | field | byte表現 |
|---:|---|---|
| 1 | purpose | ASCII `web-session` |
| 2 | table | ASCII `schubert_web_session.web_http_sessions` |
| 3 | id | UUIDのmost/least significant longをbig-endianで16byte |
| 4 | session_id_hash | lowercase hex ASCII64byte、raw Cookie IDではない |
| 5 | created_at | signed epoch seconds 64bit＋nano-of-second 32bitをbig-endian、計12byte |
| 6 | format | byte1個の値1 |
| 7 | key ID | 1～16 ASCII、DB key_versionとenvelope内IDに一致 |

PK/hash/created_at/format/key IDの変更は認証失敗にする。最大plaintext16384byte、最大envelope16436byte。Currentだけwrite、current/previousだけread。復号後は7.2.1閉schemaを検査して属性valueだけを返す。異常時の失効/監査はrepository/HTTP接続側、暗号部品は固定理由codeの例外で平文を返さない。暗号鍵はWeb session専用で、API context/Web log/revoke keyと共用しない。

#### 7.2.3 Technical rowの低位store（SSC-040）

`JdbcWebSessionStore`は331 §9.1の9列だけへaccessし、callerの非autoCommit/readOnly=false Connectionを借用する。Connectionのcommit/rollback/closeを所有しない。Statement/ResultSetは各methodで必ずcloseし、SQL/型/NULL/不正row/resource失敗は診断内容を保持しない固定例外。Raw Cookie ID/属性JSONを保存するmethodは作らず、暗号文/key ID型だけをbindする。

- `findLocked(hash)`: explicit9列＋`WHERE session_id_hash=? FOR UPDATE`。0件はOptional.empty、重複/SQL NULL/DDL値不整合は拒否。期限や暗号正当性をこの低位readで認可しない。
- `insert(row)`: 新規version0、更新数1だけ。UPSERTしない。
- `replace(original,replacement)`: identity(PK/hash/created_at)同一、versionが正確に+1。PK/hash/created_at/元versionをWHEREへbindし、ciphertext/key ID/last access/expiry/max inactive/versionだけ更新。0件はfalse、1件true、その他拒否。
- `delete(identity,version)`: PK/hash/created_at/元versionに一致するrowだけ削除。0件false/1件true、その他拒否。

不変rowはcreated/last access/expiryがmicrosecond精度、created<=last<=expiry、max inactive1..28800、version0..999999999、ciphertextの許可範囲を検証する。上限versionへの+1は拒否する。外側lifecycleがlock下で期限/暗号を検証し、8h idle延長とdirty属性mergeを行う。削除済rowへの古いHTTP saveを新規INSERTへ置換しない。Fixation旧削除＋新INSERTは同一短transaction、JMS/HTTP処理はDB lockを保持せず実行する。低位storeの合格はSpring Session/失効/並行merge完了ではない。

#### 7.2.4 暗号lifecycle service（SSC-041）

`EncryptedWebSessionRepository`はSpring Session adapterの委譲先として、DataSource/Clock/CSPRNG/UUID供給と専用SessionPayloadCodecを使用し、以下を短いWeb technical transactionだけで行う。JMS/HTTPやAPI password照合をtransactionへ入れない。

| operation | 契約 |
|---|---|
| create | 匿名principal・新CSRF・空SavedRequest/tokenで即時暗号化保存。新Cookie ID/DB UUID、idle8h |
| find | hash row lock後、現時刻をmicrosecond化してexpiry確認。一致/超過は削除、復号/schema不正も削除して不在。正常だけidle延長/current再暗号化して返す |
| mutate | 現在rowをlock/復号/期限検証後、現在属性へのpure callbackを適用。principal/CSRF変更は禁止、null結果/不変制約違反はrollback。SavedRequest/tokenの古い全snapshot上書きを行わない |
| authenticate | API認証済principalを受け、new Cookie/DB UUID/CSRFへfixation。UI226どおりSavedRequest/pending＋consumed tokenを含むallowlistを保持、旧削除＋新INSERTをatomic化。発行値衝突はrollback |
| invalidate | hash限定DELETEをcommit。破損rowでもlocal失効可能。API revoke/queue/監査・HTTP Cookie失効は外側 |

構造/NULL/型不正rowを表す`InvalidSessionRowException`を固定`SessionStoreException`のsubtypeとして区別し、失効用hash限定DELETEをstoreへ追加する。Row不正・復号不正・期限切れは削除commit後だけ不在を返す。DB接続/SQL/resource/暗号write故障はcommit前ならrollbackを試み固定障害、cause/suppressed診断を利用者へ返さない。commit成功後のclose故障は既に確定したDBをrollbackできないため、呼出側へ固定障害を返し、次のhash lookupで実状態を確認する。commit応答不明も未確定結果として扱い、成功を推定しない。

Idle延長はmax(現在時刻,既存last access)＋row max inactiveを用い、Clock後退で期限を縮めず絶対lifetimeを追加しない。新規/認証時は8h固定。version上限999999999の次はCookie/CSRF/created_at/属性を維持し、DB UUIDだけ新規発行して同hashの新row/version0へatomic置換、新PK AADで再暗号化する。旧PKのCASを成功させずABAを防ぐ。UUID衝突・想定外0件・commit/close故障は不成功で、呼出側が未確定成功を利用者へ表示しない。

本serviceはframework/監査handlerの実装完了ではない。Operation tokenの用途/完了/timeout handlerはsession全用途pending＋consumed合計10件を保ち、pendingを実装都合で破棄しない。QA049の完成first-write/退役条件は末尾補足に従う。

#### 7.2.5 Spring Session adapter（SSC-042）

SpringEncryptedSessionRepositoryはSpring Session4.1.1 SessionRepository、SpringWebSessionはSessionを実装し、標準SessionRepositoryFilterへ接続する。汎用Jdbc repository/Java serializationは使わない。HttpSession属性は次の閉projectionだけ。任意field/class名は追加しない。QA049で承認されたversion 2のcompletedAtだけを末尾補足に従って追加する。

| 属性 | Java公開型 | 更新契約 |
|---|---|---|
| principal | SessionPrincipal（認証4fieldの集合） | API認証済み結果だけを内部handlerがsetし、authenticateで即時fixation。HTTP parameter binding禁止。存在するprincipalのnull除去は不可、Logoutはsession invalidate |
| csrfToken | String | 同値setだけ許可。再発行はcreate/fixation/changeSessionId。存在する値のnull除去は禁止 |
| savedRequest | Stringのsafe GET path/query | safe GET validation後にこの属性だけ短transactionで更新。nullは除去 |
| operationTokens | immutable List of SessionOperationToken | 従来snapshot deltaの対象。QA049のissue/require/complete/容量退役は専用current-row短mutateで扱い、完成更新・retired再挿入を旧deltaへ流さない。同UUIDの用途/発行時刻変更拒否、全体最大10、別request変更保持 |

未知readはnull、未知write/型不正は固定診断で拒否。標準SecurityContext/DefaultSavedRequest/例外objectは保存しない。後続SecurityContextRepository/RequestCache/CSRF handlerを閉projectionへ接続する。generic getAttributeの型castはframework contractに必要なmethod一箇所だけのunchecked抑止とし、理由・Test IDを隣接記録する。

create/find/setはlifecycleへ即時委譲、saveも現在hashを再検査し、削除/期限切れは固定障害で新規INSERTしない。Session objectは発行元repositoryにだけsaveできる。private lockで同wrapper snapshotを保護する。setLastAccessedTimeはserver内のInstantをµs化し、lock下のexpiry判定後、現在Clock/既存last/指定時刻の最大へtouchする。外部HTTPから日時をbindしない。setMaxInactiveIntervalは既存確定値と同値だけ許可する。

changeSessionIdは既存principalを維持したrotateとして、fresh Cookie/DB UUID/CSRF、SavedRequest/token移管、旧削除＋新作成を短atomic TXで行う。API認証済み新principalを受けるauthenticateと分け、匿名sessionを認証済みにしない。CookieのSecure/HttpOnly/SameSite=Lax/Path=/、URL ID非使用、8h idleはUI226のまま。Mock Servlet＋実DBのfilter PTはHTTP adapter単体であり、全Security chain/画面/起動/実NK CHRとは別gate。

#### 7.2.6 SecurityContext projectionとfixation専用保存（SSC-044）

EncryptedSessionSecurityContextRepositoryは、先行SessionRepositoryFilterの公開SESSION_REPOSITORY_ATTRが設定済みSpringEncryptedSessionRepositoryと同じinstanceであることを検査し、欠落/別repositoryではnative HttpSessionへfallbackしない。永続化は7.2.1/7.2.5の閉principalだけ。request単位のlazy一回loadから、credential/detailなし・ROLE_USER/ROLE_ADMINのどちらか1個だけの標準認証tokenを作る。未知型/属性/権限・未認証tokenのgrantを拒否し、汎用SecurityContext/認証例外を保存しない。

EncryptedSessionAuthenticationStrategyは既存CSRF sessionとAPI検証済み標準認証を必須にし、principal setで既存authenticateの短transactionを1回実行する。新Cookie/UUID/CSRF、SavedRequest/pending＋consumed token移管を保持し、標準CsrfAuthenticationStrategyのnull-save/追加rotateを重ねない。DB/key/状態故障は固定SessionAuthenticationException、成功HTTPへ進めない。通常saveContextは永続principalと閉認証projectionの一致検査だけで、追加writeや任意grantをしない。空/anonymous保存は匿名/不在sessionでのみno-op、既存認証を黙って消さず不一致として拒否する。LogoutはAPI revoke/queue後の明示session invalidateを先に行う。復元後も毎業務のAPI最新認証と失効済rowの非再生成を維持する。

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

SSC-031: User管理更新では312 §6/332 §12の認証前lock preludeを適用する。非lockingで見つけたcontext ownerは候補に過ぎず、User群昇順lock後にsession ownerをlock下で再照合し、通常verifyと最新ADMIN認可を必ず行う。Raw context/候補IDをログや利用者応答へ出さない。単一transactionの通常verifyによるidle延長とcommand/critical audit/Inboxのatomicityを維持し、事前lookupやWeb roleで認可を代替しない。

| 操作 | USER | ADMIN | API条件 |
|---|:---:|:---:|---|
| Scenario/audio/video/music | ○ | ○ | 有効context |
| 本人質問送信/通知閲覧/取消 | ○ | ○ | notification owner=actor。ADMIN拡張なし |
| 質問回答検索/閲覧/削除 | 本人 | 全利用者 | USER SQLはowner必須、ADMIN handlerだけ全scope |
| Log | × | ○ | role=ADMIN |
| User管理 | × | ○ | role=ADMIN＋自己/active ADMIN保護 |

他人IDはUSERへ404を返し、存在を開示しない。ADMIN URLをUSERが要求した場合は対象に関係なく403。Web表示非表示だけで許可しない。

### 9.3 業務API0102のlocal失効（SSC-048）

検証済API0102を受けたcontrollerはApiSessionInvalidHandlerで終端する。構成済暗号repository marker同一性を確認し、閉actorの表示用投影だけを監査へ使用、WebDisplayContext/CSRF属性とSecurityContextをclearし既存getSession(false)だけinvalidateする。新session/SavedRequest/operation tokenやAPI Logout再送rowは作らない。通常GETは固定302 `/login?session-expired`、POST/HEAD/その他・AJAX・mediaは401共通error、bodyの自動再送は禁止。local DB削除とSESSION_EXPIRED監査後にだけ応答を確定する。DB/属性/監査/response故障は成功扱いせず、既存503境界へ連携する。commit済でもlocal破棄を行うが応答書換不能を伝播する。古いrequestの失効で新Loginの別rowを削除しないことを試験する。業務全controller接続は各program gateで確認する。

## 10. Logout失効再試行

`pending_context_revocations`にはcontext rawをWeb session keyとは別のrevoke queue keyでAES-GCM暗号化し、key version、requested/
next attempt/任意expiry、error codeとSS331既定claim/lease metadataだけを保存する。現在API期限を取得できない場合expires_at=NULLとし、初回Login時刻やrequested_at+8hで補わない。Backoffは5秒、30秒、5分、その後の継続再試行は15分とし、attempt_countは100で飽和するが再試行を打切らない（QA050）。
自動削除は検証済0000/0200の確定失効応答だけとする。一般0102/未知/期限経過/復号不能は保持・固定警告し、有限自動回収を保証しない。復号不能なcontextを捏造して送信せず、正規鍵/状態復旧後の再試行へ引継ぐ。fresh MessageID・元context不変、唯一claim/lease CASとJMS待機中DB解放を守る。残row/borrowerが0になるまで必要な旧revoke鍵を保持する。Table/outbox/logへraw/hashを出さない。
queue登録とlocal row破棄を既存短transactionへ結線し、登録/commit/close失敗でも独立local破棄を試みる。永続再試行または必要なDB削除が未成立なら成功表示せず既定503へ連携する。停止はHTTP drain→retry worker join→replies→外側DB/JMS/keyの順。IT/STで通常業務との混在/残件増大/集中/復帰性能を検証し、問題があれば間隔を変更して同条件で再試験する。試験・調整の記録はSS354のQA050節に従う。

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

## QA-049承認反映：JSON v2・current-row lifecycle（2026-10-03）

### 複数の実表示formの原子的発行（SSC-177）

SCR017等で一画面へ複数の承認済み用途formを出す場合、明示GETで実際に表示するformだけの用途列を既存current-row短mutateへ一度渡し、token群を全確保してから画面へ公開する。用途/null/要素・件数1～10を事前に検査する。保持pending数＋要求form数が10を超えるならUUIDを生成せず現在保持listを不変にして409とする（通常access/version更新は既存mutateのtouchであり業務token変更ではない）。

全確保可能なら、free slotを先に使い、残る新form1件につき最古completedAtのconsumedを1件だけ退役する。同時刻は保存list順、pendingは退役しない。候補UUIDは開始時の全保持UUID（退役候補を含む）と今回候補の両方に衝突しないことを検査し、衝突/時刻不正/保存失敗は全list更新をrollbackして成功公開しない。UUID自動再試行・一部formだけのpending保存はしない。単件issue/require/completeのQA049意味、purpose/issuedAt不変・初回completedAt、API owner/HMACと保存結果検証、入力本文非保存、10件上限・8時間idle/Inbox7日起点を変更しない。DB資源を解放してからAPI/JMSへ接続する。

### 検証済み自己Password resetのlocal終端（SSC-177）

現在ADMIN自身への真正UPW0000/0200はAPIの全session失効を確定した結果であり、0102を受信した事実ではない。callerはfresh IF-020の本人束縛とUSRMUT24 target/versionを確認し、完成印を保存した後、同Spring repository markerに属する現在local sessionだけをinvalidateし、display/security contextを消去して固定Loginへ戻す。API critical監査を正とし、API_SESSION_INVALID/0102監査の捏造、追加LGO送信/再送、別local rowや新Login rowの消去はしない。失敗/未確認commitを成功化せず、既存fatal保持・Cookie終端/503契約を維持する。通常の真正API0102専用terminalは従来のevent/redirect/401を変えない。

同HTTP session内の全用途を合計してpending＋consumedを最大10件とする。用途/UUID/issuedAtは不変で、completedAt欠落はpending、検証済0000/0200を初めて確認した時刻だけを完成印として保存する。完成印を業務結果・認可・API成功proofの代用としない。入力本文・password・payload/HMAC対応入力・業務result snapshotをsessionへ保存しない。

保持中の同token/同入力POSTは現在API認証と既存owner/layout/target/payload HMAC・保存済み結果の検証を経て再操作する。結果GETのrefreshではAPI更新再送を行わない。新formで枠が必要になった場合だけcompletedAtが最古のconsumedを1件退役し、同時刻は保存list順で決定する。pendingを退役しない。全10件pendingなら新form発行を拒否する。退役済み/不在tokenのPOSTは409と明示再GETを要求し、API送信・新UUID発行・自動再操作は0とする。

8時間idleのsession上限、API Inbox7日の保持起点、wire/HMAC/DDL/Current baselineは変更しない。完成時刻から8時間/7日を新たに延長する保証も追加しない。実装・独立PT・nativeの完成認定は別に行う。

current encoderはformatVersion=2を書く。既存認証/CSRF/SavedRequestのallowlist・順序・16KiB/深さ3・strict parserは維持し、operationTokens各要素はpurpose/token/issuedAt必須＋completedAt任意だけとする。completedAt欠落はpending、存在するならcanonical UTC InstantかつissuedAt以上の初回完成時刻。JSON null・未知key・重複key・不正型/UTF-8等は拒否する。v1 decoderは旧3fieldを厳密に読むlegacy pending互換でありcompletedAt混入を許さない。旧3引数constructorもpendingとする。任意object/class名や結果snapshotを追加しない。NKENC1・AES-GCM・AAD・session row DDLは不変更。

issue/require/completeはfresh current-rowを既存短mutateで読み、現在listへ原子的に適用する。完成は検証済0000/0200の受信後、DB/JMSを同時に保持せず、初回だけcompletedAtを書き同tuple/既完成時刻を変更しない。不在/退役tokenをcompleted処理で再挿入せず、古いrequest snapshotで完成をpendingへ巻き戻したり別tokenを消したりしない。issueだけが必要時に最古consumedを1件退役する。現在rowが失効・削除済みなら再生成しない。commit/close不明は成功化せず、次回の現在row再読で確認する。

独立PTは全pending10拒否、pending不退役、consumedのみ必要時1件退役、同時刻順、完成時刻first-write、302応答喪失後同token再操作、退役409/API0/新UUID0、100並行とstale snapshot、v1/v2独立golden・null/未知/破損、commit/close不明、失効row非再生成を含む。旧reader切戻し時のv2失効・再LoginはSS343補足に従う。QA050のpending logout期限NULL/継続retryは別途2026-10-03承認され§10へ反映した。JSON v2のQA049とは独立した実装/PT/IT/ST確認を必要とする。

## QA-050承認反映：API expired rowの内部fence（2026-10-03）

API Logoutで既存の未失効sessionが期限切れの場合、User→sessionの既定lock順で取得した現在状態と取得後の現在時刻を再検証し、EXPIRED/revoked fenceと監査・既定0102 ERROR snapshotを同transactionで確定する。古いnowによる遅延認証の許可や、wireの一般0102を永久失効proofにする変更は行わない。既失効0200は真正保存状態/日時を検証して返す既存経路を守り、Web rowの自動削除は実際に検証済0000/0200を受けた場合だけとする。User lock/業務TOUCH/Logout/cleanup競合、rollback/commit-close不明、expiry±1µs、監査・ERROR snapshotと応答不変更を独立PTし、未実証を実装済みとしない。

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
