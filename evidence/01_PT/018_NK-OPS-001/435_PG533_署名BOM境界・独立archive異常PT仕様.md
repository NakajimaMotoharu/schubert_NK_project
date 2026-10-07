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

既存001～013には正常、null、欠落、byte改変、namespace、例外、並行/interrupt、全取得/解放faultを維持する。本追加は変更bootstrap試験群の限定検証であり、全体・native・正式coverage100%合格に加算しない。DB/JMS/実VM、原本/Backup、Current baselineを変更しない。

## 実行と証跡

- 初回source254aa287a/v1 actual1、親pomのjar plugin版解決失敗、compile/PT未実行。BUG826/YKT595起票後、Source固定して `bash tools/quality/vm/050_s1/pg533_bom_pt_v2.sh <full HEAD>`。旧v1を再実行しない。
- Host Linux/JDK25.0.4/Maven3.9.12、既存offline repositoryを使用。
- storage/bootstrapのcompile/NullAway/SpotBugs、BOM16PT、JaCoCo四counterを同じsource/runで照合する。storageの選択対象なしは合格PTへ加算しない。
- 私有ログ/source hash/XML/exit: `/home/mini/codex/project1/work/pgpt-runs/PG379/pg533-bom-pt-v1.*`。公開manifestは終了後にsanitized結果・hash・不足counterを記録する。
- 失敗は未実装TDD/fixture/実装障害を分類し、承認済み実装の違反は915/916へ修正前に起票する。
- BUG/SSC: BUG826/YKT595、SSC追加なし。正式認定PT-WEB-20260925-24は据置。未網羅/未実行をPASSとしない。
