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
