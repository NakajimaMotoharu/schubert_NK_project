# NK-QST-001 受付・Worker接続 実行結果（暫定）

PG419選択v9（01:04:12）42PT（7/9/7/API19）F/E/S0/static4zero/exit0。BUG446/YKT343のInspector全8＋ASUB7/OUTBOX4を同reactorで直接再試験。POMは42.7.13 compile明示、Deployment XPath/固定JVM flags/禁則/versionを全件保持。次Source固定の全6再回帰が必要、選択成功を全正式gateに置換しない。

PG419全6 Source31bf758db初回は00:59:01 exit1、Protocol80/Storage154/Bootstrap210成功、API798中旧Inspector scope XPath1F（BUG446/YKT343先行登録）。API静的/Web/Batchは未実行、full合格加算0。Work pg419-six.log SHA256 **fa51c6f7bda70c9d022d6051c83ea54233158675ceecdf84fb393cb400900930**。PG-D-328の明示compile scope/version/runtime unchangedを独立deployment oracleへ追跡し、選択再試験→新Source全6へ進む。

PG419 v8（00:47:22）：34PT（7/9/7/API11）F/E/S0/static4zero/exit0、log SHA256 **35b83b41c9f19e6b17216104884ef606cd8aae7e120881f8a33e1acc780d4dea**。同変更mainの選択exec累積でSubmission残B/L/M/C33/5/0/0、Owned0/0/0/0。Owned全20 branch/57 line/7 methodはinflight close割込と終了前依存保全を含む。ASUB007 public ctor/Random UUIDv4/late9000/config null、ASUB005 PROCESSING/ERROR/response layout/versionを追加。fresh同source全scope/VM/formalではない。実装file SHA256：Submission **0ed3a8a5202ffa172ac1e5d8937627d277b3d6ea3d0fa37319325eeade69869b**、Owned **95d8d7182e062445c2b9dc0b24af4fe25167d7b424670307da2379bb3b845159**。BUG437～445の直接再試験は成功したが横断full/Worker/既存main負系/YKT341342全閉鎖は保留。

PG419 v7追記（00:42:29）：33PT（7/9/7/API10）F/E/S0/static4zero/exit0、log SHA256 **b2b22c6db037ae68ed9fc2d365eb85ad45c055a8f7d673740a6c44b3e53c3181**。OUTBOX001～004は実専用threadの一時SQL/Runtime再試行、inflight join/二重close/close後wake拒否、Error健康失敗＋固定stderr、割込/自己join拒否を確認。B/L/M/C residualはSubmission35/8/1/0、Owned1/2/0/0。close callerのinflight interruptとpublic ctor/初期化null、Inbox PROCESSING/ERROR/layout/versionの追加probeをv8へ進め、未実行の上積みは合格0。

## PG419 受付＋専用Outbox（2026-10-02）

dev-foundation、base531409a28後の未commit同WIP。Java25.0.4/Maven3.9.12/offlineM2、既存isolated PostgreSQL18/Artemis2.56.0 fixture、OS Linux。Productionはsrcのみ、Current baseline不変更、VM signedPG408/source32c/23SQLへ未配備。

`JAVA_HOME=work/toolchain/jdk-25.0.4 PATH=work/toolchain/node-v24.19.0/bin:... ./mvnw -B -o -Dmaven.repo.local=work/toolchain/m2/repository -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api spotless:apply test-compile jar:test-jar test -Dtest=MessageCodecTest,LinuxInodeSecurityTest,ApiNonSecretConfigTest,QuestionSubmissionServiceTest spotbugs:check jacoco:report`

v6 00:36:45 exit0、29PT=7/9/7/API6、F/E/S0/static4zero。Work log `PG379/pg419-question-selected-v6.log` SHA256 **e0026111d0829bb585a511c215a624b17f2480eb26ce230613a508f4ae28ed3a**。本runは変更fileを保持した選択探索、正式同source全runではない。

| Test | 実際値・独立根拠 |
|---|---|
| ASUB001 | QSB4400 literal→受付atomicDB→別実threadのJMS persistent→QWK320 literal一致→元SENT→QSBRSP0000。M0/新W分離、type ACCEPTED/state RECEIVED、µs DB/17digit JST ms、同/新Message再送0200、保存cipher/completion/expiry不変更、1question/job/work/Inbox、別送信なし。 |
| ASUB002 | pre-admission期限過ぎは9000/DB0、commit後budget切れは9000/COMPLETED・PENDING保持、後送信確認の再送0200。request threadにはwait/JMS中DB connection0。SQL-only SENT fixtureはproof試験でありMQ受入ではない。 |
| ASUB003 | current auth0102、token本文違い0105、同Message違い恒久拒否と監査、Inbox purge後同本文9000/異本文0105・alias/新q/work0。rollback不確定/監査SQL故障は固定一時型。 |
| ASUB004 | open/null/autocommit/readonly/全atomicINSERT/Inbox完了/commit故障で全5表0、close不確定はcommit済受付1だが成功返却なし、rollback故障もlease0/provider text非露出。 |
| ASUB005 | encrypted snapshot破損、work欠落/内容/W/日時/lease/SENT時刻/job owner/correlation/receipt改変は再送成功せず新受付0。 |
| ASUB006 | receipt名UKだけsavepoint再試行、sequenceが1件目1→失敗2→新成功3で独立期待、3collision exhaustion rollback、同寸法reserved不正の実service拒否。 |

API2新主classの残B/L/M/C：QuestionSubmissionService **35/8/1/0**、OwnedOutboxDispatcher **10/20/1/0**（v6、既存coverageを100%と主張しない）。後者のError redaction修正・専用寿命PTはv7で継続中。Worker/質問read/cancel/delete/全31/3consumer/ordinary ready/CHRは未実装又は未接続。

失敗は加算0：compile初回format未適用、v2 compile API単独旧snapshot（BUG437）、selected初回JDBC/JMS同名import（BUG438）、v2 3F3E/µs投影＋error golden（BUG439440）、v3 1F/fixtureがWireMessage constructorで先行拒否（BUG441）、v4 serial compile警告（BUG443）、v5全6PT成功後静的NPE1（BUG444）。retained cleanup/auditはsource review BUG442、子thread default fatal textはBUG445、修正前台帳登録済。

v2失敗log SHA256 **7bb72c06d1bcbd5809b98f37c565e0e89800f88c830a07f8e36565a7b5a749ec**、v3 **74c3bd871a3caf0fef9ea4a628a9575fc515cbec3bc03c95081ddc0c5e220158**。raw SQL/wire/assertion failure/providerログはWorkに留め、Gitへ保存しない。YKT341 µs/Worker投影とYKT342既存main handler回帰は未完範囲を保持。
