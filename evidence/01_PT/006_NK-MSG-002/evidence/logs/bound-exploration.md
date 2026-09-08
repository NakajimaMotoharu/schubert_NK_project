# 保存元Message binding 探索試験

2026-09-08 / NK-MSG-002 / SSC-033 / PG-D-085 / PT-IDEM-B01～B04。

実行command（branch dev-admin、正式対象commitはmanifest）:

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,JdbcInboxCoordinatorTest,JdbcScenarioSnapshotReplacementTest,BoundInboxExecutionTest test org.jacoco:jacoco-maven-plugin:0.8.15:report
```

| run（/tmp rawのみ） | 終了時刻JST/exit | 結果 |
|---|---|---|
| PT-ADM-bound-explore-01 | 16:39:38 / 1 | API18件中1failure: BUG-049の新試験SQL NULL oracle型誤り。合格算入しない |
| PT-ADM-bound-explore-02 | 16:41:33 / 0 | API18件全PASS、Bound/JdbcInboxCoordinator/StoredRow line/method/class/branch missed0。Protocol FieldCodec/Storage OwnedTransferDirectoryは補助実行 |

期待: SS324 §3.1のmagic/LP/fieldCountを独立DataOutputStream＋JCE-HMACで作成。core保存動作の最小空field canonicalを使い、wire/User全field意味はADM024～027の別PTを正とする。24byte bodyはUI236 USRMUT24から手組したliteralで、Production encodeで期待を生成しない。B01は実AES-GCM保存元AADの復号、B03/B04の29byte ciphertextはDB格納だけの合成fixtureであり暗号有効性を主張しない。

初回/再送/100並行source、real23505競合再読、handler1/row1、期限・metadata不変、SQL NULL/誤PK/close/key/HMAC、旧API/read-only1lookup/Scenario replacementを確認。認証ADMIN、User outer replay/header再構築、HTTP/NK実アプリCHR、cleanup BUG-014は未完了。正式clean verify/静的解析/全coverageの結果をmanifestへ別収集する。
