# PG628 保持期限factory障害再現・是正PT

BUG897/YKT666/PG-D400、SS341§6.3/343§6.17、WBS-P017-05既.5/1.5/3.5pp。scopeは既native保持期限へのProduction adapter束縛一箇所/package-private factory methodと回帰Test、新class0/no new public operation/path/authority/除外0。この費用の明記は最初の修正編集後・選択試験前、着手前記録遅延として487eventへ保持し遡って記録済みとしない。K01全回帰/N15native及び修復は別費で二重加算しない。

## 独立oracle・実欠陥

PG626当72fbは実新Backup2SUCCESS後、Main30/33.986s、非Backup0/旧最古一件を含む全Backup変異0。nativeparentdd050cef…/samebyteNoMatch0はcollect225～228/removeRetained最初unlinkへ到達。LinuxHostDirectoryCalls.unlink/syncが無条件UNAVAILABLEのため、実保持8→7最初deleteが不可能。injectされたwritablefixtureだけでProduction default未試験だった。

| Test ID | 実行・期待 |
|---|---|
| ISSRET001（既） | 独立handJSON/fullbyte fixture7,8,9世代をProduction選択factoryのrealFDで実行。7保持/最古0,1,2exactset/fourfiles+emptychild消失/残全byte一致/closedFD |
| ISSRET009（新） | Productionfactoryが既LinuxDirectoryCalls、read-only mutation拒否portでは8世代firstunlink一回拒否/全32file全byteとnames不変/結果未成立。是正defaultと同元fixtureでoldest1の四file+emptydirunlink/rmdir/fsync正常/残7全byte不変/FDclose |
| ISSRET002～008（既） | FAILED/REUSED read-only不変、unknown/.part/symlink/malformed/DB非SUCCESS/metadata・claim・root/期限/未観測/current排除/部分unlink・sync失敗の非成功を維持 |
| BAT194～209（既） | BackupArtifactVerifier/ManifestReader 独立固定byte/hash/false/null/例外/属性/FD/timeout/close全拒否matrix |

Root所有metadataはtestに明示したモデル（host実UID1000と混同0）、realLinux FD/read/unlink/rmdir/fsyncを分離。期待値はProductionencoder/methodで生成しない。storage LinuxHost read-onlyは変更0、全回帰でも既HOSTwrite-refusalを再確認。

`bash tools/quality/vm/050_s1/pg628_retention_factory_pt_v1.sh <固定40SHA>`：batch3suite選択、freshjacoco1session/sourceguard/NullAway/Spotless/Spotbugs/原exec・原XML保全。新method/component counters、XML/FES/skipped/rerun/静的/source/終了codeを照合後記、全PGPT100ではない。

現時点新選択試験未実行。変更されたfactory使用影響を同source六回帰で確認し、新候補署名・未使用配置/現failure所有再認証/正規active→pending/一回resume/当source真正DONE/ownedstop/nativeへ。元失敗active e492/cutoff18:32:42.140966Z/7d381、Backup2SUCCESSと元原本を保全し、旧33secを成功へ変換しない。
