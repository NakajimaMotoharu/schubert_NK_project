# 279 NK-OPS-001/NK-BAT-001 既知Backup失敗の親結果確定

OPS009/BAK001、UI251/253、SS341§5.1/343、SSC115、BUG325/YKT257。Program/class/methodはMorningProcessMainの同owner completion、MorningDatabaseSession.failBackup、MorningBackupUnitCycle/Receipt/Termination。PG386予定。仕様登録時はNOT-RUN、結果を先取りしない。

| Test ID | 入力・操作/独立期待値 | 事前条件・fixture/根拠 |
|---|---|---|
| PT-OPS-MMAIN009 | SUCCESSは実archive callback1回・failBackup0、FAILEDはarchive0・failBackup1回、両resultがFAILED/1target/0success/1failure/0bytes/COMMAND_FAILURE、実終了UTCµsである | 固定run/両handle、固定Clock、記録するAccess port。expectedはliteral値、Production methodで生成しない |
| PT-OPS-MMAIN010 | null各境界はNPE契約で無操作、時計逆転/IO/未知は正常化せず親隔離へ、結果確定失敗で後続成功/退役を呼ばない | 各clock/DB/archiveの独立故障、外部Main unknownの既存同identity試験 |
| PT-OPS-BFAILED-VM001 | genuine external Morning→fresh正常非0worker→明示stop/全終端→両DBFAILED/COMMAND_FAILURE readback→原本/current再照合→request/intent0。旧SUCCESSは保存し新FAILEDを隠さない。archive/MANIFEST生成0、worker失敗partは保全。最終Morning30はS2未接続で非成功 | 隔離VM、同Source/JAR/agent。元固定backup-pgpassをprivate保全し、M/A/全8停止/INVALIDのtrusted fixture scopeでworker credentialのみ不正passwordへ。DB/schema/role/原本/時計/基準oracleは変更しない。元入力の復元も同scope |
| PT-OPS-BFAILED-VM002 | UNKNOWN/signal/timeout/commit不明はFAILEDに補完せずM/A通常unwind不可・intent残存・次回admission拒否、現実全子終端/再開条件を独立確認 | 同budget/親systemd期限、既存SSC107/BUCYCLE/BSTART負vector、実外部採取未了 |

実行環境・command/Source/branch/終了code・独立DB結果・parent/worker JaCoCo/全4counter・BUG/SSC・file hashは同Sourceの結果manifestへ記録する。FAILED/skipped/not-run/flakyをPASSへ算入しない。Coverageは除外追加や人工native callで補わない。未検証のS2/Transfer/Expiry/permit/APIWeb/CHRは本仕様のPASSではない。秘密/credential実体/dump/復号内容はGitへ入れない。
