# ServiceCredentialLocation 原五件・有限worker単体仕様

Program NK-PRO-003 / WBS-P003-07 / BUG2844・YKT2387、既BUG1798/2465履歴保持。RD SYS002004/UI243253/SS3423434/6/411451。対象read/constructor/directory/toString/invalid、Main一つのpure JDK Map/Path metadataのみ。実env/credential/file/Root/native/permission操作なし。

PT-OPS-CREDLOC-001: 固定公開ROOTのPath.of literalとREDACTED文字列を独立expectedとし、無関係PATHを持つ合成Mapを渡す。002: missing/empty/relative/slashrootを固定message拒否。003: 大小文字alias・parent traversal・NUL/CR/LFを拒否。004: 4096字は許容/4097拒否、null key/valueは固定message拒否、nullMapは境界NPEを期待し正常化しない。005: 同じ公開literal Pathをexpectedとして32freshMapの全futureを10SECONDSで照合、finally shutdownNow→awaitTermination10SECONDS true、原5の独立assert/境界/fixtureは保持する。

期待値をproduction read/getterから算出しない。実worker非終端/failed/error/skipped/aborted/flakyは合格へ算入しない。新定義0、原5 whole classを固定sourceで一回実行し、JUnit XML/一session/一CRC-exec/全対象line-method-class-branchの実counter/初期化/Main一つ/秘密・trace/hashを独立postで確認する。Main/全Projectを再構築/全正式資格したとは扱わない。旧sourceのexecを合算せず、coverage未測定はnull。

Root Java25/UTF8/NullAway/lint Werror、SpotBugs全物理集合/MissingClass/Error0、fullRoot PMD/GJF/CS、実command/OS/tool/byte/hash/sourceは各prepare/unit/post manifestへ。ServiceConfigFiles outerとIdの別資格、実設定/鍵/VM/DB/nativeはHOLD、正式1964/53/元190新0/工数null。原計画の/1済と全owner/2未受入を分離する。
