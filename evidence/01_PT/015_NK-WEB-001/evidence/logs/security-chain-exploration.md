# 単一security chain探索・BUG-073再現記録

Program NK-WEB-001、PT-WEB-131～141、PG-D-113/114、BUG-073/YKT-065。OS/JDK/toolchainは421、独立fixtureと期待値は本Program単体テスト仕様書を参照する。以下は正式clean gate前の探索であり、Program完了/本番起動/IT/STの証跡とはしない。

| Run | 終了日時（JST） | 結果 | 非格納raw log SHA-256 |
|---|---|---|---|
| security-chain-20260909-explore-01 | 2026-09-09 01:48:35 | Web新6＋既存HTTP4 PASS。ただしSavedRequest消費/Servlet Principal後条件の欠落があり、合成完成とは認定しない | 8074345c1743491321c021a9571bde3ca70ffa06d7c2f11d5510b3a5876c4e1b |
| security-chain-20260909-explore-02 | 2026-09-09 01:54:50 | exit1、Web7中PT132/137が仕様不適合を再現。期待: 一致GET後SavedRequestなし/認証後Principal reader。実際: 保存GETが残存/ANONYMOUS。修正前にBUG-073起票済 | 6e3c5c1ba16d560c06e7fc476061e07c9207111a4bfe018975dd429fb0d1e286 |
| security-chain-20260909-explore-03 | 2026-09-09 02:07:29 | exit0、Web15（新11＋既存HTTP4）/Protocol5/Storage16 PASS、failed/error/skipped0、NullAway/format/SpotBugs0。新factory/閉wrapper全line/method/class/branch100%。全reactorは正式再実行予定 | ff77df4a60ac91c838aad0b9f15a651dfd6b4c9277169692f825fe9266c01ec9 |

探索03 command（repo root、JAVA_HOMEは421のJDK25.0.4、local repositoryはwork/toolchain/m2/repository）:

```text
./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=ClosedServletSecurityFilterTest,WebSecurityChainTest,EmbeddedWebSecurityTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

修正: RequestCacheAwareFilterを既存EncryptedSessionRequestCacheへ接続。ClosedServletSecurityFilterは閉認証actorを要求単位にsnapshotし、Servlet getterへ投影する。native認証/汎用sessionへの委譲をせず、programmatic認証操作は固定例外で拒否する。実HTTPでPrincipal/role/CSRF/session継続を確認し、100並行・別thread/Holder変更後もactorが変わらないことを独立期待で確認した。Servlet SPI nullable戻りは明示し、内部はOptional、不正nullは例外として試験する。NPEの正常扱いはない。

Spring Security7.1.1公式release source確認はPG-D-114。標準Servlet wrapperのnative delegation/default repository/null-role挙動は採用前調査であり、別のproduction障害として扱わない。raw Cookie/session/CSRF/API context/password/JVM propertiesは格納しない。正式実行のbranch/commit/実行時刻/環境/全coverageはmanifest.jsonへ収集する。
