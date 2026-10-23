# 1708 Batch integrity metric 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171/UI252/SS341351/PG-D566。IntegrityFailureMetricRecorder constructor/record/detailedMetricsRequested、Area.parse/values/valueOf。新INTEGRITYMET001..008＋必要既Batch245を当253/33で普通実行予定。SS351 `nk_integrity_failures_total{area,step}`、Hash/path/configの三分類を内部Area HASH/PATH/CONFIGへ閉じ、stepは既BatchStepの十値だけ。DEBUG30counter事前登録/STD詳細0、既MonitoringModePolicy strict契約を再利用する。Batch供給失敗eventの計数部品であり、全サービスの検査/分類/実失敗/永続incident/調査・修復/手動退役/保護警報auto-closeを実装・認定しない。

| Test ID | 目的/fixture・操作/独立期待値 |
|---|---|
| INTEGRITYMET001 | 手書3area×SS341十step=30series、Counter型・label key2・初期0、ID/path/body labelなし |
| INTEGRITYMET002 | 全pair一回＋三回供給→各4、HASH/BACKUP_DBだけ一回追加→5/他4、系列数不変 |
| INTEGRITYMET003 | strict area literal→各typed定数・未知/空/小文字/null拒否、全values配列独立/valueOf/未知/null、生成2直接契約 |
| INTEGRITYMET004 | DEBUG/STDのnull area/step拒否・既値不変、STD全pair登録/増分0、constructor null/未知mode拒否 |
| INTEGRITYMET005 | 第二counter factory Runtime/Error同一identity・呼出2/残1/close0、caller finally close1 |
| INTEGRITYMET006 | increment前/済み後のRuntime/Errorは同一再throw・一回/補償/close0、partial増分を保持し成功へ変換しない |
| INTEGRITYMET007 | 64fixtureのpairをproduction呼出前に独立集計し全30へ照合、有限future/別owner7と系列30不変 |
| INTEGRITYMET008 | foreign Gauge同seriesをCounterへ置換せず例外・同一meter/値7/close0 |

既BatchStepは十enum literal/backup booleanだけのpure初期化で全source読取済み、既Batch metricでも利用中。新Areaはpure enumだけ。port接続/実file/hash/DB/key/config検査・Root/VM/Backup/配備操作0。SDK故障をformat/cause探索/catch正常化/retryしない、実hook/source/owner/asOf/namespace/filter/exporter・業務exactly-onceは未受入。期待値はSS341十step・SS351三分類/labelと手書fixture入力で独立生成、production methodからexpected算出0。

7788 ordinary253/33→7790独立四100/CRC/static→7792正常六compile/PT0→7794全1772（当Batch63/歴史API26-Web14）→7796全119/103trace→7798生成新2＋既120・raw全個別理由→7800公開scan、1709結果へsource/run/実日時/OS-JDK-tool/branch/command/exit/XML/input/期待/実際/coverage/BUG/hashを結合。開始3/5/9pp上限10/fresh receipt→eventへ固定、原-v4-v5/旧markerlast27区間/累積・専有N-T/工数null/元90再基底化0。正式1964/53/原190新受入0/QA051final/PTALT0/whole451-native-CHR/actualHOLD維持。
