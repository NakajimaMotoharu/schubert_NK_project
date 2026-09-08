# UserMutationRequest探索実行

2026-09-08 dev-admin、Java25.0.4/Maven3.9.12/PostgreSQL18.6/JDBC42.7.13/Flyway13.4.0、隔離実DBと合成fixtureのみ。未commit作業中source。正式対象commitは後続manifestで固定する。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,UserMutationRequestTest test org.jacoco:jacoco-maven-plugin:0.8.15:report`。

| Run | 終了JST | 終了code/結果 | 原因・独立期待・実際 |
|---|---|---|---|
| request-01 | 16:13:54 | 1／testCompile失敗、request試験未実施 | 初期TDDのtestにTWR内explicit close warning。Production不変更、手動finally所有のtest scopeへ直しwarning抑止なし |
| request-02 | 16:15:16 | 1／4件中2error、failure/skip0 | BUG-048の誤った有効wire oracle。UI236を根拠に修正前起票、code/goldenは不変更 |
| request-03 | 16:18:20 | 0／4件PASS | 5layout/7kind/N12/N9/role-B独立・手組LP/JCE-HMAC、case/key拘束、実PG dispatchとDB依存0100、strict wire/close/100独立並行。新規全coverage100% |
| request-04 | 16:20:54 | 0／4件PASS | read-only DB失敗とsecret clone/所有配列zeroの独立観測を追加。新規全coverage100%。正式gate待ち |

期待値はUI236のoffset、SS323 §9.3の順序/型/targetから手組み、SQL後条件、独立JCE HMAC/PBKDF2。Productionのcanonicalやencodeをexpected生成には使わない。failed/flaky/skipped/not-runはPASSへ含めない。

| Run | /tmp raw log SHA256（raw実体はGitへ保存しない） |
|---|---|
| request-01 | a6a7f8bab75e62fef3700cf19a03113ebe600c2e9443ed5bfc0ae2149e3cc8e8 |
| request-02 | 6367c338db5d2e4de9aa146a2ef9b58671a90b9b636e7286f5d43bc87b204edb |
| request-03 | 0fcc1dd31a10fa1a4a9a55c537b57e04cd8d8dea0fe044166c0a9b3838b7c73c |
| request-04 | 48261ba3a984384ed4efcbaec677eec182b395f7ac07320a4961bb4db80a2fa9 |
