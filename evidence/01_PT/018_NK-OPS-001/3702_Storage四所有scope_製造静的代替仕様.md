# Storage四所有scopeの製造／静的代替仕様

F03/411451/SS311333341343352354、原2/5/9pp cap10、IMPLEMENTATION/ADDITIONAL_FINDING。BUG2460五siteのうちFactory root/RootInspection no-op stream/OwnedTransfer independent child/close-race childの四siteをlexical ownershipへ。BUG036 async取得childとBUG2461 executorは本群で未是正のまま残す。

Factory: TWRを追加し元のclose失敗・二重close・slash拒否を保持。ordinary: 同じ既存streamをTWRへ、same rejectionとnull oracle保持。independent lifetime: parent→childの取得順・明示parent先close/child継続/child二重close/全postclose negativeを維持し、外側TWRを足す。close-race: parent,child,executorのTWR順で逆cleanupをexecutor→child→parentにし、workerの明示close・全latch/data/count oracleを維持。executorの生成をchild取得の後へ移すのは、worker開始前の資源取得のみ。Main/fixture/expected値の変更はない。

元三source/current29/全88/レビュー31を固定し、全transformを事前検査後に書込。format前後hashを分け、独立逆tokenは新scopeだけ除去して元sourceを復元し、close-raceのchild宣言だけ元位置へ戻す。元のexplicit close呼出しは残す。全他Java token/assert/入力の不変・scope欠落とcleanup順の否定を記録する。

own201 parse-only/formatと当三source PMD/CSのみ。元Test compile/run/native/Root/実FS/VM/process/DB0、代替fixtureなし。新XML/保持診断/既理由31から是正4を除く27を新hash/座標に束縛、目標raw88→84/非該当25+是正残2/未分類57。結果未確認を目標から実績にしない。元runtimeHOLD/実PTPASS-covnull/正式1964-53/工数nullを維持。
