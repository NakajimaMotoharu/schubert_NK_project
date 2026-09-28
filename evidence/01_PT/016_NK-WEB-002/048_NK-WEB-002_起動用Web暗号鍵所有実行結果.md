# NK-WEB-002 起動用Web暗号鍵所有実行結果（PG367・暫定）

- 対象source/test/spec: `d77450f43`、branch `dev-foundation`、2026-09-29 JST、Linux x86_64/JDK25.0.4/Maven3.9.12/SpotBugs4.10.4.0/JaCoCo0.8.15。仕様[047](047_NK-WEB-002_起動用Web暗号鍵所有単体テスト仕様書.md)。
- 限定`PT-WEB-NKEY001～004`: 2 suite/5 PT、failure/error/skipped 0、SpotBugs0。`WebNativeCodecs` outer class JaCoCo missed I/B/L/M/C=`0/0/0/0/0`、covered=`150/10/42/7/1`。synthetic current鍵からsession暗号・復号、2 key copyの全消去、別service/閉鎖/null/途中失敗/2 thread closeを確認。初回testCompileのprivate field参照と明示close警告は不合格履歴で合格件数へ算入しない。
- 全6回帰trigger: Web credential/securityの所有境界追加。固定sourceで`./mvnw -o -q -Dmaven.repo.local=<固定m2> -Dnk.pt.repository=<本tree> -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch clean test spotbugs:check jacoco:report`、終了0、365 suite/2,485 PT、failure/error/skipped 0、6 module SpotBugs0。
- 全体coverage missed I/B/L/M/C: Protocol/Storage各`0/0/0/0/0`、Bootstrap`60/37/11/4/0`、API`95/3/32/4/0`、Web`80/1/25/4/0`、Batch`1403/29/306/120/15`。全4指標100%、JS対象、正式53scope・実NK CHRへ加算しない。
- R1/D01・05・06の局所実装であり、`WebProcessMain`の業務runtimeへ未結線。previous rotation/revoke codec、root前段/正式Unit/Broker管理readiness、Login/Log実外部経路は未受入。R2/R3/CHR-A01/L01を完了としない。
- Sanitized manifestは同階層`evidence/provisional/PG367-web-native-codecs/manifest.json`。raw JUnit XML/JaCoCo XMLや秘密実体はGitへ含めず、path順hashで追跡する。
