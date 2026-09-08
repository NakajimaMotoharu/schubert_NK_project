# Log application探索（PT-ADM-067～073）

NK-ADM-001/NK-MSG-002/NK-AUT-001、FUN-008/AUT-002～003/MQ-006～010/MON-004、UI225/226/232/235/241/242、SS312/314/323 §9.5/324/332/351/352、PG-D-092。Java25/Maven/実PG18/Flyway/Artemis2.56は421の固定toolchain。Synthetic DB/loopback brokerのcomponent PTでIT/STではない。

| run | 完了JST | 結果 | raw log SHA-256 |
|---|---|---|---|
| PT-ADM-log-application-explore-01 | 2026-09-08 18:56:27 | 新7件全PASS、failure/error/skip0。追加10classのline/method/class/branch全100%（探索計測） | 7a69c59ce665c8885617c6d220cec5bffb792e201b83dec11443dbb2c0bf2507 |
| PT-ADM-log-application-explore-02 | 2026-09-08 18:58:02 | 新7件再PASS、failure/error/skip0。無条件の新規検索には再送監査が見え、元の凍結結果へは混入しない独立byte/SQL検査、LOG監査全6fieldの値を追加。追加10class全coverage100% | 88071fa6c9eac55c7d2d0d14f5f388ce7be461242c75489b85fbb024d9eae86f |

command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,LogQueryApplicationServiceTest test org.jacoco:jacoco-maven-plugin:0.8.15:report`。raw logは/tmpに保持し、Gitは秘密値を除いた要約・hashだけ。NettyのJDK Unsafe deprecated warningは既存Artemis経路で、Java compiler warning抑止やPT skipは追加していない。

read-only現在認証/ADMIN/既存Inbox検査またはLog1SQLをcloseし、最終writeで現在identity/ADMIN/owner再確認、DB勝者のInbox/critical監査、commit/close後だけwire/JMS。完了時刻+24h/NONE、0000/0200/9001、非保存0102/0103、同Message条件/owner mismatch恒久拒否、PROCESSING/欠鍵/保存row消失・改変/全JDBC/clock/UUID故障を確認。100同Messageは1初回99再送、100別Messageは100初回、条件/owner競合は50成功50恒久拒否。初回body/expiryはLog変更や再送監査追加で変えない。

oracleは独立UI235のPAGED48/LOG2088/header256（日時/id降順、0/1/100・最終超過page）、手組LP/JCE-HMAC、JCE-AES/Deflater、SQL後条件。実Artemisでsend/ACK/DBfaultを注入しdeliveryCount2、1Inbox、応答property/全body、恒久不一致DLQとqueue drainを確認。Auditは現在verified actorだけ、ROLE_DENIED/SESSION_INVALID/PROTOCOL_REJECTED/INBOX_REPLAYED、LOG target、検索値を含まない閉集合。public null/未知layout/全stage Connection所有、UUIDv4、actor改行redactionを検証。

既存User queryの同じSS段階patternを参考にLog固有の検索/100件/9001契約へ接続。Test fixtureはLog用に独立した公開JDBC境界faultで、Productionのtest専用accessor/reflective private invocationはない。既存testの期待値をLogのProductionから生成しない。新規障害なし、BUG追加不要。

正式clean verifyの対象commit/日時/OS・JDK/tool/command/exit/全coverage/静的解析/Test ID/証跡hashはmanifestへ固定する。探索だけでProgram合格としない。全layout登録・Web session/HTTP/起動・実NK CHR、IT/STは未完了。
