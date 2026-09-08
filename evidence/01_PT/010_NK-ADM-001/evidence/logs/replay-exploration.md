# User更新暗号replay 探索記録

2026-09-08 / dev-admin / PG-D-086 / PT-ADM-028～032。Java25.0.4/Maven3.9.12、合成fixtureのみ。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,UserMutationReplayServiceTest,UserMutationRequestTest test org.jacoco:jacoco-maven-plugin:0.8.15:report
```

| Run（raw /tmpのみ） | 終了JST/exit | 結果・hash |
|---|---|---|
| PT-ADM-replay-explore-01 | 16:54:12 / 0 | replay5/request4全PASS。header総長の重複assert branch1missedで正式認定しない。SHA256 d0477d81c84a7021916f5a54b2be7ec46b0f3f4de160552afc9d3316d7ebad11 |
| PT-ADM-replay-explore-02 | 16:55:50 / 0 | replay5/request4全PASS。既存HeaderCodecのregistry/総長invariantへ責務を一意化し、実body280byte checkは維持。新service/Snapshot/request全counter missed0。SHA256 a90ae487581d88e5648913342f8cf8a2ad7ac22221485dfbfba72213d24bd5d0 |

期待はUI232の0-based header offsetとUI236 USRMUT24の独立配列、明示JST時刻・target/version、SS352の独立LP/AES-GCM/Deflaterで生成。Production header/payload/crypto encoderをexpected算出には使用しない。暗号認証が有効な異常header/bodyも独立JCEで作り整合拒否を確認する。テストの固定nonce/zero鍵は合成vector専用でProduction暗号のnonce生成は変更しない。

全5layout/7mutation、初回0000・unlock0200、同Message/別Message同tokenの成功0200、確定error原code、Transient0102/0103/9000の非保存、target/ref/N9版/時刻/state/layout整合、key/cipher/AAD改ざん、NULL/closed/USER/別owner/request scope、100並行を確認。279/281byte、DATA/record/count/total length改変を全て拒否し、coverage除外やguard弱化はない。

DB/User現在versionの実更新後replay、現在ADMIN否認監査、実Inbox/JMS/HTTP登録は後続。正式source commit・実行日時・終了code・全module PT/coverage/static結果・sanitized JUnit/hashはmanifestで固定し、この探索logだけでProgram完了とはしない。
