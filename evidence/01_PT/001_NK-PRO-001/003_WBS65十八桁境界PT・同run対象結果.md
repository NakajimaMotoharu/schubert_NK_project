# WBS65 十八桁境界PT・同run対象結果

2026-11-12。Test/source `8f66c2c17b33e564c0f6aa56214db47b616dce49`、Production Main `7aed8eace7c844c2f79f2e39db766faf914890d5`、branch dev-foundation。PG26204-PROTOCOL-WHOLE124-RANGE。JDK25.0.4/UTF-8/Linux amd64/Asia-Tokyo。Main変更0、旧25 Test source/120 method/五独立TSVのbyte変更0。

追加したTypedUnsignedRangeBoundaryTestは四method・113入力観点で初回成功。1..18幅の0/最大36、各幅-1/最初のoverflow/Long両端72、無効幅4、null名優先1。期待値は標準BigInteger10^widthの算術と独立literal、Production桁上限関数不使用。JUnit四methodは同run全124の内数、独立追加実行数として足さない。

実行はinput024 prepare→static→025 preflight→source固定/push→024 run 8f66...→026 independent post。各command/時刻/OS/JDK/終了/入力hashは下記manifestのoriginal/compile/static/preflight-manifestへ保存。compile0、PMD17 rawは旧17既知対象と全一致・applicable0、新Test raw0、Checkstyle0。全25fixture/124件でF/E/S/aborted/container-abort0、Main正CRC163/held四初期化0。旧120の再確認目的ではなく新四追加後の必要module品質実行であり、元の120結果は不変保全した。

Module実測はLINE3478/METHOD742/CLASS159/BRANCH1014、全miss0。物理176は実測code159＋noCode13（package7/interface6）＋既存標準synthetic switch-map四として独立確認。手動除外/旧exec union/fixture抜粋なし。元Program全体の正式受入ではない。

同runからP00103の75source/75物理を投影した実測はLINE1450/METHOD374/CLASS73/BRANCH38、全miss0、宣言専用interface二。追加COMPLEXITY393/0も保持。自然B0の各sourceを0/0=100へ換算せず、owner集約の正の38branchと区別する。

標準filter445は別表で全件を記録した。Java25 record getter302/equals71/hash71と、TypedFieldValuesの空private utility constructor一。前者はcompiler定型で独自logicなし、named296getterは独立public bindingの実assertと結合し、base六getterはliteral入力/immutable/clone試験と結合する。最後のconstructorはsourceで空/非公開/インスタンス生成なしを確認し、private reflectionを使わない。既定filterを変更せず、当445にruntime coverageがあると主張せず、全authored意味処理のcounterと分ける。新しい除外globや到達不能偽装はない。

BUG2645/YKT2325は元工具が旧五counterと新六counterを全dict比較し、追加COMPLEXITYだけでguard失敗した事象。PG26210beforeを保全、旧必須全値一致/四counter正数miss0を維持して修正。追加metric許容と必須欠落/branch miss拒否のmetadata検査を記録、製品PT再演0。

証跡：module evidence/01_PT/002_NK-PRO-002/evidence/PG26206-protocol-whole124-range-independent-v1/manifest.json / SHA256 d2bd415f1fce8d1ae5521aaa89e9fd14838248275537741080619a233df8b678、owner evidence/01_PT/001_NK-PRO-001/evidence/PG26208-p00103-same-run-scoped-coverage-v1/manifest.json / SHA256 57f6f377902bb0ae20017281e34d2a755c173729545243f77778bcf450aff1d8。二manifestのfilesからXML/counter/input/expected/source/実際値をTest IDに追跡する。正常Test新四の各case referenceも同runから別表化した。

追加PT不足は解消、WBS-P001-03/2個別受入は後続の契約・scope・451条件判定で確定する。正式1964PT/53scope・元190新受入0・工数率null、実VM/native/CHR/全scope451/HOLDは維持する。IT/ST完了の宣言なし。
