# 1714 DB query duration取得結線 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171 MON006/010～013/UI252/SS332351/PG-D569。DbQueryDurationMetricCollector constructor/collect・Observation compact constructor/outcome/elapsedNanoseconds/equals/hashCode/toString。既1712のQuery二値/Outcome二値と秒recorderへ借用Function<Query,Optional<Observation>>を結線。private owner lockでread→complete/null/invariant検証→publication→同一Optional返却を直列化する。STANDARDはsource未呼出。欠測/Runtime/Errorは観測eventなし、成功0秒やFAILURE時間を捏造しない。完全供給FAILUREは正当な一観測として記録し、真の0秒eventとmissingを区別する。provider/registry/connection/clockの所有・一意性・外側期限は新たに主張しない。

| Test ID | 事前fixture/入力/操作 | 独立期待値・観点 |
|---|---|---|
| DBCONN001 | 二Query×二Outcome、各0.5秒、read中countを確認 | read完了前当pair0、返却同一Observation、後count1/sum.5、全4呼出/registry close0 |
| DBCONN002 | Optional.empty→FAILURE 1ns→empty→SUCCESS 0ns、各query | missingは増分0、FAILURE1/count1/sum1e-9保持、真0はSUCCESS count1/sum0、全8read/4record |
| DBCONN003 | 初回.25秒後Runtime/Error、別source nullOptional、nullQuery | 元Throwable identity/既値保持/追加failure event0、nullはNPE異常伝播/未正常化、query nullはsource未呼出 |
| DBCONN004 | ctor source/registry/mode null・空/小文字/未知mode、STD二query | 境界拒否/CONFIG_INVALID、STD read/factory/record/全meter0、nullQuery仍拒否 |
| DBCONN005 | null/負-1/MIN、0/1/MAX Observation、equal/別Outcome/別time/null/型違い | ctor invariant・literal accessor、record五生成contractを独立typed値/文字列/配列で確認、同値hash整合 |
| DBCONN006 | 自己所有二Thread/latch、first readを保持して後続workerが先行ownerを実待機 | first publication前record0/source1、解放後second source内first count1/sum.25、後SUCCESS.25/FAILURE.5各1・有限5秒future/finally解放 |
| DBCONN007 | 64入力のquery/outcome/nsと独立count/sumを呼出前集計、別registry | 元Observation identity/全pair期待count/sum、差1nsを検出するtolerance1e-12、別owner1秒・既owner64不変 |
| DBCONN008 | SDK factory第2 Runtime/Error、別registryの記録後failure | provider未呼出/primary1＋補助6/borrowed close0、partial count1/sum.5と元identity保持/再試行・補償0/caller finally close1 |

自己所有固定Clock、既SDK summary/同histogramを使用し、SQL/DB/JMS/実時計/Root/VM/process/配備操作0。新8＋必要既API138を当146/18、正常六compile/PT0を別snapshotで固定sourceから実行予定。原138を新sourceへ転用しない。独立post36Java/実30＋metadata1/CRC0/四counter100、全1779physical（当API31/歴史Batch65-Web14）/全125delta-110追加physical、生成既45＋新record5/raw全個別理由を1715結果へ記録する。実collector scheduler/source真正性/時間測定/hook/exporter/backend・whole451/native/CHRは別未受入。

group1937、着手前3/5/9pp上限10/fresh9残91/reset1793382075（PG7870 fresh receipt）。Production source固定前は新PT未実行。元-v4-v5/旧markerlast27区間/共有累積・専有N-T/工数null/元90再基底化0、原190新受入0/正式1964-53/QA051final/PTALT0/全actualHOLD不変更。期待値のproduction生成/skip算入/既成功だけの再演は禁止。

## 2026-11-24 排他方式の是正

BUG-3748／YKT-2929。私有ロックで供給→完全値の公開を直列化し、正常・STANDARD・例外すべてでfinally解放。DBCONN006は自PT workerの待機先と旧期待を照合する。旧0件、先行が公開した成功0.25秒、後続失敗0.5秒、欠測と真の0秒の区別を維持。PG43814の通常八ケース、CollectorとObservationを同じexecで測定する。実DBは不要。
