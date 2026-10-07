# PG533 署名BOM境界・独立archive異常PT仕様

- Program: NK-OPS-001 / `ReleasePayloadVerification`、公開入口 `StartupReleaseManifest.verify/verifyCandidate`。
- Trace: RD SYS002/004・OPS009・DAT009、UI212/251/253、SS343 9.1/11.1、SS354、451、WBS-P018-02。
- 事前計測: 487 event PGPT-20261008-0030、低位0.5/基準1.5/高位3.5週次pp。共有枠残88%、実token N/T不明。PMO消費へ配賦しない。
- 状態: 実装・独立試験準備。PG531/532は当Production byteの不足診断であり、本変更の試験合格ではない。

## 独立oracleと範囲

実際の一時directory、literal release inventory、独立SHA256/ZIP、固定SQL `select 1;\n`、独立CRC -690524359を用いる。Productionのprivate methodを反射実行せず、公開検証入口から受入/拒否・全resource解放を観測する。owner/RO属性は明示した合成fixtureでありnative認定ではない。

| Test ID / method | 入力・操作 | 独立期待値・根拠 |
|---|---|---|
| PT-OPS-FULLBOM014 / fullBom014ArchiveMetadataAndStreamDisagreementRefuseAndClose | duplicate ZIP entry、SQL size -1/67108865、SQL stream長 -1/+1、archive entry count 131073を個別注入 | 承認payloadは一意、material最大67108864、stream長=entry size、archive上限131072。全件IOException/redacted message、狙ったarchive一回、archive close一回、取得済みentry stream close一回 |
| PT-OPS-FULLBOM015 / fullBom015MigrationEntriesBelongOnlyToApiAndHaveSqlSuffix | Web内SQL、API内非SQL migration、署名hashと合致するが異なるVERSION bytes | SQLはAPIのみ/.sql、VERSIONは承認release+LF。署名一致だけでは受入不可。IOException、全owned FD解放 |
| PT-OPS-FULLBOM016 / fullBom016ForeignDeviceAndOversizedMaterialRefuseBeforeRead | release directory/ VERSIONのforeign device、VERSION material size 67108865 | 同一filesystem/最大material契約違反をVERSION channel取得前に拒否。狙ったmetadata実到達、VERSION open 0、全owned FD解放 |
| PT-OPS-FULLBOM017 / fullBom017InterruptAfterChannelAcquisitionClosesWithoutReading | VERSION channel取得直後にcallerのinterrupt、最後にtest側で解除 | read前に拒否、取消を勝手に解除0、取得済channelを一回close、owned FD全解放 |
| PT-OPS-FULLBOM018 / fullBom018ManifestBoundsSameSizeTamperAndEnumerationLimitRefuse | manifest size 0/1048577、同サイズVERSION byte改変、directory entries16385 | manifest範囲1..1048576、hash一致、列挙最大16384に反するため拒否、列挙stream一回close |
| PT-OPS-FULLBOM019 / fullBom019RegisteredThirdPartyJarIsNotAnNkSharedDependency | 独立literal登録したorg.example:vendor:1.0/API lib jar | NK共通依存と区別し正規third-party jarを受入、独立SHAとartifact件数一致、FD全解放 |

既存001～013には正常、null、欠落、byte改変、namespace、例外、並行/interrupt、全取得/解放faultを維持する。本追加は変更bootstrap試験群の限定検証であり、全体・native・正式coverage100%合格に加算しない。DB/JMS/実VM、原本/Backup、Current baselineを変更しない。

## 実行と証跡

- 初回source254aa287a/v1 actual1（jar版解決）、source42f0e6cbc/v2 actual1（SpotBugs prefix解決）、どちらも親pomに起因するcompile/PT前拒否。BUG826/YKT595起票後、依存storage/bootstrapを明示選択し親pomを含めない別v3へ固定、`bash tools/quality/vm/050_s1/pg533_bom_pt_v3.sh <full HEAD>`。旧v1/v2を再実行しない。
- Host Linux/JDK25.0.4/Maven3.9.12、既存offline repositoryを使用。
- v3 sourcec4117fe97 actual1はstorageの選択PT0件をfailIfNoTests規約が拒否、bootstrap未実行。規約を緩めず、別v4 `bash tools/quality/vm/050_s1/pg533_bom_pt_v4.sh <full HEAD>` でstorage/bootstrapの全PT・compile/NullAway/SpotBugs・BOM16PT・JaCoCo四counterを同じsource/runで照合する。旧v1～3は不合格保持。
- 私有ログ/source hash/XML/exit: `/home/mini/codex/project1/work/pgpt-runs/PG379/pg533-bom-pt-v1.*`。公開manifestは終了後にsanitized結果・hash・不足counterを記録する。
- 失敗は未実装TDD/fixture/実装障害を分類し、承認済み実装の違反は915/916へ修正前に起票する。
- BUG/SSC: BUG826/YKT595、SSC追加なし。正式認定PT-WEB-20260925-24は据置。未網羅/未実行をPASSとしない。

## v4 限定結果と次run

source dbea258c7、2026-10-08 07:30:20～07:31:09JST、actual0/source不変。storage158PT/22suite、bootstrap252PT/37suite、F/E/S0、NullAway compile/SpotBugs2module0。BOM16PT全PASS、当class LINE244/METHOD31/CLASS1は全covered、BRANCH184covered/6miss（PG495 host16miss→6）。module全100%ではない。v4 XML/SpotBugs/BOM XMLをprivate `pg533-bom-pt-v4-artifacts` に保存し次cleanで上書き0。

次=追加017～019のsourceを固定し別 `pg533_bom_pt_v5.sh <HEAD>`。v4合格を変更後sourceへ流用せず、同じ2module全PT/static/counterを一回実行する。工程正式認定/全体native/IT/STを更新0。
