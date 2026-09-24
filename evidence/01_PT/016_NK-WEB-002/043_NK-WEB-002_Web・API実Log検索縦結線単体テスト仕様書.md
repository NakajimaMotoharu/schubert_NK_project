# NK-WEB-002 Web・API実Log検索縦結線単体テスト仕様書

PG257 / PT-SCR-135。対象は`WebLogApplicationRuntimeTest#scr135RealHttpAdminLogSearchUsesProductionApiBroker`とProduction `WebLogApplicationRuntime`→`LogSearchWireClient`→Artemis→`ApiLogPathApplicationRuntime.startWithLoginAndLog`→`LogQueryApplicationService`。RD FUN-001/008、AUT-001/002/004、MQ-003/006～010、UI221/225/226/232/235、SS311～314/321/323/324/331/332/342/351/352。Test IDはJUnit method、016/evidence manifest、本書で一意に追跡する。

事前条件: 隔離PostgreSQL18/Flyway全migration・実Artemis、合成ADMIN1名と独立JCA PBKDF2 hash、caller所有codec、実HTTP server。ログインGETで200/title `schubert NK - ログイン`/非空CSRF/Secure・HttpOnly匿名cookie、POSTで302 `/`/認証cookie rotationを期待する。認証後、独立SQLで`app_logs`へ`action=PTSCR135`、`message=synthetic log result`の合成1行を投入する。

操作: 認証cookie付きGET `/logs?action=PTSCR135`。独立期待値はstatus200、DOM `.log-row`ちょうど1件、その行のactionとmessageが投入literalに一致し、`request_inbox`の`LGSREQ01`完成行が1行、Logの`PTSCR135`行が1行、API/Web双方ready・terminal0。期待値はProduction query/codec/controllerを呼んで生成せず、UI235の画面値とDDL/SQL後条件を使用する。正常/ADMIN権限/CSRF/cookie/DB-JMS連結を本caseで確認し、USER拒否・境界・null・再送/並行/例外は既存PT-SCR-093～104、PT-ADM-067～076、PT-AUT-INBOX-007～009が担当する。Game-contextは非呼出し明示stubで、全process入口・実NK CHR-L01/A01を本caseで完了扱いしない。

選択command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node -pl src/schubert-nk-web -Dtest=WebLogApplicationRuntimeTest test`。正式runの環境/branch/source commit/command/終了code/coverage、入力/期待/実際、BUG/SSC、sanitized evidence path/hashは016/evidence manifestと044結果に記録する。failed/flaky/skipped/not-runは合格に算入しない。
