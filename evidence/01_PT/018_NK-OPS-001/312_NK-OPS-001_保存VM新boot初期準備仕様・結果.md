# 312 保存VMの新boot初期準備（SSC165）

Program NK-OPS-001、SS342/343、RD SYS002/004・OPS009、UI251。工具は隔離PG/PT専用でProduction PT分母外。ProductionのUNKNOWN/失敗受理、Root gate、原本/Current baselineは変更しない。

| Test ID | 入力/操作・事前条件 | 独立期待値/根拠 | 結果 |
|---|---|---|---|
| BOOT428001 | actual58006280 boot/固定instance、Morning cold全18property | root実UID0、旧9024boot不可、現在Mが不在。欠落/未知/追加fieldを拒否 | 工具48assert成功。期待値は独立18field literal、Production methodからexpected生成しない |
| BOOT428002 | 同M→既存固定8stop→A→同kernel全tree/manager前後 | 全MainPID/ControlPID/Job0、cgroup全子process0/populated0、既存lockmetadata/inode不変 | native v5成功、旧v1～4拒否は合格算入しない |
| BOOT428003 | 専用batch DB/advisory、保持MaintenanceRunFiles.Sessionのpending完全原本 | 固定run/activation/cutoff、元232全14列の独立SQL byte SHA75601476…、全Backup実体hash/原本metadata/hash前後不変 | native v5成功、DB dump/raw列はprivateだけ |
| BOOT428004 | 旧PG425署名55353381…/pin/current/全BOM、hostRO bind | 元Sourcea3保持、正常Unit/current変更なし、任意candidate/秘密値fallbackなし | 実verify/BOM成功 |
| BOOT428005 | startup/3request欠落、新bootinitial配置 | new-only Root0700、現boot新INVALIDのみ・同原本、旧intent退役0/旧143成功推定0/migration0/workerstart0 | native v5 exit0 |
| BOOT428006 | Asset/config独立固定SHA、API200後のTransfer child | 全named metadata/hash前後不変、既存childを旧emptyへ復元しない | BUG530是正後実成功、原本は保存 |
| BOOT428007 | 導入済PT-only agent output/drop-in | actual root-api/parent/backup/cleanup/inspector/expiryだけを設定と照合、権限/gate迂回なし | BUG531でroot-api不足を修正前登録しRoot未起動時にnew-only準備。Root native再試験は未実行 |

環境：保存同QCOW/Ubuntu26.04.1/Linux7.0.0-34/JDK25.0.4、new boot58006280-5301-4a1b-a0c2-66bce4a8a38e。元QEMU不在を確認後のみ新QEMUを起動、同Morningの二重startなし。apt timer2個は現boot元active/enablement保存→runtime停止、enabledは保持。復元は全public/worker停止/所有解除後だけ`systemctl start apt-daily.timer apt-daily-upgrade.timer`を行いactive/enablementを照合する。

実commandは`java -Xlint:all -Werror` compile、host `Pg428ColdBootPreparationTest`、VM root-private `java --enable-native-access=ALL-UNNAMED -cp <boot-tool closure/current operations+api artifacts/libs> Pg428ColdBootPreparation`。Sourceは旧signed PG425/a3の実artifactを観測する環境工具であり新Production Source352のPT/coverageを代用しない。工具source保存commitは後続管理commitから追跡、full PG428のsource/toolsと混同しない。

private native `Work PG379/pg428-cold-boot-native-v5.log` SHA4a7ae4c4749d55b24a86223f01350d932b993ec667ac76caa2b6169066698313、exit0。全SQL/原本/Backup/fixtureの前後保全はVM `/var/lib/pgpt-s1-preservation/pg428-cold-boot-v5` Root0700/各file0400。v3の旧空保存directory、全失敗logは保全。native成功からProduction boot全品質/100%を認定しない。BUG527/YKT376はProduction tmpfiles整合/再試験が残るため未完。

PG428 signed candidate Source352d6663edb492b074b900c03b528620c3c92210/manifest9c0fe6a5…は同新bootでverify03cff7cc…/activate90543ade…の実exit0、Unit差分0/drop-in不変、新INVALID/readback確認。通常Morning70d8b3c8…/PID3752は一度のみ起動、Cleanup0後親30、API/Web未起動。native parent.exec9351f2cf…/同class mismatch0がMorningPreviousBroker.collect→anchor空履歴拒否を示し、当回同bootのArtemis journalは実0byte。BUG532/SSC166に先行起票し初回cold/no-history依存を閉鎖中。既存正規API200は旧Sourcea3/PG427だけであり当回合格に流用しない。
