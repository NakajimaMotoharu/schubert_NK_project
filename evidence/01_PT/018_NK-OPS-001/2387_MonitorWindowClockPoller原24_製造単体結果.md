# MonitorWindow・Clock・Poller 原24 製造単体結果

2026-10-28 / dev-foundation / source `f8ad1ae16aa52db0119fefbad9e2cea6d6affe55` / 2386・PG-D761・BUG2006-YKT1754 / 原1561・1586・1599のRD171/UI252/SS351/451対応とTest IDを継承。主費F03、元canonical owner/costは全六path P018-09、原3/7/10pp・cap10/追加費0。計画二fixture是正/必要source再認証/新Main文脈八/歴史九source再束縛を分離、新Test ID/個別受入増分0。

Window007は同一executorのTWR外囲みだけで、元try/finally shutdownNow/await10秒/四worker64task/全assertを保持。Pollerはprivate AT→BASE_INSTANT二identifierのみ、method at/固定Instant/他全token不変更。全元token逆と十非同値負例、事前の指定formatterで確認。Main/ClockTest/他Test/POM/別golden不変更、元source0124/既成功/失敗を巻戻さず保持。

| 証拠 | 真正結果・SHA-256 |
|---|---|
| PG12844 plan | 0/十負例/十Main・選択三Test＋support一/原owner、af75aa949766cfffb5342f11bcec67fd2e61c484d60dca63b83d2d7a48715568 |
| PG12846 normal | session18629、0/六jar/PT0、48d6cc8b9d01d392bdcd94c070fb9357ae774e42119324c21c6096051f2ece17 |
| PG12848 whole24/3 | session50708、0/FES-aborted0、89f4bac39fcdfe6410e3f3badbe50d03c13899241317f516133592cc2138e733 |
| PG12850 static | session59859、1/raw19→17/CS-processing0/六SB0、77ddcdcd19da753042dca663d3940012a6ef1fdfae74bf463e546a122ff8c3e3 |
| PG12852 independent | session65008、0/測定保存・対象三Main全100、a3297ed8bbdb614f3ffb237edb34638a45d2375eb8dab20ed852244f4e271923 |
| PG12854 contexts | 0/十七node・Main新八/既九source再束縛、3273a1622d8a8121316e31c28821651d27b5f81db7944f4e62998d7cba75403e |
| PG12856 context post | 0/元XML-span-method/owner/24反例、aa4e7a66e1b83f630c11c08c2db119f54ef84e3d27853b83ffcbedea8c3ba3e7 |
| PG12858 trace | 0/原983の二Test SHAだけ変更/他981同一、05668fb67894a11ac8226baabd546fac403ee14525a393b04cb5b8011078e6cc |
| PG12859 trace post | 0/元owner/六反例/全WBS前後同HOLD1、c6956b07c21c40abd749909ce17b803fc3a61c1b54113614efbc21e6587b8d84 |
| PG12860 current delta | 0/原二IDのみ是正、3d0e54ec1bc26a9865b7ac38fc89f527565b2359cb9ad592a6e8f1f0c1464390 |
| PG12862 delta post | 0/十二反例、3163d97f2edbbebe7a13141151d6d041e26906f5c17c0f25aae397a9794a27d1 |

Manifestは `evidence/provisional/PG<番号>-*/manifest.json`、実commandは `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg<番号>_<対応entry>.py`。完全argv/開始終端日時/source snapshot・globalinput・SDK/tool/test physical/OS/JDK/branch/期待実際/終了は各manifest。Linux/JDK25.0.4/Maven3.9.12/Jupiter5.13.4/JaCoCo0.8.15/PMD7.28/CS14.3。normal未実行PT0・skipをPASSとせず、原24は単一exec `PG12848-MONSEQUENCE-JP`・Window八/Clock八/Poller八の三suite/FES-aborted0・空CWD。

対象Main四counterはWindow **13L/2M/1C/14B**、Clock **17L/2M/1C/4B**、Poller **28L/4M/1C/8B**、合計 **58L/8M/3C/26B、全miss0**。全八method detailもmiss0、branch0/0はNA。まず実counterを保存し測定0とselectedThreeMainCoverage100=trueを分け、その後の完成gateで100を必要とする。例外handlerはJaCoCo branchとは別に元Runtime/Error/null identity・不変/未commit/一回gapの独立assertを照合。全暗黙例外/割込/全JVM schedule・fixture全分岐の保証ではない。

独立全XML/summary/CRC/全input・全Main1843同byte、全Test1962のうちWindow/Poller二physical差・他1960同byte、SourceFile/Code-debug reader三正常四異常、十Main＋三selected Test＋support Test外側14唯一定義・許可外probe0/JDBC-Artemis load0を確認。support FilesystemHealthObservationTest元十methodは未選択で、FixtureStore body/initializerと必要の全sourceを審査した値stubのみ。全FileStore virtual methodをoverrideし2統計以外throw、実path/属性/identity/FSを読まない。固定Clock/AtomicLong/明示Duration/自己有限workerのみ、実Root/VM/DB/SQL/JMS/ネットワーク/FFM/native/鍵/権限操作0。

完全Batch645はcovered253L50M17C85B/missed18164L3155M396C8373B、他API467/Web358/Protocol176/Storage80/Bootstrap117 covered0を同一execで保持。必要のAlertLifecycle/TimedFilesystem等の未達も完全counterへ残す。JaCoCo0.8.15の既定compiler-generated enum/record/synchronized処理filterだけを継承し、State enum/ObservationContext record等の物理classも完全artifactから除去しない。暗黙JVM故障や生成methodを人工的に呼んでcounterを増やさない。旧別source Context66/Duration38/Registry19/Alert14等のunion0、人工呼出/手動除外/filter変更0。全artifact/451/正式coverageは未達。

静的十七はMain monitor四/unchecked catch四/nullable一/Test Thread八。private final monitorは順序/経過/gapを原子的に保ち、Pollerはclock/input/actionを同sequenceに保持する。内側のclock→観測/window/lifecycleへの順序を審査、callback期限や実collectorの所有は外側責務で局所timeoutを保証しない。generic catchは失敗を一回gapへ変えて同一RuntimeException/Errorをそのままthrow、retry/正常扱い/例外formatをしない。null結果のNPEも正常結果ではなく非commit/再throw、明示@Nullable sentinelはNORMAL/UNKNOWN resetと次VIOLATING再設定のguard下で使う。

Test Thread八は standaloneの自己poolでJ2EE application workerではない。Window invokeAll10秒＋旧finally shutdownNow/await10秒、Clock/PollerのinvokeAll/getと全TWRには局所絶対deadline無し、外JVM240秒と区別。独立集合1..64、固定読取回数、非atomic action serialize/同一期間起点、元guard/hash/現caseを結合しraw17/gate1を保持、抑制・実装是正に数えない。新Main分類八、既nullable一＋Thread八はsource再束縛九、全17は全scope資格待ちpendingを保持する。

現source導出 raw8469（Main1505/Test6964）、累計948、refs3188/pending846/未参照5281、追加raw八保持。原scope19/current17の差はPMD04807/04865二件だけ、原983の現before六hash/ownerを別に確認し歴史sourceと混同しない。全再解析0/actualViolationCountnull。BUG2006/YKT1754は当二fixtureの再発防止/非該当根拠と原24まで限定完了、製品PT失敗/実装工具不備/本群build失敗0。正式1964PT/53scope・17/190・工数null・QA051final/全F03-451/CHR/安全HOLD・原見積不変。保存commit/pushは456へ記録する。
