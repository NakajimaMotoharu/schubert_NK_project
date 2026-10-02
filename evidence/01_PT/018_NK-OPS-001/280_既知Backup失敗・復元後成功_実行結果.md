# 280 実Backup既知失敗・入力復元後成功（PG386、暫定）

2026-10-03 BUG563/YKT407証跡packaging補正：ignored `.log`のoracle/failed-unit metadataを同byteのtracked `.txt`へ保存、既存実行Source/結果/時刻/coverage/原本・Backup現物は変更せず外部再実行0。PG385補正manifest SHA037b65cf95afa6bd68242761c77908b99eec58a9c93c2912403c70dea3e5721f、PG386補正manifest SHAc76c0c050544a06fa2acf8ed2cfbad0dcef9f1a2254fa48c62520a925c994c69。旧087bf6a…/30f3ce8…manifest revisionはGit履歴に保持、下記旧hashは当時記録として有効。714manifest中233既存log参照＋4補正txtの237件は登録/存在/SHA一致、陰性ignore canary PASS、001provisional PG437 reproduction packaging-check.py/915916を参照。formal/S1の認定更新はない。

Source `d49a3a9fb0876ccf07e3e968df9e961bce215397`、dev-foundation、SS341/343・SSC115・BUG325/YKT257・仕様279。実Ubuntu26.04 VM、kernel7.0.0-34、JDK25.0.4、PostgreSQL18.6、age1.2.1、JaCoCo0.8.15。IT/STや正式認定ではない。

| Test ID | 実入力・操作／独立期待値 | 実際結果 |
|---|---|---|
| PT-OPS-MMAIN009/010 | 固定Clockと記録Accessのliteral FAILED counts/COMMAND_FAILURE・成功archive callback・null/逆転/故障 | 選択Bootstrap9+Batch43の52件成功、静的各0。全6同source回帰にも含む |
| PT-OPS-BFAILED-VM001 | 署名/fullBOM・M/A・全8Unit終端・INVALID原本を保ち、Backup専用credentialのみprivate負fixture。真正外部Morning --resume、正常非0worker、両完全FAILED行・原本後条件・退役 | 親58161ad0006a4fb6909d4a74d6cd0b62、子98336502bb5f4764b378eccea15979f3。ExecMainCode1/status1、DB行7/8・attempt4・FAILED/1/0/1/0/COMMAND_FAILURE、実終了03:53:12.364635Z。旧成功不変、失敗part保全・新MANIFESTなし、request/intent0 |
| PT-OPS-BFAILED-VM001/RESTORE | 同trusted scopeで変更前force保全済原byteを復元。credential値/hashを出力せずFiles.mismatchと別cmpで一致証明 | private原fileと現在credential完全一致、root0600/nlink1/108byte。失敗fileはprivate保全 |
| PT-OPS-BFAILED-VM001/RETRY | 同source・同run/cutoffで入力復元後の真正fresh子、実artifact生成/独立oracle・両結果再読 | 親90999e2a66954050b835d49a89475c89、子886b0f0822364c67b09d2be470cbc05b（PID1 start/stop done）。行9/10・attempt5 SUCCESS、dump170930byte、config20480byte、暗号credential41160byte、固定7/16member・private復号・size/hash・pg_restore-list224一致 |
| PT-OPS-BFAILED-VM002 | 実30分期限/UNKNOWN隔離/次回拒否/正規復帰 | NOT-RUN、合格に加えない |

両外部Morning最終exit30はS2/S3未接続の部分非成功。permit0、原本run/cutoff・旧ABANDONED/成功/今回失敗すべて保存。成功済stepを通常resumeで再生成する現sourceの不整合は別修正対象であり、この結果から通常resume契約の合格を推定しない。

実証跡：`evidence/provisional/PG386-native-backup-failure/manifest.json`、hash `30f3ce8a11b7fa7822de6c5a618a91cec5723014c58604b3b5dbd92a1fc1ca45`。全file hash・実command・入力/期待/actual・終了code・BUG/SSC・環境・fresh Invocation・DB全列・復元根拠をmanifestと対応fileへ記録。raw journal、credential実体、鍵、dump/復号archiveはGit外private。

全回帰trigger=SSC115/BUG325の実Main failure completionと同起動security群。同source固定全6 clean/test/SpotBugs/JaCoCo/runtime inventory、13:20:30 JST、12:57、2544PT/372suite F/E/S0、静的6module0。manifest `evidence/provisional/PG386-known-backup-failure/manifest.json` hash `c229df4c98cb8cc983c217a16be9631163cfc324f3b0adebd8abbeff79de520a`。

Host B/L/M/C未網羅：Protocol/Storage0、Bootstrap37/13/5/0、API3/32/4/0、Web1/25/4/0、Batch247/1040/241/23、合計288/1110/254/23。PG385とのgraph差分−2/0/+1/0。**同byte Batch host+今回正負parent/worker union178/459/99/11**、不一致0、hostから69/581/142/12解消。a6b等の旧source execは混ぜない。全4coverage100%未達、S1全受入/正式53scope認定は据置。

初回負fixtureのReleaseApproval参照比較による入力変更前拒否はBUG349/YKT279起票後、version/hash値比較・Production全BOM再読へ修正し、実負試行と正規復元を確認。横展開追加negative/全対象品質閉鎖は継続。
