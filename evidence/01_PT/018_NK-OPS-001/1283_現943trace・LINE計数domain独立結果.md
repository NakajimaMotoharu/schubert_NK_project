# 1283 現943traceとLINE計数domainの独立結果

source870/PG-D459、仕様1282、WBS-G13.07部分整合。元3985真正0と独立原XML/全8511667/六Jar/六coverage（1281、qualification76d222ee）を使用し、追加Production試験/全回帰/実VM/DB/service/配備/業務intent/permit操作0。

PG6102 stage/元16972真正0、apply/元90095の適用部分真正0、全WBSaudit真正0。485/486のcurrent candidateだけを現943へ更新し、歴史941descriptor/source/個別17・481/484 byte・486歴史rows/counts/source/measurement/formal/工数nullを保持。二typed exception補助型だけを既P005-03/導入6b5cea563・226fbb6c5の同byte/追加予算0/UNASSESSEDへ対応付け、旧candidateはbeforeGit634e3dddb/path/hashとmeasurement参照でhistory保持。SSC311状態だけmain35702e5f57f962b916beee646751fbd192858642/PR168へ反映済み、code/tool/evidenceをmainへ混在0。アプリPR添付は上限100で一回拒否され、再送/迂回0、URLは履歴保存。

| 証跡 | SHA256 |
|---|---|
| PG6102-current-host-measurement-v1/manifest.json | 7cc058fdbc5983ca4c0a36e231d25d9f54883e44d2e3de9a40b2e3015c30a17a |
| WorkPG379/pg6102-current-support-trace-v1/stage.safe.json | efc09a5a874edec0935e2ba64797fad10cbd066cd4f158386374eb8eb2f78e27 |
| 同/apply-intent.safe.json（管理metadata journal） | efc09a5a874edec0935e2ba64797fad10cbd066cd4f158386374eb8eb2f78e27 |
| 同/apply.safe.json | 58b8a1772d9f4ec0838f12f320658cba2aa8cb103e646b38295cd4782ada32c7 |
| PG6102-current943-trace-v1/manifest.json | eddd284529eee70f264351fc905ce93dc7c898bb041535e5b1611f0578f7227d |

全943のGit/current byte・二SS295移転/明示二補助型/一owner、全sourcefile/既owner counterを照合。現在Java担当116の技術測定は93がclass counter未網羅0、22が未網羅有り、1がcharacterization別証跡必要。後者は六Production module外の四compatibility-tool familyを未測定で保持し、0/100を補完しない。これらはWBS受入数ではなく、元17/190の受入は不変更。旧04bb native測定と当host-only測定は別domainで、新sourceへ輸入0。

## BUG1543の原因と再試験

最初のreportは「ownerのclass-family LINE3533＝module root LINE3525」を要求して停止し、公開report未作成だった。原stage/apply/audit0・元coverageはそのまま保全し、再適用/原PT再演0。原因はLINE counterの集計domain混同で、class sum自体は正しい。sourcefile/rootは同じ物理行を統合し、一部classの命令だけ未実行でもそのsource行はcoveredになり得るため、両者を等置してはいけない。

| batch sourcefile | class未網羅LINE合計 | sourcefile未網羅LINE | 差 |
|---|---:|---:|---:|
| MorningDatabaseSession | 20 | 19 | 1 |
| MorningBackupRequestPublication | 20 | 19 | 1 |
| MorningPermitPublication | 50 | 48 | 2 |
| MorningBackupUnitCycle | 66 | 64 | 2 |
| BackupUnitStartClient | 97 | 96 | 1 |
| MorningStopPass | 25 | 24 | 1 |
| 計 | 278 | 270 | 8 |

是正後はclass-family LINE3533をそのままowner品質gapとして保持し、sourcefile/root LINE3525を別projectionへ記録。METHOD668/CLASS38/BRANCH722は同domainで一致。各sourcefileをmodule/package/fileの一意キーで既ownerに割当て、XMLの各物理行ci/miから独立計算したmiss/coveredとsourcefile counter、さらに全module rootとの一致を確認した。未知file/owner・二重file/物理行・偽counterは拒否。3工具unit actual0には「一classが未網羅・別classが同じ行を実行」の反例と当全六XML/実六file差8を含む。pyflakes0、最終report actual0。8を新coveredや追加進捗へ計上せず、全class品質判定では未網羅3533も残す。

旧4948 owner_measurement/3282 group_coverageはclass-family計数として妥当なため変更せず、旧report/04bb原記録を歴史保持する。旧source固有mainはその資格済sourceのroot一致を要求し、新sourceへの汎用転用を認めない。新6102ではowner lineCounterDomainとsourcefileLineReconciliationを明示して両系列を接続、全未網羅class行を消さない。BUG1543/YKT1303当scopeCLOSED/完了2026-10-21、本是正/証跡commit参照。

現Rootの四counter未網羅はL3525/M668/C38/B722、owner class-family LINE未網羅は3533、global100/native/CHR/F03/451/trace全終了依存/引継ぎは未完。WBSauditは190項目/252leaf/17受入・formal変更falseで合格したが、G13.07のRD/UI/SS全要件join全体やPGPT完了を意味しない。正式1964PT/53scope・17/190/工数null・QA051final/PTALT未特定代替0/実操作安全不明HOLD・原v3v4は維持。
