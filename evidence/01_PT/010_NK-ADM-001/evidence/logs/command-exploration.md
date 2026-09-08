# User command探索実行（正式gateとは区別）

2026-09-08、dev-admin、作業中source。Java25.0.4/Maven3.9.12/PostgreSQL18.6/JDBC42.7.13/Flyway13.4.0、rootless隔離DB・合成fixture。対象source commitは後続正式manifestで固定する。探索時の未commit状態を正式coverage確定とは扱わない。

共通command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,UserCommandServiceTest test org.jacoco:jacoco-maven-plugin:0.8.15:report`。05のみUserQueryRepositoryTestも追加。

| Run | 終了JST | 終了code／結果 | 独立期待・実際・位置付け |
|---|---|---|---|
| command-01 | 15:37:51 | 0／command6件PASS | 014～019、実SQL/独立JCA PBKDF2、新規User/version/session/audit、lock±1μs/sequence容量・savepoint回復 |
| command-02 | 15:41:49 | 0／command10件PASS | 020～023追加。JDBC途中fault、null/encoder異常/secret消去、100同version＋相互ADMIN＋100別target、監査allowlist/golden24byte |
| command-03 | 15:43:17 | 0／command10件PASS | 防御的DB count/重複row/監査上限/SQL2200H＋close/savepoint故障/conditional0を追加、新規全coverage100% |
| command-04 | 15:44:49 | 1／10件中1失敗 | coverage以外の追加RETURNING ID負例でBUG-045検出。修正前05ac5da起票。合格に算入しない |
| command-05 | 15:46:34 | 0／command10＋query7件PASS | BUG-045修正、RETURNING NULL/0/N12超過・MIN/MAX時刻、同型SELECT UserId例外の横展開再試験。新規全coverage100% |

Failed/flaky/skipped/not-runは合格に含めない。Secret/provider/SQL result dumpなし。正式runまでProgram進捗と確定561件の最新gateを更新しない。

Raw log SHA256（raw実体は/tmpのみ）:

| Run | SHA256 |
|---|---|
| command-01 | f3f1d0800c9e086f3ce6e6ae11a35049d9299f72aec194dea91bc51bd0ff1b0f |
| command-02 | e48235ffa6b2a58545dc333ec6403a699b5c1e32872cfab32a342d8f55ed8265 |
| command-03 | a681cb9f4149305b7e7f9982352972133bad5e01a5f4683b4efe43ead2f12f09 |
| command-04 | 69ccacbdd4e614278d6ff4e5ca3bb1f0ff7d579d49f6112ee2926856a0f648c6 |
| command-05 | e8d3a94e028def365db22ffe1d49faea4bc0ee95ba48c2dca2d75c823144543e |
