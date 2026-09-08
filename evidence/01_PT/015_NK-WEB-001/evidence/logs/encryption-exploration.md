# Session暗号探索記録

2026-09-08 JST、dev-web、SSC-039/PG-D-095/PT-WEB-016～023。先行SSC起票3c56af3、SS/PT仕様5f5c25d。JDK25.0.4/Maven3.9.12/Gson2.14.0/JaCoCo0.8.15、他環境は正式manifest/421参照。値はすべて合成fixtureで、key/nonce/raw属性/ciphertext/JSON入力やprovider診断をこの証跡へ転記しない。

## 探索結果

| run | 終了JST | exit/結果 | raw log SHA256（/tmp、Gitへ格納しない） |
|---|---|---|---|
| PT-WEB-crypto-compile-01 | 19:42:28 | 0、Production compile/NullAway PASS | 26fff66c319fd86e38d89c1ca978fb1a59d1b1d7150a2fb3bace1e1707f28a70 |
| PT-WEB-crypto-explore-01 | 19:45:36 | 1、新規PT初回接続のtestCompileでexplicit close＋try-resourceの-Xlint warning。8件未実行、合格算入0 | c1633869be8c91b31643c07408816bcb3197ceb0214bed0a96243ee5adeb34e0 |
| PT-WEB-crypto-explore-02 | 19:46:27 | 0、closeを意図的に競合させるfixtureの所有権を明示finallyに修正。既存属性7件＋新暗号8件PASS、failed/error/skipped0 | b0d352903e396582f632c85d54629c6d788cb51ae2bf9845fa4ea9a84de13d5e |

新規5class（Reason enumを含む）のline/method/class/branch missed0。累積探索coverageなので正式clean verifyで再確定する。初回未接続PTのresource宣言修正であり製品挙動/期待値の変更なし、新BUGなし。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=SessionPayloadCodecTest,SessionAttributeCodecTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report
```

## 独立oracle・review

SSC039の7field順序をDataOutputStreamで手組し、UUID bytesは固定hex、created_at secondsは独立JavaScript Date計算1788825600＋nano123456000を使用。JSONはPT009～015の手書きhelper（Production encodeなし）。JCEによる独立AES-GCM全文byte比較。各AADfield/PK/hash/created_at、envelope/nonce/tag/body、current/previous/unknown、DB内包versionを個々に変異させ認証拒否をassert。認証済みでも不正JSON/UTF8/最大byte超過を拒否する。

全public null/不正設定/immutable copy、provider復旧finally、100並行nonce/属性、公開this monitorとの独立、latchで進行中暗号とclose順序を確認。Nonce一時arrayは注入CSPRNGの公開出力bufferでzeroを観測。所有key copyのclose時zero fillはsource reviewとclose後fail-closed/restart別instanceの契約PTで確認し、private field reflectionやcoverage除外を使わない。constructorは全設定検証後にkey copy、private final lock、provider/schema診断cause/suppressed保持なし。API/WebLog/revokeと暗号keyを共有する経路なし。

## 正式gate・残件

正式PT-WEB-20260908-03、source3bb7319839395b14ba87b9e2e96daedcfda4be15、19:47:46～19:52:00 JST、exit0。全648件（Protocol80/Storage34/API394/Web99/CHR41）、暗号8件を含むWeb23件PASS。全5対象moduleのline/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。SSC-039完了、新BUGなし。詳細とhashは正式manifest/002/checksums。DB repository/失効・current再保存/CSRF/HTTP/実NK CHRは未完了。暗号部品の合格をProgram完了やIT/ST完了へ換算しない。
