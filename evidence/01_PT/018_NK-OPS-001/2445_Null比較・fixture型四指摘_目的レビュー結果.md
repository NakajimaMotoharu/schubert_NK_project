# 2445 Null比較・fixture型四指摘・PG目的レビュー結果

2026-10-28、2444/PG-D789/source81a1b0c32be8167c07320e6bfaf469bcd44eb7bd、先行save5ef20b6696f8c3be3184a718478a12d07416e9e7/push4049真正0/origin一致。群開始0.5/1/2pp/cap10を保持、共有開始used11/reset1793774153・専有費/N/Tnull、終了fresh観測は487 eventへAPI最小fieldを直接転送し、原/改訂/群見積と混同しない。

| 元ID | source目的の確認 | 保持する未証明 |
| --- | --- | --- |
| PMD-02148 EqualsNull | dbConn005が`assertFalse(first.equals(null))`を明示し、wrong-type/別値/record accessor等と並べたequals負契約。参照比較へ置換せず元oracleを保持 | 当sourceのTest実行/生成method coverage/collector全体・並行成功は未確認 |
| PMD-05293 MissingStaticMethodInNonInstantiatableClass | outer private constructorのnamespace、static nested Script/Childがreader/process portを提供。streamはChild所有の非static ReadStream/WriteStreamで、外側のstatic method/fieldではない | fixture/Unit/実processを起動した根拠ではなく元サービス経路HOLD |
| PMD-06238 TestClassWithoutTestCases | TestIoはouter Testから構築するIo callback実装、当nested bodyに@Testなし。名称のTest prefixをJUnit case欠落とみなさない | 実NioIoへ接続、元Test全体はFS/native/credential境界を含みHOLD |
| PMD-06249 TestClassWithoutTestCases | TestSecurityはInodeSecurityCalls実装としてouter Testから構築、当nested bodyに@Testなし | Files等の実境界へ接続、class load/初期化/実行・実credentialアクセスなし |

元ID/原全attributes/current signature/current行/class/method・三source SHA、証拠断片/hash、元owner-cost（P01809/P00404/P01801）、個別目的と残存リスクを全四行保存。実sourceを新Testとしたり、旧成功/compileを実行許可へ転用しない。全規約適用性確定/false-positive一括除外/指摘抑制/実PT免除ではない。

## 工具の失敗と限定是正

元13316/session42726/entry6bfedf4aaf91d0d1b6fd695c314571c5a14605a2bbfbc6f54a007985eb535dd5真正1、OUTなし/source変更0/PT0。field型名から四型すべてstaticと誤仮定したguardであり製品/Test失敗ではない。BUG2048/YKT1796先行起票後、別13317で実宣言の二static外型＋Child内二非static streamを確認し目的文言を訂正。元工具/失敗を保全・再実行0、原失敗reportファイルは未保存の欠測を残し、元exit/entry/OUT無しは独立postへoperator観測として記録した。

13317/session35240真正0、manifest `e3a2f4ba8d26b368328838e54db68be515dad20af72071d7b11c1862ef7aadd0`。独立13318/session46909真正0、manifest `9cc205651a953ed3292b541957bfac90c2ee33b1c777e43f84e57726092183f0`、元四ID/全source SHA/元attributes/証拠断片・型階層/責任費・実行0とtyped負8（欠落/重複/equals oracle/階層/owner/免除/boolean zero/coverage）を確認。全証跡pathは本directory下`evidence/provisional/PG13317-null-fixture-purpose-v2/manifest.json`とreview.json、`PG13318-null-fixture-purpose-post-v1/manifest.json`、各command/環境/全loader/entry hashはinvocationに固定。

元三source/expected/Test/code/995全row/費用/runtime/source資格の変更0、fresh build/PMD/target PT不要のため再実行0。目的refs3345→3349（+4）、pending1366→1370、noRef4402→4398、raw7747/corr1694不変更。原global9409/追加32（うち14未分類）/source db33の全体実測8022を別保持。履歴集合はpinned13317＋独立13318を読む`pg13320_null_fixture_review_history.state_after`、PRIOR_TRACEはcode資格13312/7443c342のまま。現sourceを読むproducer.expected/validateを将来変更後の履歴計算へ転用しない。

BUG2048/YKT1796は当工具/目的文言scopeを全四確認・八反例で完了、修正commitは本結果を含む次保存（456参照）。ProductPT/新TestID/受入0、coverage未測定・全F03/451/正式1964-53/17-190/工数null/QA051final保持。実FS/Unit/VM/DB/鍵/Root/native/Graph9/保留二工具/私有rawは非操作、原本Backup/native証拠/stash7/Scenario3/Currentbaseline保全。限定公開/exact保存push後も必要な独立PG/PTを継続し、通常小群/commit/PMO待ちで止めない。
