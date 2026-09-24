# NK-OPS-001 Web/API service unit単体テスト仕様書

Program `NK-OPS-001`、PG269、配備source `src/deployment/systemd/schubert-nk-{api,web}.service.template`、PT class `ApplicationServiceUnitTest`。RD SYS-002/004・OPS-009、UI212/225/231/251/253、SS311/313/321/342 §4～5・343 §2/6。対象はunitの依存順・非秘密環境・credential分離・資源上限・hardening・構文であり、Java main、全ready、実systemd起動は対象外。

| Test ID / method | 事前条件・入力・操作 | Productionと独立した期待値 |
|---|---|---|
| PT-OPS-SVC-001 / `apiDependencyCredentialAndResourceContract` | repositoryのAPI templateを読取り、全必須directiveを照合 | SS342 §4.1/4.2/5.1のexpiry→API、API 2048M/Xms512m/Xmx1024m/Direct256m/Meta256m/停止60s。343 §2/6の専用API UID/GID、transferのみwrite、DB/MQ/API AES/HMAC currentだけ5秘密。Web/session秘密なし |
| PT-OPS-SVC-002 / `webDependencyCredentialAndResourceContract` | Web templateを同様に読取り | API→Web、1536M/Xms384m/Xmx768m/Direct128m/Meta192m/停止30s。Web専用UID/GID・DB/MQ/Web AES currentだけ5秘密。assets/transferへwrite不可、API/HMAC秘密なし |
| PT-OPS-SVC-003 / `noSecretInEnvironmentOrShellAndNoAutomaticWritableEscalation` | 両unitの非comment全行を検査 | `Environment=`/shell/SetCredential/PassEnvironment/特権ExecStartなし、LoadCredential各5、ProtectSystem=strict、ProtectHome/NoNewPrivileges、SendSIGKILL=no、AF_UNIX/INET/INET6だけ。credential実値はfixtureにも証跡にも存在しない |
| PT-OPS-SVC-004 / `renderedSyntaxIsAcceptedWithoutStartingService` | isolated tempへunitを`.service`でrender、ExecStartをtest-only `/bin/true`へ置換し必要依存unitをtest-only作成、`systemd-analyze verify --man=no` | exit0・stdout/stderr空。OS managerへinstall/startしない。実ExecStartの起動可能性は未合格 |

各Testは正常・欠落/余分directive・cross-service credential・秘密環境・shell・権限逸脱の拒否を文字列/全行/件数で検査する。nullはfile読取失敗としてJUnit異常終了し、成功に数えない。外部並行起動、再送はunit契約の外で、SS321/324・既存PTへ追跡する。独立oracleはSS342/343の固定値をTest内に明記し、unit本文からexpectedを生成しない。選択command: JDK25/Maven3.9.12 `./mvnw -o -pl src/schubert-nk-api -Dtest=ApplicationServiceUnitTest test`（登録offline repository/JDK/PATHを使用）。実行日時/OS/tool/branch/commit/正式command/exit、失敗・skipped、coverage、input/expected/actual、関連BUG/SSC、sanitized file hashは057と`evidence/manifest.json`へ記録する。TemplateのみでPG/PT完成としない。
