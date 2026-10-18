# 永続記録・worker要求の取得前scope

NK-DAT-001/NK-BAT-001/NK-OPS-001、RD DAT/BAK/OPS009・UI251・SS332/341/343/354・SSC308・BUG1414/YKT1178。主費WBS-P004-03、構成費P017-03.03（終了/close）・P017-06・P017-07.02（資源例外）、親03/07は非加算。群1197の開始.3/1/3共有ppは一度固定、1198/1199の費用leaf訂正は追加費/受入ではない。child split/専有N-T/null、先行child受入/全契約/451の未達を保つ。

対象：DurableRecordFiles readFile/write/forceの3、BackupWorkerRequestFiles read/writeの2、CleanupWorkerRequestFiles read/writeの2、MorningBackupRequestPublication.publishの1。前七つのnullablechannel/customWriterはnull時だけ既UNAVAILABLE IOException、nonnull側はfactory直返却・unboundclose・全port先行。Morningはopen::open/Owner::closeでnullのNPE型を保持（内部診断messageは資源共通名へ統一、利用者向け電文/例外分類は不変）。公開前後gate/割込/所有/namespace/new-only/再open/metadata/EOF/force/原本保護/UNKNOWN/close優先順位は変更しない。実DB/Backup/VM/秘密情報操作0。

独立oracleは既DurableRecordFilesTest12・BackupWorkerRequestFilesTest10・CleanupWorkerRequestFilesTest13・MorningBackupRequestPublicationTest7の全42case。Test IDは各JUnit method一意名をmanifestに収録し、既PT-BAT-046..057、PT-OPS-MBPUB001..006/1425001、breqfile/creqfile試験への対応を維持する。既literal byte/content/size/UID/GID/mode/link・観測順・非上書き・null/欠落/異常IO/progress/割込/並行/複合closeの期待をproduction methodから生成しない。新Java case0、取得後OOMEの無理な実機再現はせず、scope fault既試験＋全port前置/実bytecodeの無追加call/確保を独立に証明する。

当source一snapshotで関連既642＋対象42の予定684PT/85suiteを真正完走、六format先行0/NullAway・ErrorProne0/三static0/全storage四counter miss0。旧sourceの642へ単純加算や旧native輸入はしない。全764Mainの差分を要求し、新outer4と付随nested debug候補だけ許容、debugは旧実classSHA＋全opcode/handler意味同義、他不変。bytecode検証は8caller全port先行と7checked factory/null側IO、Morningの直接factorymethodrefを確認する。

実行tools：pg5192_durable_worker_selected.py → pg5194_durable_worker_bytecode.py → pg5196_durable_worker_public.py → pg5198_scope_classification_durable.py。元job終了code/XML/source/archive/command/toolversion/日時/coverage/BUG/hashは1062とallowlist manifestへ保存、rawXMLproperty/秘密実体は公開しない。BUG1414全体、残152候補、新whole3833/558/1661/native/全四100/F03/CHR/451/QA051finalは別受入で未完、通常小区切りで停止せず継続する。
