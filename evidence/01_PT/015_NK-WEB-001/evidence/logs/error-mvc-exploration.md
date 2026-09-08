# 共通error・内部dispatch探索記録

正式認定: 未実施。探索成功をProgram完了へ算入しない。正式全回帰後にsource/日時/coverageを追記する。

NK-WEB-001/SCR-090、PT-WEB-148～157、PG-D-116、SSC-047、BUG-074/YKT-066。関連FUN-001/002/AUT-001～004/TST-001～005/MON-004、UI221/222/226、SS313/314/351/352。toolchainは421 §5.9～5.10、独立期待・fixtureは001 §14.12。

| Run | 終了日時（JST） | 結果 | 非格納raw log SHA-256 |
|---|---|---|---|
| error-20260909-explore-01 | 2026-09-09 02:44:24 | exit1。PT156内部ERRORでterminal期待1/実際0。BUG-074起票後、修正前の再現失敗。合格へ算入しない | 78750e19d3a1a0cc0dcf46bef541b3a409013ed15446c823cf7b2218a4148362 |
| error-20260909-explore-02 | 2026-09-09 02:49:03 | exit0。PT156修正後成功、関連既存25件を含むWeb26/Protocol5/Storage16 PASS | 767921f9d75bb88008160cf29d68985aa0a10341bbaad3d69481e581aff36268 |
| error-20260909-explore-03 | 2026-09-09 02:53:16 | exit0。先行5件＋既存25件でWeb30 PASS、静的解析0。全新規試験追加前で正式coverage判定なし | c85c2ffe14c86c0120db6f75a31a14f592a14e2385aa88c2416b34bf460e9364 |
| error-20260909-explore-04 | 2026-09-09 02:58:10 | exit0。新10件＋既存25件でWeb35/Protocol5/Storage16 PASS、追加classのline/method/class/branch100%、NullAway/format/Enforcer PASS、SpotBugs0 | ec0d1a10c226da138f971541c8177cdc58f86b3c6b483107ffb0164509dab87c |
| error-20260909-explore-05 | 2026-09-09 03:01:37 | exit0。実HTTP TRACK拒否後の共通400をPT155へ追加し、同35/5/16 PASS、failed/error/skipped0、静的解析0 | b461e3c5d9db25f8b08a80fd69f91018dd18c9e56cb2fc15dcbb679fb7ebd3b3 |

最新command（repo root、JAVA_HOMEは421のJDK25.0.4）:

```text
./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=ErrorMvcTest,MenuMvcTest,WebSecurityChainTest,WebRequestSecurityTest,EmbeddedWebSecurityTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

01/02はPT156のみ（02は関連既存25件併行）、test goalまで。03はPT148/149/150/151/156を選択。rawログはGitへ保存せず、再現はTest IDと上記selectorから行う。探索JaCoCoは累積し得るため、正式clean verifyを別途要求する。

BUG-074はrelease sourceのFilterChainProxyがchain選択前にStrictHttpFirewallを呼ぶことが原因。error用SecurityFilterChainを追加するだけでは元TRACEの拒否が繰り返される。Caddy/header/UUID検証後、実DispatcherType.ERRORかつexact /errorのみInternalErrorDispatchRouterから非業務error filterへ分岐する。通常要求・他dispatcher・ERROR別pathは従来単一business chainとfirewall/CSRF/roleを維持する。外部の偽dispatcher header/queryでは分岐できない。routerの初期化失敗時の両filter終了、終了例外時の他filter解放、全終了でThreadLocal clearも試験した。

DB故障がsnapshot前なら匿名表示、snapshot後なら表示用username/roleと解決済CSRFだけを使う。CSRF拒否は先行handlerで既存値のみsnapshotする。rendererはDB/JMS/HttpSession/native principal/例外/message/元URI/queryへアクセスしない。全固定statusの日本語messageを独立Map/DOMで照合し、100並行でactor/role/CSRF/UUIDの混入0、native session0、秘密canary非表示を確認した。実Tomcatのerror MVCを使用するがLogin GETはfixtureであり、Logout、全画面、runtime bootstrap、実NK Characterization、IT/ST完了を意味しない。

証跡はTest ID・counter・coverage・hashのみ。raw session/cookie/token/password/context/鍵/DB dump/JVM出力は格納しない。
