# Retention削除行・名前境界の独立PT

Program NK-OPS-001 / MorningGateEvidence.retention, retentionName / MorningBackupRetention.collect。関連RD運用・UI運用・SS341/343 SSC133、PG-D510、1505。PT_DEFAULT、全Main/旧Test/gates固定。実原本/DB/鍵/VM/Unit/permit/native資格へ依存しない。正式1964/53、17/190、工数null、PTALT未解決/代替0は不変更。

| Test ID / method | 条件・独立期待値・後条件 |
|---|---|
| PT-OPS-RETWIRE-001 / retwire001DeletedGenerationWholeFrameAndDiskPostconditions | @TempDirに今回生成した八世代。固定名前八件・SS行順・固定三payload size/hash・操作前各MANIFEST inputのJDK SHA-256から全NKBRET1 byteを独立構成。最古一件DELETE、七件RETAINと全残fileのbyte不変、current不変、FD/stream/channel解放を検査。production resultからexpected生成なし。 |
| PT-OPS-RETWIRE-002 / retwire002InjectedName255Accepted256RejectedWithoutFilesystemNameCreation | 既Io listingにASCII x×255/256のPath dataを注入。FAILED/current無し。255は固定78×255のBEFORE/AFTER/PROTECT READ_ONLY・保護数1を含む全byte、256はIOException。実256byte filenameは作成しない。fixture不変・全資源解放を検査。 |

正常/境界/異常は新二methodで確認。null/三mode/同invocation拒否/並行再送/故障は既関連MorningBackupRetentionTest・MorningGateEvidenceTestを同source選択へ含める。実DB並行・原本再送・運用権限の受入とは分離。合成UID/effectiveUid/dev/ino portは実OS資格変更でない。既固定root.useは呼ばない。

着手時共有83/残17/reset1793082864、群予算.2/.6/1.8pp固定、費用主P018-03.02/参照P017-07.02追加0。実費/N/T不明null、予算消化を完成率としない。初回source99fce5ed71603655a08ad2d1e849a5e6b4d78bcc/6878-v1/session95822は真正1、compile/format0→PT1、29件10suiteの境界一件失敗。新DELETEは成功。BUG1630/YKT1383に修正前起票、FAILED READ_ONLY行と保護数を既SS343§6.17/既failed goldenから補完した。Main/旧oracle変更0。元公開failure manifestはprovisional/PG6878-retention-wire-failure-v1/manifest.json、元manifest ab527946/元XML74735061、終了07:52:09.883197Z。256境界は初回255失敗により未到達・合格算入0。新only v2の真正再試験と原XML/counterは未実施。途中合格化・別source全体結果の加算なし。

独立期待値の訂正：255byte FAILEDはCOUNTS末尾1、PROTECT|78×255|READ_ONLYをBEFORE/AFTERの後に置く。これは既SS/既goldenからの欠落補完で、production actualからexpectedを生成していない。

## v2真正結果・原資格（2026-10-22）

修正source a9d073e067a4400c7b68c94bb0e91a9b0903ace5、元run pg6878-retention-wire-selected-v2/session95369終了0（07:55:06.307542Z～07:57:59.587643Z、173.280101秒）、archive28717850ceb00d94b43d89e53b78a9f481f718a396a08a88e6fb075dff18b151。選択29件10suite/新二method、F/E/S/flaky/not-run0、phase0,0,0・六SpotBugs0、全source固定。既三mode独立goldenと新DELETE・255/256を実行し、未到達だった256もIOExceptionで確認。

commandは完全PYTHONPATHで`python3 -B tools/quality/pg6878_retention_wire_selected.py run`、元結果だけを`read`で資格確認（session53973終了0）。公開PG6880-retention-wire-original-v2/manifest.json SHA256=8b33234201d16c5ae4c236fb0b7f0052953dbab88f723c712bb0439ec92bf3d7。全851Main/1669物理Mainが旧Mainとbyte一致・差0、Main/旧Test/quality/Current baseline変更0、PMD raw1409保持/Checkstyle0。

当sourceの元XMLのみを6882で照合、公開PG6882-retention-wire-qualification-v1/manifest.json SHA256=28c662227ca3dc4643090086c4b27e98184d60173083b55a8a3e13fb1e5ce2e9。TestID二件と元case/source hashを一意join。retention実L69/M1/B20、retentionName実L3/M1/B2、各miss0（methodにCLASSを捏造しない）。class全体は選択未実行methodを含みmissL134/M3/B40、class100とはしない。旧全体4209のcoverageを新sourceへ合成せず、必要全体は後続変更と束ねて実施する。

BUG1630/YKT1383は新oracle修正の同29原XML/全byte再発防止・旧三mode非該当根拠まで確認し当scope完了。旧v1失敗は保持。現在起動job/readerなし、実環境HOLD・F03 Root11・QA051final・正式/17・工数null不変。fresh共有84/残16/reset1793082865をraw保存し、前2864との差1秒から同窓/リセット/専有実費を推測しない。通常小受入では停止せず次独立PG/PTへ進む。
