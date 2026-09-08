# 管理Log query探索・障害/横展開

PG-D-090/SSC-036、PT-ADM-055～060、dev-admin、2026-09-08 JST、既存Java25/Maven/隔離PostgreSQL18.6/Flyway。Current/利用者data不使用、synthetic app_logsのみ。末尾space拒否・診断levelの表示集合・独立SQL/2088byte期待を明示する。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,LogQueryRepositoryTest,UserQueryRepositoryTest test org.jacoco:jacoco-maven-plugin:0.8.15:report`。探索01～03はUserQueryRepositoryTestを含めない。全て正式clean gateの代替ではない。

| PT-ADM-log-query-explore- | 結果 | 分類 | raw SHA256 |
|---|---|---|---|
| 01 / 18:19:53 | compile失敗、PT未実行 | 新規接続のElapsedMilliseconds(int)へLongを直接渡すmethod referenceとPayloadCodec.encodeの引数不足。Math.toIntExact/既存false overloadへ接続。独立wireのElapsedはN9でなくX9（左詰めspace）とUI232/235に照合 | 32c64ee535e38eb74812d37e9a2d717ebbbbd80577c3fec323594bec70dfb632 |
| 02 / 18:20:56 | 3件中1error、他2PASS | BUG-053：typed X末尾spaceを正常と誤期待。16fdff8起票後、先頭space正常/末尾拒否/空optionalを分離、Production不変更 | 3ce4d53cdbc85f63a492367d98bd1af1639f966eda0a377e0261370e9aa110d8 |
| 03 / 18:22:44 | exit0、3件PASS | ページ/filter/level集合・独立wire・日時境界。negative/並行未完 | acb6dabcb3e84e7b71f2c1c2448791f425b2fb19b8a8e5282dbd4f9f79d19ed3 |
| 04 / 18:24:07 | exit0、Log6＋User7全PASS | SQL/JDBC/NULL/capacity/close/100並行追加、新2class全coverage100% | e85ceec665f2d4ad6d07a653f9ef5f33830a59b948c56a40d821dd2ec63feea7 |

## BUG-052 / YKT-047

compile前reviewでLog CTE/派生tableのSELECT *2箇所を検出しc8b90e6で修正前起票。共通15列の明示projectionへ修正、count/list predicateとsort不変。全Production Java/resourcesのcase-insensitive `select[[:space:]]+\\*`検索は修正後0件。他User/Scenario/Media queryは元から明示列。共有UserQueryFaultsがpublic prepareStatement境界でSELECT */password_hash/context_hash/ciphertext/FOR UPDATEを拒否し、Log055/059/060へ適用。独立2088byteとSQL列投影・optional/NULL後条件を確認。到達不能/coverage除外/suppressionなし。

## BUG-053 / YKT-048

UI232のXは末尾space padding、FieldCodecは原値末尾ASCII spaceを曖昧値として拒否する。Log queryはstrict typed値検査を検索用trimより先に行うため、新PTの末尾space正常期待が誤り。先頭space/NFC/escapeの正常検索、末尾space・全spaceの拒否、Optional欠落/明示emptyの正常を分離。UserQueryRequest040/042とMediaRequestはwire decode済みで末尾paddingを有効値に含めない。既存UserQueryRepositoryは内部trim-firstの別API契約を持ち、その内部fixtureの末尾spaceを一律拒否へ変更しない。HTTP/form入力のtrimは後続Web境界で別確認する。共通FieldCodecおよびUser/Scenario/Media既存PTを正式非回帰に含める。共有fault helperはtyped getObject(String,Class)にも同じ列差替えを適用するだけで、DB/oracle代替や秘密値出力を追加しない。

実行ログは/tmpだけ、Gitにはsanitized要約/hashと正式PASSのJUnit method/timing/counterだけ保存する。PGPT Program完了、Log request/replay/外側transaction/HTTP・実NK CHRの完了を宣言しない。
