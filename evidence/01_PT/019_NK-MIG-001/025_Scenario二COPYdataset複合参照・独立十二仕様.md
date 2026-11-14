# Scenario二COPY dataset複合参照・独立12仕様

NK-MIG-001/MIG003005006/MIG-DAT004005/DAT004/FUN004、UI223/242/254、SS331/V002/34310.1.4 SSC350・WBS-P01903.02。

既に別々に検証済みのScenarioFileCopyBatchとScenarioEntryCopyBatchを、同じ宣言済datasetとして接続する内部ScenarioCopyDataset。nonnull二batchを受け、全Entryの(game_id,script_file_id)が今回File batchの(id,game_id)へ一致することを検証する。他のFileMapを使ってEntryBatch単独だけが成立していても今回File batchに不在なら拒否する。全file/entryのcreated_atは同一canonical UTC値（両batchで検証済）を要求する。DBの一transactionで一回採取した値を共用する契約を具体化し、時刻/IDを生成・補完しない。

files/entries両方空、fileだけありentry空は値として許容するが、必要全量262/99661等の成功ではない。entryだけありfile空、game違い、未知file、二batch間時刻違いは固定IllegalArgumentExceptionで拒否する。既二batchは不変なのでその参照を保持し、公開getterもimmutable値だけ。fileCopyBytes/entryCopyBytesはnonnull既encoderで対応する各batchへ委譲し毎回別所有byte、SQL/header/terminator追加0、途中でDB/file/serviceを操作しない。nullは固定非秘密診断、toStringは固定REDACTED。本文/path/ID等をdiagnosticへ混ぜない。

PT-MIG-DATASET001..012: 001独立二COPY stream全byte、002両空、003fileのみ、004entryのみ/未知file、005同id別game、006全file/entry共通stamp違い、007null二batch、008null encoder二経路、009immutable二batch入力aliasからの独立、010毎回byte所有/呼出順独立、011redactionと拒否後正常値の独立、012finite8worker64task/Future5/finallyshutdownNow-await10。oracleは手書きliteral/DDLの複合FK/一transaction条件、Productionによるexpected生成0。

必要closureは新Dataset1+FileBatch1+EntryBatch1+FileMap4+EntryMap3+Placement4+EntryRow1+Copy1=全16physical/8Main。新12+既FileBatch14+既6suite各12=whole98、同source/一exec/通常Root静的/CRC-init/四100/実Code差を記録。旧成功の確認再演や別source合算をせず、この新しい二batch接続に必要なscopeとして実施する。実Current/全件数/物理asset/hash/speakerFK/DB/COPY/transaction実行/Root/native/Actual4/aru/CHR/global451/ITSTは未完でHOLD解除しない。

追加不足.9/2.7/5.4（未較正）=内部詳細.05/.15/.3+製造12定義.4/1.2/2.4を一群.45/1.35/2.7cap3、必要normal98別群.45/1.35/2.7cap3。前FileBatchの旧費用/開始額/元SV上限保持、再確認や新12の繰返し加算0、専有実費/token null。端末空き約5.6GiBで小source/固定小fixtureだけを作る。大容量実masterやVM/DB作業は行わず、既容量条件を満たす別工程へ送る。
