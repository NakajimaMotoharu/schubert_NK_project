# COPY行streamとdataset接続・独立15仕様

NK-MIG-001/MIG003005006/MIG-DAT004005/DAT004/FUN004、UI254、SS331/34310.1.4 SSC351、WBS-P01903.02。

既PostgresCopyTextEncoder.encodeRowsは全行を単一StringBuilder/byte[]へ組み立てる。実ETLへのCOPY transportは全streamの追加bufferを避けるため、新PostgresCopyTextWriterで宣言済Iterableを一回だけ進め、各rowをsnapshot→同一非zero列数検査→既encodeRow→借用OutputStream.write(byte[])の順に送る。次rowを取得する前に現在rowを送信する。heap追加量は最大encoded一行に比例し、巨大raw_block一行自体の上限を追加せず実測は後続に残す。既byte-array API/既Main encoder全byte/escape/nullable/NFC責務を変更しない。

writerはnonnull既final encoderだけを保持、null encoder/Iterable/sink/row・空row/列数不一致は固定IllegalArgumentException。元codecのNUL/surrogate不正は元の固定例外を伝播する。IOException/iterator故障を成功へ変換せず元exceptionのまま伝播し、失敗後に次rowを取得しない。送信済prefixは残り得るので原子的保存/DB commitを意味しない。sinkはcaller所有、成功/失敗ともflush/closeを呼ばず保持しない。実DB/FD/file/Root/permit/サービスを開かない。toStringは固定REDACTED。

ScenarioCopyDatasetへwriteFiles(writer,sink)/writeEntries(writer,sink)を互換追加する。旧constructor/getter/byte-array methodsは不変。fileは既immutable rowsを渡し、entryは既Row.fieldsの参照List（O(行数)参照、本文複製なし）を渡す。null writerは既dataset固定診断、null sinkはwriter固定診断、元I/O故障を伝播する。二方法は共通FK/時刻検査済みのdatasetだけを使い、上流の1transaction/権限/全量/実source/asset受入を代用しない。

PT-MIG-STREAM001..012: 001手書き二row escape/NULL/UTF8全byte、002空Iterable・sink無操作、003一回iterator/次row取得前の送信、004null encoder、005null Iterable/sinkをiterator前に拒否、006null/空row、007mixed widthと送信済prefix、008元NUL/surrogate例外とprefix、009sink IOException同一instance/次row未取得・closeflush0、010iterator故障同一instance/既prefix、011input/sink所有・redactionと独立呼出、012finite8worker64task/Future5/finallyshutdownNow-await10の独立golden。新Dataset PT-MIG-DATASET013..015は二stream golden、null writer/sink、両経路の元sink障害/再呼出不変。

必要closureは新Writer1＋既Dataset接続変更と支援全8Main=9Main17physical、Writer12＋Dataset追加3＋元98=whole113。新定義15だけ、同source/一exec/Root通常静的・NullAway/lintWerror/CRC-init/XML/四100/実Code差を照合し、旧成功の確認再演・別source合算0。追加不足1.1/3.3/6.6（未較正）=詳細.1/.3/.6+製造15定義.55/1.65/3.3を群.65/1.95/3.9cap4、必要normal113別群.45/1.35/2.7cap3。元費用/群開始額/SV上限保持、実token/専有費null。小literal/メモリsinkだけ、実DB/全量/原本/Backup/Rootnative/Actual4/aru/拒否対象HOLDを解除しない。
