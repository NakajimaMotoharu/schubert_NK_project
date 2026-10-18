# 固定296snapshot所有・F03適用性 PT仕様

NK-MSG-002/NK-OPS-001/DAT009/UI241/SS324§6/15・352、Test F03-OWN-ZIP-001..003、BUG1453/YKT1217。Root296実行中の独立host読取のみ、Main/Test/署名/実VMを変更せず同接続経路の資格を保全する。新scopeのnative圧縮二件は原237 inventoryとは別母数、元割合を書換えない。

001 原PG5426の全1647 finding metadata hash **41ddbd7c** と全3896/562/1664独立資格JSON **273d2710**、現PG5430/BOM85fb/実API Jar/三Main実class SHAを厳密一致。ResponseSnapshotCodec.compress/decompressのjavap実constructor PC→scratch NEWARRAY→handler全範囲/normal exceptional endを独立抽出する。Errorを捕捉しないDataFormatException handlerをcleanup保証へ読み替えない。

002 compress PC5constructor/12newarray/any開始15、decompress PC4constructor/11newarray/guard開始14を実確認、二件は**DEFECT_OPEN**・BUG1453へ束縛し、finallyがあるだけでfalse-positiveにしない。実OOM/永久リーク/現在Root失敗は未観測で、fault試験・是正は後続。現Main/SS/Currentbaselineを変更0。

003 OperationFingerprint.canonicalBytesのWipingStream constructorPC11/store14→Throwable body15..132・normal close133/exceptional close140と実WipingStream class/source・SecretBuffer/OperationFingerprint元whole XMLの独立期待値を結合し、この一指摘だけFALSE_POSITIVEとする。close呼出しが無意味だから除外するのではなく、実TWRによって既に解放/wipeが実装されていることが理由。

command `PYTHONPATH=/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg5506_snapshot_ownership_review.py`。新専用公開manifestに全1647の元finding ID/source/spanを保持して三件だけ個別更新し、他1634未確認/既十結果を保持。PMDを再実行せずraw1647/抑制0・F03/正式false。管理三は独立PC fixtureでguardあり/array先行/typed-only guard/foreign・欠落を検査し、Production試験/coverage加点0。結果1132へ元exit/source/class/payload/hash・未解決BUGを保存。

1273群開始0.5/1/3ppはこの記録以降の証拠化作業へ固定。先行の初期Source/javap閲覧には別着手見積りが無かった事実を残し、遡及費用/Root群への均等配賦/原v4残減額0。正式1964PT53scope/工数null/QA051final維持、当初/前回/v4未較正597.25へ新発見・実費を混同しない。Root元watch24893の通常観測を継続する。
