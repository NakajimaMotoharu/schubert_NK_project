# 2463 Cleanup値型whole10・変更後通常PT仕様

2026-10-29、Production8a518b2535a1d29ce1493fa56ed7be285a540201/savef7c7241025a3ef6235568385132dd0e7207daff1/push37999真正0/origin一致。PG-D798、主費用leafWBS-P017-07.01（原canonical owner/cost P01707を保持）、開始0.75/2/4pp・cap10/開始freshは487へ直接記録。元1977～1980の20/4成功は参照のみで、今回変更CleanupStepValuesの現source資格を必要とする。

対象=既CleanupStepValuesTest whole8（BAT154..161）＋CleanupValueBoundaryTest whole2（PT-BAT-CLEANVALUE001/002）。全Test/Main/helperを読取確認済、元Test body/fixture/入力/期待値/注釈変更0・新TestID0。今回private一文字列定数化したwhole8と、同primary Mainの独立境界二件を一つの新runで実行する。旧20や別execを合算せず、BatchStepValuesの反射診断/残値型へscopeを広げない。

要求=NK-BAT-001/OPS009/DAT009/UI251/SS331§3.14/SS332§11/SS341§7/SSC057。独立期待値=固定九kind/step/完全SQL名と上限1000/LOGS10000（SQL発行0）、countsの固定tuple/MAX/負・deleted超過・skipped不一致、delta2/total5→before3、OK/LOCK_BUSY/BACKUP_GATE/FKの固定組合せ、QUESTIONのみdeferred、known/unknown total/null拒否・固定redacted文字列、独立同値/一field差のequals/hash、自己所有virtual64task/delta0..63-total100-before100-iとi0だけcomplete。Production出力をexpected生成に使わない。再送/実commit/実Backup/所有後条件は本値型範囲外。

PT_DEFAULT：四primary Main unit=CleanupCounts/CleanupKind/CleanupStepChunk/StepCleanupSummaryの全nestedを含む**五物理**をnormal Jarで先に確認、全constructor/enum/value/JDK・自己所有executor/Future timeout/TWRだけ。参照BatchRun/BatchStep/BatchStepAttemptもpure value・固定架空UUID/時刻で、実run/permit/Root/DB/Backupを生成・操作しない。BeforeAll/TempDir/FS/JDBC/JMS/HTTP/native/Graph/私有鍵/外部process0、元whole Testからmethod抽出0。

13430 entry/標準JUnitでwhole二class10method、当13406 normal9e2d9cb7・全current input/六Main/SDK15/JDK25.0.4/JaCoCo0.8.15を束縛、単一session PG13430-CLEANUP-CURRENT-WHOLE10を一回実行。独立13432相当で全XML/source/終了/五物理全key/単一execCRC/四counterを照合する。参照三Mainの未測定counterを0へ補完せず、全batch artifactや旧9source/12classに拡張0。既公式生成filter不変更/新除外0、未達は未達保持。元owner/costP01707のTest二SHA・現registry13412/594dce78へ照合する。

全ログの元日時/OS/JDK/tool/source/command/process/exit/hash・input/固定expected/actual TestIDはmanifest/結果2464へ保存、F/E/S/aborted/not-runは合格にしない。新製品障害なら修正前915/916起票、原見積/N/Tnull/正式1964-53/17-190/工数null/QA051final/全actualHOLDを維持。終了後も独立PG/PTへ、残10以下又は枠不明で新規停止保全。
