# 素材inventory純値製造と独立12通常PT仕様

NK-MIG-001/WBS-P01903.02、FIL003005/MIG003006・MIG-DAT003006、UI254、SS343SSC342（main e48e393185/PR208）。Java25 bootstrap package migration/AssetMigrationManifest。実I/O・DB/原本・authorityなし。未実装機能TDDなのでBUG起票なし。元/2のETL/実master/DB/ID・表示順と受入は残す。

| Test ID | method / 独立期待値 |
|---|---|
| PT-MIG-ASSET001 | canonicalGolden: 五列/固定header/順序/UTF8LFを手書きtextblockと全byte比較。abc3/既知ba7816...15ad・empty0/既知e3b0...b855、input2/total3。production encoder/hashからexpected生成0 |
| 002 | validPathsAndKinds: 全4kind/NFC/supplementary/relativePOSIX名、境界0/LongMAX、emptyinventory。非authority値であること |
| 003 | invalidPaths: 空/absolute/backslash/空segment/`.`/`..`/全control/非NFC/未対応surrogate、source・target・observed双方拒否 |
| 004 | nullContracts: list/要素/kind/path/hashすべてのnullを明示拒否、NPEcatch正常化なし |
| 005 | invalidSizesAndHashes: 負byte/63・65桁/uppercase/nonhex拒否、lower64許容 |
| 006 | duplicatePaths: source/targetそれぞれの重複Entry・観測target重複を拒否、元list不変 |
| 007 | checkedAggregateOverflow: source/observed各MAX+1のoverflow拒否、MAX+0許容 |
| 008 | immutableOwnership: 元list変更・返却list書換・返却byte全消去でも元snapshot/golden不変 |
| 009 | identicalClaims: 観測順逆転でもmissing/extra/size/hash各0、observed2/3・metadataMatches true。constructor六負値は拒否。file/DB成功とはしない |
| 010 | missingClaim: missing1/extra0/他0、observed1/0、metadataMatches false |
| 011 | unexpectedClaim: missing0/extra1/他0、observed3/4、metadataMatches false |
| 012 | independentSizeAndHashDifferences: byteだけ/hashだけ/両方で各countを独立固定、metadataMatches false |

Source/Test全体をGJF/RootNullAway/lintWerror/PMD/CS/SB、固定source whole12一回、独立post全physical CRC/初期化/XML/FES/全四counterへ結合。到達不能・除外・無意味assert・旧exec合算なし。時刻/環境/JDK/tool/branch/source/command/終了/input/output/hash/coverageは各manifestと結果。返値は宣言metadata間の比較、実file/symlink/hash/原本/移行/Unit/Go/451/ITSTの成功ではない。

追加発見価格 .8/2.4/4.8の内、source+全12Test製造 .5/1.5/3（上限4）、normal .3/.9/1.8（上限3）。旧見積りの既存artifact前提がowned0で成立しなかった不足を明示して追加、元/2のETL/fullcriteria費用とS/V原枠は減らさず保持。専有実費/token不明null。
