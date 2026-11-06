# 既資格索引 metadata仕様

NK-OPS-001/WBS-P015-02、477/478/487・BUG2335/YKT2080。PG20454/4011の候補SavedScreenTargetは元836/PG19348既全8証拠の発見で追加製品実行をしない。起票時の全公開manifest/source pin照合とnegative metadata確認を075 strict版・076 legacy版へ実装した。予算は4011原0.5/2/4pp cap6のまま、S/Vへ付替えない。

Tool契約は公開path/hashの再帰抽出・Main whole sourceだけのpin・未成功/中断/skip/union/除外の非索引化・未知schemaの保持・同byteとdriftと不明の分離。独立literal fixtureと実PG19348の固定SHAで076の7checkを検証。絶対pathは当repoの公開evidenceへ限定し、private/raw/VM/DB/process/held二source/RootFailed二sourceを読まない。legacy側は既sidecarのactualSourceRunBound=trueとMain pin参照だけを索引へ載せる。既成功と現在の全依存/期待値/後条件の同一性を認定しない。索引に無いものはUNKNOWNであり新規実行の許可ではない。

実commandは `python3 -B evidence/01_PT/018_NK-OPS-001/input/076_known_source_evidence_index_legacy.py evidence/01_PT/018_NK-OPS-001/evidence/PG20458-known-source-evidence-index-legacy-v1`、再実行禁止（new-only出力）。元075/PG20456の6checkはstrict schemaだけの途中版として保全。実結果/OS/Python/実終端/入力SHA/全参照hash/除外理由は3589/978とmanifestへ記録。metadata7はProduct PT・coverage・新Source資格・WBS受入へ足さない。修正commitはpublication後のGit byte照合を追記する。
