# NK-WEB-002 Web・API実Login縦結線単体テスト仕様書

## 対象・追跡

PG255、PT-SCR-134。`WebLogApplicationRuntime.start`の実HTTP GET/POST `/login`、`MqLoginClient`/`ArtemisRequestSender`、実Artemis、`ApiLogPathApplicationRuntime.startWithLogin`、`LoginInboxService`/`AuthenticationService`/`AuthSessionService`、実PostgreSQL18/Flyway。RD FUN-001、AUT-001～004、MQ-003/006～010、SYS-001/002、UI221/225/226/232/234、SS311/312/313/314/321/323/324/331/332/342/352。Test methodは`WebLogApplicationRuntimeTest#scr134RealHttpLoginUsesProductionApiBrokerAndSession`。CHR-A01/L01への依存を外すためのPG/PT縦結線であり、実NK Characterizationそのものではない。

## Fixture・入力・独立oracle

隔離PG18へProduction Flywayを適用し、`schubert_app`/`schubert_web_session`の分離roleを使用。User `reader`/`USER`、合成password `synthetic-password`のPBKDF2-v1保存hashはPT側JCA `PBKDF2WithHmacSHA256`、salt固定16byte/310000回/256bitで独立生成する。Production `PasswordHasher.encode`をexpected生成に使用しない。実ArtemisのProduction topology/6 Queueを隔離起動し、鍵3種/Web session鍵/Log鍵は合成32byteでcaller所有とする。生鍵・cookie・CSRF・session/context・password・電文本文・DB dumpを証跡へ保存しない。

実HTTP GET `/login`は信頼済proxy headerを付け、status200、title `schubert NK - ログイン`、非空hidden `_csrf`、Secure/HttpOnly session cookieを期待する。GETのcookie/CSRFを同一client内でPOST `/login`へ渡し、formは`username=reader`/合成password/CSRF、UTF-8 URL encodingを使用。POSTは302で`/`へ遷移し、匿名session IDとは異なるSecure/HttpOnly新cookieを返す。新cookieで保護GET `/`が200を返す。独立SQL後条件は`request_inbox` LGNREQ01 COMPLETED/AUTH_SESSION1行、`auth_sessions`非失効1行、`app_logs` LOGIN_SUCCEEDED1行、Web session1行、失敗count0。Production HTTP/JMS/DB値で期待値を作らず、RD/UI/SSのHTTP結果とDDL predicateをoracleとする。

## 観点・完了条件

正常・CSRF/匿名→認証・JMS送受信・API transaction・Web session fixation・null/失敗は既存PT-AUT-INBOX-007～009、PT-SCR-127～133、PT-WEB-084～089/131～157と合わせて追跡する。本caseは新たにWeb/API間の実送受信を1本検証する。Game-context/Log検索handlerは本caseでは起動だけの明示的非利用stubとし、全API readinessを主張しない。選択成功だけで認定せず、source固定の全reactor `clean verify`、Java line/method/class/branch各100%、静的解析0、負canary、全scope/hash照合を要求する。実行command、JDK/tool/commit/時刻、coverage、result、BUG/SSC、sanitized evidence hashは042結果と`evidence/manifest.json`へ記載する。
