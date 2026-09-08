# User照会application PG/PT探索

PG-D-089/PT-ADM-048～054、dev-admin、2026-09-08 JST。実PG/Flyway、既存toolchain、合成fixtureのみ。正式合格はroot clean verifyとmanifest採取後に確定する。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,UserQueryApplicationServiceTest test org.jacoco:jacoco-maven-plugin:0.8.15:report`

| PT-ADM-query-application-explore- | 結果 | 分類 | raw log SHA256 |
|---|---|---|---|
| 01 / 17:58:18 | testCompile失敗、PT未実行 | 新fixture helper実名inboxMetadata/戻りListの呼出し誤りを訂正。未到達SQL fixture列名も既存response_versionへ照合。Production/期待値不変更 | 0af6b06563056ca8836503c75c4f6334d645fc1bfa0165d2583370c061fa6a15 |
| 02 / 17:59:05 | testCompile失敗、PT未実行 | 新test service factoryのContextHash checked exception宣言不足、test wiring訂正 | 010621c19e79eecb1c93138c8fa6efb6f2ab1ef3c3cb2f43e89cf78516925fb6 |
| 03 / 18:00:10 | exit0、初期3件PASS | ADM048/049/054初期assert。正常/凍結再送/24h/権限変更とstage所有確認、残4件は未実施 | fba7eb62a6979943eaf25cd85aee7fc72e7d3032865f849c66c2b4067491b50a |
| 04 / 18:02:38 | testCompile失敗、PT未実行 | negative追加時、前formatterが未使用として削除したtest例外importを追加。初回test wiring | 26acbe9f5985b7630b4cf0a3a4269abdba17c4d80f9c02f70a71c39941f2b4c2 |
| 05 / 18:03:26 | exit0、6件PASS | DB/SQL/commit/close/rollback/clock/ID/key故障、100同Message/100別Message/100異query/100別owner、保存row消失・改変追加。実JMSはまだ未実施 | bb81cb3430bc8c08613254a5f09252b1f2eee3c5082849940fb96e794e14508a |
| 06 / 18:04:57 | exit0、7件PASS | 実Artemis send/commit/DB故障と再配送count2、凍結body/元expiry/1Inbox、DLQ/queue drain追加 | a7da365d9c2f713cef4a16df956332a2a47ee8dd456881126f7c16736912534c |
| 07 / 18:05:51 | exit0、7件PASS、新Production全coverage100% | 初段否認→最終ADMINへ回復しても無query結果で許可しない負例、否認監査actor/allowlist/control除外追加。新10classの全counter100%、除外/抑制なし | cf1fec3da23d584665173b6317e2e9cc2fede8c95345dfe712d3d301adbcbd15 |

上記compile未到達は初回test wiringとして記録し、合格へ算入しない。実装済みProductionの仕様違反はこの探索では検出していない。DBのcompleted_at/expiryと独立JCE復号body、query canonicalの手組LP/JCE-HMAC対DB値を照合する。Raw provider/JMS出力は/tmpのみ、Gitにproperties/stdout/session/context/credential/password/DB dumpを保存しない。全体dispatcher・Web/HTTP・起動・実NK Characterizationは残task。
