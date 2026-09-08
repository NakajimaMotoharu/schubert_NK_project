# Session technical store探索・列数是正

2026-09-08 JST、dev-web、SSC-040/PG-D-096/PT-WEB-024～031、BUG-056/YKT-051。JDK25.0.4/Maven3.9.12/PostgreSQL18.6/JDBC42.7.13/Flyway13.4.0/JaCoCo0.8.15。Production roles/migrationsで隔離した合成DBだけを使用、master/実session/raw JSON/DB dumpなし。

## 障害先行登録と横展開

e1bcbecで修正前起票。新規説明の列数を誤って10と数えたが、331/V003の実列はid/hash/ciphertext/key/created/last/expiry/TTL/versionの9列。SS314 §7.2.3、441 PG-D-096、PT024/030の全誤記を9列へ訂正。実DDLおよびProductionの明示COLUMNSは当初から9列のため変更しない。`rg '10列'`でこの3文書中のsession誤記残存0、`web_http_sessions`の全Production SQLを確認。cleanup側は列数の全件投影をせずid predicateであり非該当、331/V003は正しいため非修正。

再発防止はPT024の実ResultSet metadata9＋固定列名集合/明示SQL一致、PT030の全9列NULL拒否。PT025はcipher/key/last/expiry/TTL/versionすべて変更して独立値を照合し、PK/hash/created predicateを各々誤らせ0件を確認。検索だけでYKT完了にせず正式全reactorで再試験する。

## 探索結果

| run | 終了JST | exit/結果 | raw log SHA256（/tmpのみ保持） |
|---|---|---|---|
| PT-WEB-store-compile-01 | 19:56:30 | 0、compile/NullAway PASS | 7cc29da0d6ee393152b473a01aebf7bb61afbef776fafcefe2feddfd001b15b3 |
| PT-WEB-store-explore-01 | 20:00:35 | 0、新8件PASS。ただしbranch missed2で品質gate非合格 | 396e01423785ca9cad2fe3722f2bf74dbd065e84aa2c342d0d09a532a1fa0acd |
| PT-WEB-store-explore-02 | 20:02:06 | 0、新8件PASS、新3class全coverage100% | 9cf3f00ba66206dddad09f1da3478d8685fb66ac0cb5b31d64ba805304e44189 |
| PT-WEB-store-explore-03 | 20:02:58 | 0、全更新列/identity predicate確認を補強、新8件PASS、新3class全coverage100% | 1c3327dad04b5ab1490e3845f4f86b5799e13e3f6482fcf03b8db432e0f0e488 |

探索01のmissedはfindLockedの二つのreturnに複製されたjavac try-resource close null guard（javap確認）。Optionalのsingle-return構造へ整理し、行あり/なし双方のResultSet/Statement close故障を独立追加した。実処理/期待値を変更せず、除外設定・suppression・private reflection・到達不能合格扱いなし。JDBCがnull resourceを返す負例も維持する。探索coverageは累積のため正式clean verifyが最終判定。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=JdbcWebSessionStoreTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report
```

新規/更新/削除rollback、原子的old-delete/new-insert、同一PK/hashの制約、stale CAS false/削除後再生成なし、Web業務schema42501、全DDL bounds、全null/時刻精度を確認。公開JDBC proxyで接続設定/prepare/全bind/query/update/各getter/close/null resource/SQL NULL/不正row/更新数/重複を注入し、固定例外cause/suppressed0とConnection caller所有をassert。100 row-lock更新後version100、競合CASの1勝者で101、削除後のstale update0件。

## 正式gate・残件

予定PT-WEB-20260908-04。source/開始終了/全件数/coverage/静的解析/hashを正式manifest/002へ確定後記録。低位ciphertext storeであり、暗号/lifecycle接続・期限失効・dirty属性merge・CSRF/HTTP/起動/実NK CHRは未完了。IT/ST完了とはしない。
