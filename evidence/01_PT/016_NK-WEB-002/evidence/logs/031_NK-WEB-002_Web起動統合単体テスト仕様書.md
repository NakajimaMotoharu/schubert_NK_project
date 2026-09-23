# NK-WEB-002 Web起動統合単体テスト仕様書

PG222、RD SYS-001/002/004・AUT-001・MQ-001/002・TST-001～005、UI211/212/226/252、SS311 §5・314・321 §4・342 §4・352・362。対象 `WebApplication.start`。技術的DB/JMS接続確認、暗号化session repository、承認済みsecurity chain、loopback HTTP/MVCをこの順で接続する。外部credential/keyの取得、API business listener、Queue実在・実効設定management gate、実NK CHR-A01/L01は別未完了。codec/DataSource/provider/監査/JMS factoryの所有権はcallerに残し、起動されたHTTP serverだけを戻す。

| Test ID | fixture・入力/操作 | 独立期待値 |
|---|---|---|
| PT-SCR-117 | 隔離PostgreSQL18/Flyway Web role・SS321 embedded Artemis・test専用AES key、固定audit/ID、実Tomcat、trusted Caddy転送headerでGET `/login` | DB/JMS probe成功後に127.0.0.1でHTTP起動。status200、HTML title `schubert NK - ログイン`、CSRF hidden fieldとSS314指定の`SCHUBERT_NK_SESSION` cookieを生成。forwarded headerなしの直アクセスは403。DB session行あり。画面期待値はUI226/QA-045固定値、DB期待値はDDLから独立算出 |
| PT-SCR-118 | DB接続拒否または停止broker、使用可能runtime path/port。`start` | redacted固定 `WebStartupException`、依存に到達する前/後の順序を明示、HTTP bind前失敗でportが未listen。provider秘密本文、key、raw sessionを例外へ出さない |
| PT-SCR-119 | null各依存、非directory path、不正port/feature configuration、閉鎖後のserver | null/不正引数はfail-fast。無効起動でDB/JMSに触れない。HTTPを閉じた後は再利用不可。secretはtest/evidenceに保持しない |

実行command、OS/JDK/tool version、branch/source commit、exit、coverage、結果、関連障害、証跡path/hashは正式run後の032とsanitized manifestに記録。failed/error/skipped/flakyをPASSへ算入しない。4指標coverage・静的解析・全41scopeを正式gateで確認する。これはWebの限定的production composition PTであり、Production起動全体やIT/ST完了を宣言しない。
