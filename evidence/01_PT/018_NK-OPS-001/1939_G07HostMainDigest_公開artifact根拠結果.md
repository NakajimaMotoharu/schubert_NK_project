# G07 正常host Main class digestの公開根拠結果

2026-10-25 17:08 JST、group2175/PG-D658。Production source64446a9f8901084a4ad7eba1f66ae975eb2bbdea不変更。1938の固定仕様に基づき、正常host Jar6の1843 Main class/965 sourceを実byte・SourceFile・Jar/source hashへ結合した。producerはPython ClassFile parser、独立postはJDK25 Class-File APIを使う別実装であり、対象classのload/init/実行は行っていない。

|公開manifest（evidence/provisional以下）|元終了code|SHA256|
|---|---:|---|
|PG9564-g07-host-main-class-provenance-v1|0|458970306a06b661c558c67f25b5769308fffb91d2c7d8603f996084a70de2ff|
|PG9566-g07-host-main-class-provenance-post-v1|0|8ad5591f0f152f44a9efb0e87a38d3eb8a6c844a7dadb3ecb50934c0747a929b|

原40086 findingのtupleと重複個数、歴史content05d73/sourcefb9、既31707公開根拠を保持。残8379の全exact captureを別抽出し、新しい実Main class digestを少なくとも一つ含み、全captureが公開artifactへ結合できる3829件だけを追記分類した。公開根拠済み31707→35536、未分類8379→4550（未根拠4549＋exact capture未再構築1）。registry SHA fbff1d26291e75f91341125afecc97fcdd9899c5b50bd8fb53bc886f5fffaf10、updates SHA a57cb221d8d3923df136305a2b4e29256c76271ebc98c671b44f8606e20f13aa。候補値・候補だけのhash・context本文の新保存なし。

独立postは1843registry/965source/8379tupleの一致、工具Java metadata6vector、proof集合6vector、metadata12反例を確認。自己所有の工具compile/read JVMは元終了0、producer session97532/post82368も終了0を回収済み。外部VM・業務processの所有/生存/終了は未照合HOLDのままである。

これは固定された歴史scanの追加根拠であり、現在sourceのsecret gate合格ではない。actualSecretCount/coverage/工数率null、実PT/新Test ID/新Main/正式増分0。正式1964PT/53scope、個別17/190、QA051 final、全current WBS audit実1HOLD、BUG1746、F03 Root11、実VM/DB/native/鍵/intent/permit/配備/拒否対象未特定操作のHOLDは不変更。scanner/全scan再演/祖先全blob hash再演/私有raw/対象runtime/遠隔操作0。

開始07:41:55UTC used3/残97→観測08:07:04UTC used4/残96、同reset1793513544/secondarynull、共有丸め差1pp。専有費/実N/T/配賦はnull、usage74eb00e8の既存cursorを維持し、明示usage recordなしを消費0へ読み替えない。開始.5/2/6pp/cap10、原/v3/v4/v5見積り不変更。事前SDK path仮定による実体読取前guard停止は1938の選定手戻りとして分離。Borrowed9は原資格から不変なので成功確認だけの再実行0。

次は9568 END/9570 public delta/通常commit-push。その後、残4550について既存の古い正常host成果物の公開source/class/Jar由来を読取で立証できる範囲を新群として選ぶ。存在しないartifactを遠隔回収したり、旧成功を当sourceへ移植しない。現在窓残10%以下/取得不能等の正規条件まで継続し、小群・commit・通常報告・PMO返信待ちでは停止しない。
