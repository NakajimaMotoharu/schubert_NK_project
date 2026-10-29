# 監視collector七Main十四指摘：製造静的仕様

2026-10-30 source6b53/dev-foundation、保存97f21ca6fa634372e90125fe77af4cd911877f7d、PG-D891。群3042原0.5/2/4pp cap10。前段selection読取/準備を遡及せず、新規PG受入と再認証/tool費を分離する。新Product/PT/JVM/実DB/VM/鍵/配備/回収操作0、拒否PTの試し実行や代替実行ではない許可済みPG source review。

## 対象と独立根拠
Main324行を全body確認：API AsyncJobMetricCollector45/DbPoolMetricCollector44/MqPressureMetricCollector48/OutboxMetricCollector53、Web MediaStreamsMetricCollector45/WebDbPoolMetricCollector44/WebOutboxMetricCollector45。canonical ownerは各WBS-P018-09。原指摘PMD00352/353/355/356/361/362/364/365/07377/378/380/381/383/384の十四IDだけ。既raw6247/参照3682/pending2821/未参照2565の歴史複数source domainを保持、確認済み同期lock指摘を再計上しない。

SS351§6/8/10・RD171/UI252（origin/main byte一致）に基づき、観測不能を真0/成功にしない、STANDARDの詳細収集なし、機密例外/labelを出さない。generic catchは観測失敗時のowner snapshot無効化＋同一Throwable再throwの境界であり、正常化やretryではない。borrowed Connection/MXBean/Functionは取得/close/transaction操作せず、private lockがread→publicationを直列化。API outboxの部分record故障はrows/ages/lastObservationを全クリアするが、exporter全family横断のscrape atomic性を主張しない。

missing()の実bodyはAtomicReference.set(empty)又はconstructorで事前構築したclosed enum-map rowの同操作のみで、外部provider callback/文面format/例外graph走査を行わない。nonnull事前条件はcatch外で拒否、port違反null/NPEをcatchしても同一失敗再throwで正常扱いしない。実DB/broker/source所有/deadline・runtime結線・global観測一貫性は未実証を明記。

## 検証・command・期待値
`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14370_monitor_seven_failure_fourteen_context.py`。独立14372は元PMD XML/十四raw重複occurrence/Source bytes/ASCII位置/token/ownerとsource-specific guards順序を別計算で照合。raw消去/任意suppress/閾値/正本変更なし。current normal14216・元測定13253の各hashを区別し、同byte対象だけ原座標へjoin。新source全静的測定を実施したとしない。

期待値は各Mainの上記独立資源/失敗契約、Test計数・coverageはnull/新PT0。18metadata改変＋全guard削除反例を検証し、実raw14は残してcurrentWholeJoinPendingをtrue、qualityGatePassをfalseに保つ。結果2654/manifest/hashへ。正式1964-53/歴史17-190/工数null/QA051final/全F03-451/動的HOLD・原本保全維持。

P00501は1525/488で既別source新規受入済みだったため、481の歴史NOT_ACCEPTED表示だけを根拠に再受入/新規出来高へ数えない。今回の静的14や元198をその新受入へ振り替えない。
