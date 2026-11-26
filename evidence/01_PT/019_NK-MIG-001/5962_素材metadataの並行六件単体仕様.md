# 音楽・動画・Media・対応表の並行六試験

WBS-P019-03.02/2、F03、SS331・343・354、BUG-3938／YKT-2997。対象は表の既試験だけ。元仕様の別列、byte列、借用stream終端、元入力・期待値と依存を保持する。

| ID | 選択メソッド | 独立期待値の元仕様 |
| --- | --- | --- |
| PT-MIG-MUSICID012 | MusicLogicalIdTest#finiteWorkersUseFreshDigestsForTheSameStatelessIdentity | [037](037_Music安定logicalID・独立十二仕様.md) |
| PT-MIG-MUSICCAT024 | MusicMigrationCatalogueTest#finiteWorkersProduceTheSameIndependent129RowGolden | [047](047_Music百二十九行と全media結合・独立二十四仕様.md) |
| PT-MIG-MUSICPAIR026 | MusicMigrationPairingTest#finiteWorkersShareNoMutablePairOrShadowState | [045](045_Music宣言pair算出・独立二十六仕様.md) |
| PT-MIG-VIDEO024 | VideoMigrationCatalogueTest#finiteWorkersBindTheSameImmutableClaimsWithoutSharedOutput | [041](041_Video固定二十catalogueとCOPY生成・独立二十四仕様.md) |
| PT-MIG-MEDIABATCH020 | MediaAssetCopyBatchTest#finiteWorkersUseOneImmutableBatchWithIndependentSinks | [043](043_MediaAsset集合とmanifest結合・独立二十仕様.md) |
| PT-MIG-MAPMAN007 | CurrentMigrationMappingManifestTest#mapman007SharedImmutableManifestHasFiniteIndependentReaders | [135](135_現行ID四対応表manifest・既組立接続全958仕様.md) |

各workerと入力の個数、5秒結果取得・10秒終了は元仕様に従う。一次失敗と終了失敗が重なる検証は既MigrationFixtureWorkers試験を参照する。各今回TestIDの終端を当正規Bootstrapの一つのexecで取得。通常の既済別試験、実DB／原本／領域アクセスは対象外。
