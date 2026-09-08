# PT-QUALITY-003/004/005 正式検証

- Run: PT-IDEM-20260907-05 / branch dev-messaging / target 8350b519f3c251f1c52266707d49efea5968f962
- 2026-09-07 22:52:37～22:54:33 JST、root clean verify exit0。OS/JDK/Maven/commandはmanifestとrun-summary参照。
- RequireJavaVersion / RequireMavenVersion PASS。DependencyConvergenceは親、CHR、Protocol、API、Webの全5 reactor PASS。
- SpotlessはCHR12、Protocol178、API83、Web33＝306 fileを実検査。変更必要0、cacheによる省略0。後続batchはまだ存在せず合格件数に含めない。
- 機械整形185 file。機能差分はgeneratorが既存semantic呼出しを再現する修正だけであり、production semantic・Current baseline・固定長goldenは不変。
- generation-results.json: 69 named record＋catalog1＝70 file一致、隔離catalogへの1行追加を差分1件として検出、production/fixture/SS不変。
- null-canary-results.json: positive compile0、negative compile1で4件の意図したNullAway違反検出。意図した負fixtureはproductionでも成功PT件数でもない。
- Protocol69/API105/Web48/CHR41＝263全成功。4指標coverage100%、SpotBugs0。BUG-017/018/019、YKT-014/015/016の直接再試験範囲。PGPT全体完了ではない。
- raw log SHA-256: fd277f6129452c320a669bb374e280afc9395e04ea36840490e3a46fcddaecf9。raw stdout、JVM properties、fixture secret値を転記しない。
