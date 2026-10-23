# 1549 MonitoringPolicyEngine 単体テスト仕様書

2026-10-23、P018-09/NK-OPS-001/C07共有参照。SS351§7～10/SS-D044、UI252§5～6、RD MON005～013、PG-D521。4段階のpure部品を一経路へ接続する製造stage、見積1/2.5/5pp・上限10pp、共有7/残93/reset1793306748（開始0維持）。

不変ObservationContextは明示cause/UTC表示時刻/同owner単調elapsed Durationを保持し、null/負をconstructorで拒否する。これは実source/所有/原因撤去の証明書ではない。MonitoringPolicyEngineは12入口の生値を正しい閾値へ渡し、固定ConditionとServiceで同一AlertRegistryへ接続する。mode確認は既mode parser→4詳細service一致を返し、active状態を変更しない。collector/実clock/外部サービス/ログ送信/制御/永続化/配布は存在しない。実HTTP/MQ/DB/Root経路へ接続せずPT_DEFAULT。

| Test ID | 独立入力・期待値 |
|---|---|
|PT-OPS-MONPIPE-001|Contextの3getter/equality/不変値、各null/負Duration拒否。原時刻/明示cause/単調値が失われない |
|002|12入口の正常入力は空、11警告条件（integrityは非該当）の固定warning入力→正しいCondition/Service/level/count1/時刻。閾値期待値は1547のSS literalから独立に固定 |
|003|全12critical入力→同owner12active、正常化0/600秒・原因未確認は保持/確認時close、別Condition取り違え0 |
|004|負scalar/null Service/Contextは拒否し既active snapshot不変、失敗を正常としてcount加算0 |
|005|strict2mode/詳細4一致だけ正常、未知/mismatch/null拒否、既alertと無関係に不変 |
|006|64並行同TRANSFER/Web入力→一event/count64、独立caller終端、不正高cardinality key APIなし |
|007|全12×6入口の固定key対応/一覧72とimmutable snapshot、未知condition/文字列入力なし |

全7新PT＋既41必要同package回帰=48/6suiteを新sourceで通常verify。期待値はProduction threshold呼出しで生成せず、Test側のSS literal入力/固定Severity・Condition・countで検証する。新2Main classを含む全14実行class＋metadata1を四counter100/CRC/単一session・元XML/static/同sourceへ接続する。範囲外actual/Root/F03未受入を隠さず、C07/全体受入0のまま。完成単位として後続の全体compile/新artifact所有・byte整合を確認するが、許可されない全PT/実環境を試行しない。command/環境/source/hash/未実行は後続1550へ保存。
