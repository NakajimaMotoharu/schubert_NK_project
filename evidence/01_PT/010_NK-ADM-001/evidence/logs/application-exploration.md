# 管理更新transaction接続 探索記録

2026-09-08 / dev-admin / PG-D-087 / SSC-031/034 / PT-ADM-033～039。

Java25.0.4/Maven3.9.12、実隔離PostgreSQL18.6/Flyway/grants・Artemis2.56.0、合成fixtureのみ。Production外側service追加とPTを並行開発。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,UserMutationApplicationServiceTest,AdminCommandAuthenticatorTest,UserCommandServiceTest test org.jacoco:jacoco-maven-plugin:0.8.15:report
```

| Run（raw /tmpのみ） | 終了JST/exit | 結果・raw SHA256 |
|---|---|---|
| PT-ADM-application-explore-01 | 17:09:32 / 1 | 新PT033/034/037の3件、1failure。新fixtureで既存independentHash(stored,password)の引数を逆順に渡した初期配線誤り。順を訂正、期待hash算法やProduction変更なし。未完了TDD fixtureの失敗、合格算入なし。ca9c58659f4a3622e1cccbece1ca0927b869fbba6cce3d66fc68121781da9a4c |
| PT-ADM-application-explore-02 | 17:12:14 / 0 | 新PT033～037の5件PASS。100同token/同Message、20別token版競合、別owner同token、相互ADMIN4組、DB/監査/crypto/commit/rollback/close/clock/ID fault。0261ddf20db8460f04c7a533b95660a20bbdc5878936d5709e1e0b136a6ace52 |
| PT-ADM-application-explore-03 | 17:18:15 / 0 | 新7件＋prelude6＋command10＝23件全PASS。新application/auditと既存変更classの全coverage counter missed0。実JMS send/ACK/DB fault、再配送更新1回、Message不一致DLQ/critical監査、独立全5layout HMAC・SQL/PBKDF2/280byte/監査allowlist。8ffea04329650cda1401a30e3827fa70dec7a587b6a8c2eaf170017e39a47ff1 |

Expectation: UI232/236の手組wire、SS324 LP/HMACのtest側DataOutputStream/JCE、DB後条件のcount/version/role/status/revoked/監査/7日保持。Password hashは保存saltから独立JCA再計算、Production methodをexpectedに使わない。後続の別commandで実DB版が進んでも元操作versionの0200を確認。初回crypto/commit前故障は全rollback、commit後close/返信ID・clock故障も成功応答せず、次配送で保存結果を再構築する。

危険値はテスト入力としてのみ使用。JDBC/rollback/closeのprovider文言、password/operation token/context/HMAC/暗号byteは報告に出さず、collectorは成功JUnitのclass/method/時間/counterだけを収集する。Raw provider/JMSログと一時DBはGitへ保存しない。

本探索ではProductionが承認済み期待に違反する障害は検出していない。正式root clean verify/全module coverage/static/trace/hash/secret scanを別実行し、manifestのsource commitへ固定してからSSC-031/034の当該接続を完了する。HTTP/全layout起動登録/実NK CHR/PGPT全体/IT/STの完了ではない。
