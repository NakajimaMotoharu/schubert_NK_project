# Web session ID・SavedRequest 境界探索

PG-D-093、PT-WEB-001～008、UI221/226、SS314 §7/352 §3。2026-09-08、dev-web（dev/dee4dd7から作成、検証済dev-admin/dc283b9依存を通常mergeした1d1d239）。既存branch/historyを破壊せず、dev/main未統合、remote push済み。全8件未実装前仕様は90e607f。

探索01: `PT-WEB-boundary-explore-01`、完了2026-09-08 19:09:32 JST、Web新8件全PASS、failure/error/skip0、追加2classのline/method/class/branch100%（clean前の探索計測）、NullAway/format/compile合格。新規障害なし。

command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,WebSessionIdTest,SavedRequestTargetTest test org.jacoco:jacoco-maven-plugin:0.8.15:report`。

raw log `/tmp/PT-WEB-boundary-explore-01.log` SHA-256 `b6e81bf563e4118cbd2f56d76ecf64a415b0a6dd6a30affedc2864d0ecea0a60`。Gitへraw JVM properties/stdout/secretは保存しない。

独立期待: test source内の0/連番/FF 32byte synthetic vectorはPython標準base64.urlsafe_b64encodeとhashlib.sha256で事前算出。Production Java codec/digestからexpectedを生成しない。100個の新規CSPRNG出力は独立JCE計算でも検証。ID/hashは明示accessだけ、toString/例外非露出、公開CSPRNG境界の成功/故障ともbuffer全zero。

SavedRequestは明示文字列比較。GETだけ、relative先頭単一/、UTF8 2048byte以内、query値を保存時にtrim/decodeしない。Scheme/authority/fragment/URI不正/Unicode line separator/dot-segment/encoded path delimiterを拒否し、正常queryのencoded slash/dot/backslash等は保持する。controller route allowlist、Spring security/session repository、CSRF、HTTPとの接続は後続であり本valueを認可grantとして使わない。

正式gateのsourcecommit/日時/OS-JDK-tool/終了code/全coverage/静的解析/Test ID/証跡path/hashはmanifestへ固定する。本8件でNK-WEB-001/PGPT全体/IT/ST完了とはしない。
