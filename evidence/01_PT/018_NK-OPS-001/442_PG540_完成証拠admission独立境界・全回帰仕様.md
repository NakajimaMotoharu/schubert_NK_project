# PG540 完成証拠admission独立境界・全回帰仕様

Program NK-OPS-001/NK-BAT-001、RD OPS009/BAK/BKO/DAT009、UI251、SS341342343/SSC218、451/487、WBS-P017-12.01。PG539群予算1.17/3.17/7.17（P01704+P01712.01）は継続、再配賦/親子重複0。正式受入/費用消去0。

| Test ID | 対象/入力・操作 | 独立期待値・根拠 |
|---|---|---|
| PT-PARENT540001 | MorningCompletionEvidence ctor、正規failed outcomeに有効SUCCESS pair、FAILED pairのIO_FAILURE、SUCCESS outcomeのWARNING pair | 全て固定IllegalArgumentException、message="Morning completion evidence invalid"/cause null。row自体の型契約は有効、他のenvelope条件は同じfixtureで保持し、FAILEDはCOMMAND_FAILURE・成功はSUCCESS又は所定SKIPPEDというSS契約を独立enum/literalで照合 |
| PT-PARENT540002 | 同cutoff別UUIDのvalid Backup pair、input listを一件元runへ変更、immutable pairから新完成証拠を構築 | コピー済pairは両方foreignのまま/直接変更不可、mixed pairは上流で拒否、foreign pairは完成証拠run admissionで固定拒否。既同run異handle test539001も保ち双方独立到達。reflection/Unsafe/coverage除外0 |
| PT-PARENT540003 | 全Cleanup rowが別runの有効Snapshot、成功Backupなのに一非TransferがBACKUP_UNAVAILABLE、失敗BackupのTransferが同reason又は非TransferがSUCCESS | 有効型のterminal/receiptは維持、run又はBackup失敗と非TransferだけをSKIPする因果不整合を固定拒否。元SUCCESS/FAILED正規例とPROTECTED WARNINGを既PTで再確認 |
| PT-PARENT540004 | 全時刻/counter/audit/receiptが有効でExpiry Beginsだけ同cutoff別run | 完成証拠が固定拒否、Expiry側の型構築自体は成功。UUID87654321…対12345678…を明示、元DB/master/Backup/VMに操作0 |

SSC218はpure admissionの順序だけをrun→handle/statusへ整理し、全条件・受入集合・固定diagnostic・redactionを維持する。旧順ではcomplete handle等値が後段のrun一致を論理的に含意した。検査削除/対象除外/人工到達で解決せず、真に意味のある入力段階でrunを拒否する。上流immutable pairの独立negativeを合わせて不正pair生成を禁止。

Trigger=Production MorningCompletionEvidence constructor変更なのでfresh全6moduleを当sourceで実行。command=bash tools/quality/vm/050_s1/pg540_full_v1.sh <frozen HEAD40>、JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs plugin4.10.4.0/Node24.19.0/offline。終了code/HEAD/src-tools全hash/XML/FES/NullAway/静的6module/適用JS/四counterを照合し、私有pg540-completion-admission-six-v1.*とartifactsへ保存後safe manifestを対応。未実行をPASS0、PG539/PG495別sourceの成功を流用0、新native/全CHR/正式品質は別未受入。BUGに該当する実装違反は修正前起票、TDD fixture未完は独立失敗として保持。

## 実行結果（2026-10-08）

source969d8ded10c0bf5841d9e3a5c531e922caf4a24a、開始09:36:28～終了09:54:29JST/1081秒、actual0/source全hash不変。protocol81/storage158/bootstrap257/api937/web886/batch1108=3427PT/510suite、全XML Fail/Error/Skipped0、NullAway Werror/SpotBugs6module0。MorningCompletionEvidenceTest11PT全成功、当class四counter LINE97/METHOD15/CLASS1/BRANCH86全miss0（旧BRANCH7miss→0、検査順の追加loopでtotal86）。P01712全15実行family miss715/66/1/140で未達、全体100/正式/native/CHR未受入。
全6project jarのProductionclass inventory不変、PG495との差は当constructorを変更したMorningCompletionEvidence.class一件だけ。全target byte/mtime/XML/static/jar/execをprivate work/pgpt-runs/PG379/pg540-six-host-v1へ保全、safe manifest SHA025d76218f019544c1825c23ea63178c3831ace6c5d4233cfd0c4965a8aa4951。collectorはpost-run独立helper hash、現frozen Maven sourceと別表示。raw/credentials/DB本文Git0、VM/元source a2・native9/原本Backup/runtime/旧failedscope/stash7/Scenario3/Currentbaseline不変更。
485/486は新source全六host測定へ更新、旧selected PG533/PG539はcommit09528f72fの独立fixtureとして保全し現在へ混用0。VM_STEPの証跡sourceはa2と明示し新host候補への適用false、正式run24/1964/53scope保持。WBSaudit PASS・独立管理7test PASS、管理結果をProduction PTへ加算0。SS342/914のdesign-only PR53/source31543e928→mainfc05d94f5公開済。検査順補足のhost実装/PTは完了、実source配備・native/全正式は未完。
