# Retention削除行・名前境界の独立PT

Program NK-OPS-001 / MorningGateEvidence.retention, retentionName / MorningBackupRetention.collect。関連RD運用・UI運用・SS341/343 SSC133、PG-D510、1505。PT_DEFAULT、全Main/旧Test/gates固定。実原本/DB/鍵/VM/Unit/permit/native資格へ依存しない。正式1964/53、17/190、工数null、PTALT未解決/代替0は不変更。

| Test ID / method | 条件・独立期待値・後条件 |
|---|---|
| PT-OPS-RETWIRE-001 / retwire001DeletedGenerationWholeFrameAndDiskPostconditions | @TempDirに今回生成した八世代。固定名前八件・SS行順・固定三payload size/hash・操作前各MANIFEST inputのJDK SHA-256から全NKBRET1 byteを独立構成。最古一件DELETE、七件RETAINと全残fileのbyte不変、current不変、FD/stream/channel解放を検査。production resultからexpected生成なし。 |
| PT-OPS-RETWIRE-002 / retwire002InjectedName255Accepted256RejectedWithoutFilesystemNameCreation | 既Io listingにASCII x×255/256のPath dataを注入。FAILED/current無し。255は固定78×255のBEFORE/AFTER全byte、256はIOException。実256byte filenameは作成しない。fixture不変・全資源解放を検査。 |

正常/境界/異常は新二methodで確認。null/三mode/同invocation拒否/並行再送/故障は既関連MorningBackupRetentionTest・MorningGateEvidenceTestを同source選択へ含める。実DB並行・原本再送・運用権限の受入とは分離。合成UID/effectiveUid/dev/ino portは実OS資格変更でない。既固定root.useは呼ばない。

着手時共有83/残17/reset1793082864、群予算.2/.6/1.8pp固定、費用主P018-03.02/参照P017-07.02追加0。実費/N/T不明null、予算消化を完成率としない。初回source99fce5ed71603655a08ad2d1e849a5e6b4d78bcc/6878-v1/session95822は真正1、compile/format0→PT1、29件10suiteの境界一件失敗。新DELETEは成功。BUG1630/YKT1383に修正前起票、FAILED READ_ONLY行と保護数を既SS343§6.17/既failed goldenから補完した。Main/旧oracle変更0。元公開failure manifestはprovisional/PG6878-retention-wire-failure-v1/manifest.json、元manifest ab527946/元XML74735061、終了07:52:09.883197Z。256境界は初回255失敗により未到達・合格算入0。新only v2の真正再試験と原XML/counterは未実施。途中合格化・別source全体結果の加算なし。

独立期待値の訂正：255byte FAILEDはCOUNTS末尾1、PROTECT|78×255|READ_ONLYをBEFORE/AFTERの後に置く。これは既SS/既goldenからの欠落補完で、production actualからexpectedを生成していない。
