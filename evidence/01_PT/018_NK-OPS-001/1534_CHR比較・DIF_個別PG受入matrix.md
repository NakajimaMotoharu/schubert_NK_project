# 1534 CHR比較・DIF 個別PG受入matrix

2026-10-23、WBS-P020-01.02、source3c70db393。群1785で.5/1.33/3pp・上限10ppを凍結。必要子01は491で同source受入済み。ArtifactComparator全Main/結果record、ArtifactComparatorTest全728行/五method/helper/16固定Oracleを読み、正本UI264/SS355§7/8/12の契約を照合した。実装修正不要、Main/Test/期待値/allowlist/baseline変更0、新Production/host PT実行0。

## 個別deliverableと独立期待値

| 元Test method（一意Test ID） | 独立期待値とPG判断 | 実証 |
|---|---|---|
| acceptsTwentyFourPassCasesAndExactlySixteenApprovedDifferences（PT-CHR-G05-003/positive） | Test側24固定ID、16手書きOracle。差分14＋同値required/contract2、16使用/unused0/unregistered0、raw/full value一致。実装からexpectedを生成していない | 元44中当method真正PASS、CLI/直API双方・atomic出力part無し |
| rejectsNullMissingAndWrongInputTypesWithoutNpe（PT-CHR-G05-004/input） | 四Path引数null/regular-fileとdirectoryの型違いはIAE。schema/JSON Pointerの比較はpath()でMissingNodeを区別し、NPE正常化なし | 元当methodPASS。固定Jackson2.19.2のFile読取は空入力にMissingNodeを返すbytecodeを点検し、readTree(JsonParser)のnullable契約と混同した不要guard追加なし |
| reportsCatalogArtifactStatusSetSymlinkAndUnregisteredDrift（PT-CHR-G05-004/artifact） | 24case集合の欠落/余剰/重複・status非PASS・caseId誤り・symlinkを失敗。object/array差を末端pathまで比較、配列index順とJSON Pointerの~1/~0 escapeも固定期待 | 元当methodPASS、CHK/failure名・unregistered pathを明示assert |
| rejectsMalformedObservationEnvelope（PT-CHR-G05-004/envelope） | version0/nonarrayは失敗、unused16/raw14を保持 | 元当methodPASS |
| rejectsUnknownOutOfScopeBroadWrongOverlappingAndUnusedObservations（PT-CHR-NK-002/negative） | 未登録DIF/未知case/範囲外/field・mode・selectorType・selector不一致、relative/*/..や末尾/Pointer、expected欠落/値不一致、同一claim/重複/未使用をすべてFAIL。differenceは実raw差が必要、required/contractは同値でも値を検査してから使用扱い | 元当methodPASS、独立17failure prefixをassertしCLI非0とFAIL reportを確認 |

「expectedCurrent/expectedNk」は独立観測oracle artifactに記載する固定値を入力とし、実行結果から自動生成しない。generic comparatorはその宣言値/selector/許可caseとactualの対応を検証する。実NKの値が承認仕様と一致するという最終受入は、独立capture/oracleを伴う後続CHRで別判定する。本fixtureの合格を実Loginタイトル/Log/16差分の実受入へ読み替えない。

正本allowlistはDIF-001～016の16ID・mode/field/case/selectorをcanonical UI264と照合し、DIF001のCHR-A01追加（QA045/UIC005/SSC074）を保持。maskは明示JSON Pointerだけ、未登録項目やDOM/page全体の正規化を追加しない。失敗observationがraw差をclaimしてもfailures自体が残るのでPASSにはならず、usedRuleは全valid時のみ。case/symlinkの集合検査、List.copyOfによる結果不変、Files.listのTWR解放も点検済み。

## quality・終了依存

source/Test/fixture/canonical文書のhashは原PG6976/6980（3c70）と現在を照合。ArtifactComparator物理二classは独立CRC実行資格と全counter miss0、当static56のうち関連行は1532の具体的根拠を適用。生のPMD/SpotBugs非0は保持、未分類/未解決当障害0。新除外/分母/抑制なし。共有四Main品質は原44の一回だけ、子別に試験数/費を再加算しない。

parallel/retryはstateless読取比較には非該当（atomic writeの競合は子01で実証）。IO/不正JSONは元checked例外でfailし、callback/実network/DB/JMS/VM操作はない。子01同sourceのstrict受入を保持してから子02を認定する。子03/親/実CHR/正式1964/53・工数率null・QA051final/PTALT0/全actualHOLDは未完/不変。
