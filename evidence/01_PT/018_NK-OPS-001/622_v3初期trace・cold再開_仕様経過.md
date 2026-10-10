# v3初期trace・cold再開（暫定、工程/正式受入ではない）

Program NK-OPS-001 / NK-DAT-001、Production40ef6e894573d2ffab1d1732124960f9c98d5f97 / PG932。SS342/343/352/353/361、451、WBS-G13.07/N11/N04/N15.04。見積版PMO-remaining-v3-20261010、SHA6f7faa627cf64a1496dd980faf59406170e3458d00773fc7e8d83bf754f98298。元見積と旧成功/失敗証跡は不変更。

## Test ID・独立期待値

| Test ID | 事前条件・操作・独立oracle | 現況 |
|---|---|---|
| PT-DEP-996001 | 485全281要件/938成果物の主担当、481候補試験・spec Test IDをjoin。現物hashは485との直接比較、存在だけで受入しない | PG996 actual0、missing/changed0、844仕様索引。TestID候補とoracleの意味照合は領域/最終段階に残す |
| PT-DEP-996002 | 工具の独立fixture：現物あり/異hash、別class候補、未知owner/欠落pathでも受入false/期待値検証falseを維持 | 二工具case0。Production PT追加0 |
| PT-DEP-997001 | QEMU/port/diskowner無し・source/backing identity固定、元snapshot不変更。空き容量制約下で私有compressed copyを作り、独立qemu-img compare exit0と元identity不変を確認 | 実行中。compressed qcow2はraw byte同値と主張せずguest logical byte同値で判定。5GiB file limit/6GiB preflight、private全0700/0600、失敗/partialは保存・不合格 |
| PT-DEP-998001 | 現boot、canonical十Unit冷停止18値/kernel空/署名187/永続24table594行/原本Backupを991-v4保存afterと独立二読。新bootの/run inodeや旧INVを復元しない | 未実行。QEMU無し/旧cc9生存記録失効。private991の永続原値だけ比較し、失われたtmpfsを成功退役としない |
| PT-DEP-999001 | 当Inspectorは合法なlive Root/owner/budgetだけ。旧成功履歴/原本を削除し新日を偽造しない。actual native/session/source/終了をN15.04で資格付ける | 契約監査中/未実行。古い親eeaeの期限/権限を借用0 |

## 対象領域の多対多trace（主担当費の移動なし）

- DAT-009（485主担当P004-01、通知削除と質問回答非連鎖）：Inspector consumer P004-04の`protectedResult`/`successAndResume`等の候補を照合。DB後条件が独立oracleであり、当空Inbox nativeだけで全削除契約を閉じない。
- FIL-006（主担当P003-05、専用local受渡しroot/相対参照）：P004-04 Inspectorの所有directory/credential/security/null/IO/parallel試験をconsumer側で照合。共通root実装と共通counterは主担当の一回費。
- OPS-009（主担当P017-12、起動依存順）：P004-04の`app925001GuardIoFailurePrecedesAllCredentialAndDatabaseIo`は、固定IO拒否→credential/DB呼出し0の独立負例。host synthetic admissionは合法OS起動の代用でなく、N04/997～999のactual owner/期限/資源後条件が別途必要。根拠はSS342/343/352と当ソースJavadoc RD/UI trace。
- P004-04の`requirementIds=[]`だけを「関連RDなし」と解釈しない。上記cross-owner要求とSS責務を明示し、938対象のsemantic oracle個別確認は未完として記録する。候補test名が直接一致しない572件は「PT欠落572件」とは断定しない。

## 実行・品質・費用境界

12:37追補：1001管理boot0、QEMU19945/newcbca、original/backing不変更。1002-v1はactual1/2.207918s、既typed空ExecStop経路を省略したBUG1004を先行起票。1003-v2はactual1/1.723828s、metadata lifetimeを保持せずGC後GetUnit拒否のBUG1005を先行起票。旧script/log/終了を上書き0。純qualified963 captureと十Refの新1004-v3 actual0/3.440239s、全10冷18/kernel・24/594/Backup47/cred19/original59/oldproof28二読一致・187同pin署名/approval・client/advisory/flock0。newafterSHA1cbb10fa83df138d5f3fe6b40b8107e16475e280745797f6e9e5a58d030073a9。

1005は成功済みDB/treeを再実行せず、上記data proofを再利用し狭い十Unit32fieldと宣言triple/cold execution tailだけを二読0/1.378268s。configSHA246a6673f16736fdd6af66d4e58d4f948bb35492d166d59c5dffe92e8572b2d8、全metadataRefs正常返却、warm履歴復元0。PT-DEP-1004001/002はRef順序・途中取得/Unref/close未知を拒否する二工具case、PT-DEP-1005001/002は独立literal宣言/foreign/null/旧warmとnewcold区別・不要全DB反復0を二case、actual0。1002二case/776typed拒否一caseも0。初回schemaキー/namespace大小文字/fixture広すぎrestore文字検索のTDD失敗は不合格保持・guest副作用0。Production PT/native追加0、formal不変更。

public `evidence/provisional/PG996-1005-current-cold-v1/manifest.json` SHA37d6b9ef6486299896b5921aea6de4c8a41738b2cdc04a89ff66753b3b7c3047。全失敗とnewsafe proof hash・未達を別に記録。SSC243先行/SS343353設計onlysource8f1/main57108/PR80通常merge確認、foundationa836へ継承、empty冷準備/Inspector/newnative/正式未完。PMO PAUSED・共有枠個別費とN/Tnull、次は合法empty cold準備と独立残host契約、通常区切り停止0。

11:59追補：997v1/v2の各compressed copyは5GiB上限でactual1。v1開始seal/convert code欠落をBUG1003/YKT772として起票、v2はbegin/convert/failureを永続保存し実convert1/source/backing stableを確認（v2の実行中に追加したexception handlerはそのrunで実行されたと主張しない、当時の非0receiptは存在）。未知returncodeを-25等へ補完0。失敗copyだけ各5GiBをhash/metadata/log/failure保持後除去、元disk/backing/旧snapshot/privateを保持。partialはどちらも合格ではない。

新1000は元保存diskを不変更のread-only backingにする197248byteのCOW作業層を作成。独立qemu-img compare actual0、元disk/backing identityと開始hash一致、旧内部snapshot保持。standalone backupとは主張せず、以後のguest変更を新 `work/pgpt-vm/private/pg1000-cold-overlay-v1/active.qcow2` にのみ記録する。VM保存元instance.qcow2を直接起動しない。free6.9GiB回復。次1001はSS343既basic.target/ネット・SSH・PGのみ、timers/paths mask、canonical unit商用起動0の同flagsで一回予約先行起動、独立argv一case0。boot/current再認証は未実行。

追加PT-DEP-997002/003：非0convert/compare/null/bool/metadata全五要素変異でboot許可false、failure receipt overwrite拒否、OSError記録は型/phaseだけ・raw messageなし、最終三工具case0。初回追加TDD E1はfixture assertionのdirectory参照誤りで不合格保持、是正後三case0・Production PT加算0。995/正式/旧成功は書換0。今回N11同stage内の再試行で開始費用を再加算せず、残見積/時間/個別実費は既区間の欠測を明記する。

`python3 -B tools/quality/vm/050_s1/pg996_v3_initial_join_test.py` / `pg996_v3_initial_join.py`、host Linux7.0.0-38/Python3.14、branchdev-foundation、開始HEAD70f98a3。manifest `evidence/provisional/PG996-v3-initial-join-v1/manifest.json` SHA05b7fb466f5bbca754f5cdb7bb0e18d9006817826c42b6a27465de39cb2e8fbb。二工具caseと管理auditをProduction PT/coverageへ加算0。正式24/1964/53・coverage100条件は不変更。

G13.07三stage低/標準/高 .6/1/1.8＋.95/1.5/2.75＋.4/.75/1.3＝1.95/3.25/5.85。N11四stage .25/.75/1.5＋.5/1/2＋.5/.75/1.5＋.25/.25/1＝1.5/2.75/6。親費用追加0。0259に事前配分、PG997専用stage eventはjob開始後の遅延として記録（時刻捏造0）。共有枠/個別実費/実tokenを分離、N/Tと個別ppは欠測null。
