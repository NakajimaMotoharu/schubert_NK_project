# API Outbox観測source cache・製造/単体仕様

2026-10-25、PG-D631/NK-OPS-001/WBS-P018-09、C07 shared追加予算0。RD171/UI252/SS311/332/342/351、既1852-53/1664/1671に対応。開始HEAD3ec4d9ca49fe694a9fe828e39d3cefcb1992b13f、製品73d94fc525c6ea8828ca82d906ec583146fee7bf、fresh52残48/reset1793382075、開始低2/基準5/高9pp・群cap10を固定する。元/v4/v5見積り、正式1964/53、原190新受入0、工数null、QA051 final、全actual HOLDは変更しない。

SDK非依存ApiOutboxObservationSourceだけを製造する。resource-free ctorとget/missingはSQL/worker/SDK/transaction操作を行わない。明示observeはcaller借用のRO/read-committed/non-autocommit ConnectionとasOfを既Repositoryへ渡し、Statement/ResultSet close完了後のimmutable Snapshotだけ公開する。writerだけ直列化、get/missingはwriter待ちなし。observe開始でmissingへ戻し、失敗時はmissing/元例外維持。fresh Entry identityによるCASでmissing後の遅延完了を再公開させない。欠測NaNと成功empty SQLの既知zeroを区別する。STANDARDはSQL未読、null境界は状態変更前に拒否する。未知/null modeは既parse契約。

新OUTBOXSOURCE001～020を予定し、実装前の未実装失敗はTDDとして区別する。独立oracleは手書きCounts3/5/7・Age2/4/6秒、固定SS wire literal、fake JDBCがConnection変更/close・未知操作を拒否する。初期/更新/empty/null/mode/SQL-Runtime-Error/RS-PS close/並行writer/読み中missing/繰返しmissing ABA/サービスrefresh無SQLを検証する。latchは必ずfinally解除・bounded await/join、sleep同期なし。Fixture outerはcompile-only。必要既ApiService16を回帰し、既DAO10/HTTP22の確認だけ再演はしない。現実DB/driver/native/worker/poll周期/生産callerは未接続でHOLD。

source固定→9042 normal六compile→9044選択36/2予定→9046外側とprivate Entryの全Main（分岐なしEntryのbranchは実0/0=NA、除外/偽100なし）実coverage・NPE静的→9048全物理/旧byte不変/所有/5architecture→1855結果/計測/公開scan/commit/push。適用性未分類は合格へ加えず、既collectorの根拠を新cacheへ無条件流用しない。初回群の成功だけで全体受入・IT/ST完了にはしない。通常区切りで停止せず、許可済み後続へ進む。

