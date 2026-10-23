# 1694 MQ供給圧力metric 結果・追跡

1693 MQPRESS001..008/PG-D559/group1911、是正source `1cbd253172b836e059b94578000c553a197f5407`。元製造新8＋必要既106を当sourceで普通114/14実行、旧106/初回114/歴史Batch237-Web27/Protocol依存のcoverageを合算0。実Artemis collector/source/owner/time・JMS/制御は未受入HOLD。

| provisional原run | 真正結果 | manifest SHA256 |
|---|---|---|
| PG7644-mq-pressure-host-v1（source d8df90b1e） | 初回普通114/14/FES0、静的資格は別pending | d92d3486b5c0ee21976e57f33952956741c62446f7ea22cd630f7381de6da238 |
| PG7646-mq-pressure-post-v1（同d8df） | 四100 L414M82C23B199/CRC0/SB-CS0だがPMD新1含む14、BUG1670へ | e03d0b3f9694bfb96406f1cccaaa467519fc7db014f3370c312fb35033b2f7bf |
| PG7648-mq-pressure-six-compile-v1（同d8df） | 六正常compile0/PT0UNRUN、変更後へ流用0 | caf90c25f1ec802a662b8af072f46ae095b159d36f1b565c104c4e59f652c2cc |
| PG7658-mq-pressure-host-v2（source1cbd） | 是正後普通114/14/FES・flaky・rerun0 | b78b9b2157480e77689d638603e32b470c70d35e57ac7dd69e514a6fcba15718 |
| PG7660-mq-pressure-post-v2 | 28Java/実23＋metadata1/単一sessionCRC0、L414M82C23B199全miss0/NullAway-SB-CS0/raw既13保持/新Main0 | 020a8f6e8bf6b5e479229bdc025fd8cbc2a9e07e6900e2262df9cb9298621587 |
| PG7662-mq-pressure-six-compile-v2 | 当六正常Main/Test compile-package0、PT0/UNRUN | 38d71fe63cf4fd59a8f9bc155ed1443608d80eb0dec31271f2c662f45c0e3a2c |
| PG7664-mq-pressure-six-post-v2 | 全1763/元1669debug不変、当API24/歴史Batch60-Web10、protocol依存176全byte一致/五architecture rule0 | 9e0ac103683daa2b7a0f5715dd26506aca4dcbd085eed19def7e5cd17aa42428 |
| PG7666-mq-pressure-trace-v2 | 全106source/94追加physical・旧104不変2新、API実23だけcurrent | 24dc29624cad45fd24f63bc9c6d9eeddb414baf913726182cda487a81c4c93fa |
| PG7668-mq-pressure-review-v2 | raw既13同source/位置の個別理由/新Main0、生成新9＋既32当普通PT・五domain負改変/全source anchor | d4c08cb34a35e94ea76efbe5c0bc6748ed5da190ecf5f66d7a832bfa1b06abf0 |

日時/OS/JDK25.0.4/Maven3.9.12/branch/source/command/actual exit/input/XML/output/CRC/四counter/static/hashは各原manifestから一意追跡。是正後session32131/68736/58487/40235とtrace/reviewは真正0回収済み、実行source変更/重複起動0。元7650/7652/7654は実行前のdraftを7664/7666/7668へ整理し、初回d8dfのpost/arch/trace成功として偽造0。初期計画の実22/全1762/93physicalはnested Snapshot一型を除いた見積誤りで、実測23/1763/94へ訂正しただけ、受入や工数進捗増ではない。

## BUG1670/YKT1421の当範囲閉鎖

PMD AvoidDuplicateLiteralsはnew constructorのaddress四literal、line62/col13。一つのprivate ADDRESS_LABELへ共通化し、同構築パターンのqueue二箇所もQUEUE_LABELで定義。修正commit1cbd253172b836e059b94578000c553a197f5407。SS label実値/全36series/独立8case/期待値を変更せず、当114ordinaryと全品質へ再結合、new raw1が消え既13が全属性不変。既raw13はowner lock/failure propagation9＋借用JDBC resource4で、同label重複には非該当。Batch MetricContract内のaddress/queueは閉catalogue enum宣言で実Gauge構築ではなく、既歴史raw28の理由とbyte不変を保全、当sourceで試験したとはしない。Web監視にはaddress/queue labelを用いず非該当。検索だけの完了ではなく、全対象の実修正とSS literal36・unknown/zero/MAX/negative/null・factory Runtime/Error/foreign Counter・64caller/別ownerの再発防止を実行した。当部品限定CLOSED、YKT1413他generated/実collector/whole451は未受入。

Snapshot新生成9は各field xor-fold・31fold・Boolean1231/1237から固定hash30607576/30607762、1<<32 hash衝突/equals非同値、全field一差・固定text/全accessorをMQPRESS008で独立検証し、当実class SHA/javap bootstrap全6fieldと同JDK/filterへ結合。計41methodを四counterへ合成/安易な除外0。SDK doubleへのMAX丸めは9.223372036854776E18として明記し、immutable snapshot原longはMAXを保持する。全Gaugeを跨ぐscrape atomic性・actual source真正性を推定しない。

元製造新8/既106のsource再資格/手戻りMain1（BUG1670）/tool・技術見積訂正/依存再認証を分離。群開始2/4/8pp上限10/原-v4-v5不変更。new quota観測0/100→1/99/reset1793382075は同新marker内の観測であり、旧27/73/reset1793306748との不明区間を0や実resetにせず、全共有累積/専有N-T/工数null・元90上限予算の再基底化0。券消費/追加課金/導入/install/M2上書き0。正式1964/53/原190新受入0・QA051final/PTALT0/whole451-native-CHR/全actualHOLD維持、原本/Backup/鍵/stash7/Scenario3/Currentbaseline保全。実VM/DB/JMS/Root/配備等操作0、PGPT完了とはしない。
