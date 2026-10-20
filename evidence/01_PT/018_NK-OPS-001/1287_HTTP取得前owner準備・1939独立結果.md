# 1287 HTTP取得前owner準備：当source1939の独立結果

source acb5fe9c375ede57f5d15fc5fc392f2197c910d4、branch dev-foundation、仕様1286/PG-D461/SSC312/BUG1545/YKT1305。Main三・既Test三への新JUnit各一。design-only PR169→origin/main ff82686063fd1700780a3885ce10e15fb1bd1125へ通常merge/fetch済、当SS一致、添付100上限は一回失敗・再送0。未受入code/tool/evidenceはmainへ含めない。

元exec62707/pg6112-http-owner-selected-v1は16:13:37.409987Z→16:25:46.349873Z（2026-10-20 UTC）、728.939886秒、真正exit0/phase[0,0]/1939件/318suite/FES/flaky/notrun0、六format先行/型nullSpotBugs0/全入力固定。API1013/Web919/他guard7。三新JUnit内の複数failure inputは三件に含み、件数を水増ししない。環境は既固定host Linux/JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0/Node24.19.0、commandは462PTPRE035とtool6112・PYTHONPATHに既pyflakes runtimeを加えたもの。初回import時のPYTHONPATH不足exit1はnamespace/Maven作成前、実jobは一つだけ。原失敗を成功扱いしない。

| 当実counter | LINE | METHOD | CLASS | BRANCH |
|---|---:|---:|---:|---:|
| ApiManagementServer | 82/82 | 11/11 | 1/1 | 46/46 |
| WebManagementServer | 117/117 | 15/15 | 1/1 | 62/62 |
| WebHttpServer | 109/109 | 15/15 | 1/1 | 42/42 |

Factory純interfaceは原JaCoCo実counterなし（実行codeなし）として保持、100へ補完しない。全global/nativeは別未完。

| 証跡 | SHA256 |
|---|---|
| WorkPG379/pg6112-http-owner-selected-v1/begin.safe.json | cfe79beae986de0821760fb4f1f48389c937da4cbcea43785f643034a7c29f1e |
| 同source.tar | f53fccf30325f1678624d305f65e2a64428396d00d1a208abc93edeadb213f1c |
| 同manifest.safe.json | 5f4c357e25c2e0f5781374a33d9b932bc33668a738878eea43847a05a5525aa1 |
| PG6114-http-owner-qualification-v1/manifest.json | 504e9754e0c815e97a70870d576988c9a7bde3aeabec6427a71bd15657ae1103 |
| 同private manifest.safe.json | 25e146627faa6caa710f6b7e9b6350cd61b6960165c9e56e18a0f82387360bba |
| 同cases.safe.json | 40fa7510b4b801367031b4e9470615a4b0f29477a124d8f8512e24e24872af72 |
| 同findings.safe.json | 3a6556f88448c7e61973ec57a82bbfd4d922b0eefa9c6c643ea3ca023f97778c |
| PG6116-http-owner-order-v1/manifest.json | 6bb8792c6b4f68fd72599f77faffac9176677f85cb1361deb6ff26ba475d8476 |

53386/6114は原全1939XML/六Jar/全851Main source/1667 compiledとJarを照合、三outer差だけ・他1664完全byte一致。無除外raw PMD1311/processing0/Checkstyle0。旧599raw1314との差はDoNotUseThreads二件/CloseResource一件が生成順序・owner構造の変更で消えたもの、ルール抑制/除外0、残1311を静的0とはしない。旧721分類も新source wholejoinの成功へ転用しない。

13861/6116は実三constructorの全flag/lock/MVC/executor/info/address先行、factory一度→nonnull/final格納/returnのみを確認。全public/package signature、既close/start/ready等の命令・例外edgeを保持、callerの取得構造のみ変更、daemon thread lambdaはprivate method名の移動だけで命令不変。InvokeDynamic indexは実bootstrap handle/全引数へ解決して照合（番号だけ無視する合格ではない）、独立負fixtureを含む工具unitでallocation/未知callback/欠落・二重取得/handle改変を拒否。実OOM/VM/Root/配備操作0、追加Production build/PT0。

BUG1545/YKT1305の三対象は限定PG/PT確認済み、当source必要全3988/595・全理由/trace・native/CHR/451は未完のため総合closeは保留。旧8703985/599925/旧nativeを当acbへ合算0。正式1964/53・17/190・工数null・QA051final/PTALT未特定代替0/原v3v4・保全物・実操作HOLD不変更。次は1288の前提成立を保存し、clean source/fresh枠/host同job無し/headroomで新only全3988を一回実行する。
