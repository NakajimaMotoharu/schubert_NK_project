# 205 NK-OPS-001 Morning親M・A連続scope・単体テスト仕様書

Program ID NK-OPS-001、class/method `MorningControlScope.execute`（native factory/port境界）。RD OPS-009、UI251/253、SS341§4～5/343、SSC100～102/105、BUG315/YKT248、PG341。親の真のM・固定8停止pass・A・A下の全8fresh観測を一つのscopeへ結ぶ。原本resume、current INVALID、journal、backup/Cleanup、permitを代替しない。PG339外部mainへはまだ接続しない。

| Test ID | fixture・入力・操作 | 独立期待値 |
|---|---|---|
| PT-OPS-MCTRL001 | M/Aを別AtomicBooleanで保持、root・stop・fresh8・trusted workのeventを手書きで記録 | `root→M→root→stop8→root→A→root→fresh8→root→work→root→A close→root→M close→root`。stop時Mのみ、work時M/A両方、成功値7。SS341 SSC086/100/105から導出 |
| PT-OPS-MCTRL002 | M競合で空Optional、stop/A/観測/workは失敗spy | root1回・M試行1回、stop/A/観測/work0、固定IOException。競合を成功へ補完しない |
| PT-OPS-MCTRL003 | M保持中stopが既知IOExceptionを投げる | A取得0、work0、M close1、原例外identity保持。これは前段policy/確定拒否fixtureでありhandle不明UNKNOWNの通常unwindではない |
| PT-OPS-MCTRL004 | stop確定後A競合 | stop1、A試行1、A内観測/work0、M close1、固定IOException。stop前の観測をA後へ流用しない |
| PT-OPS-MCTRL005 | A取得後fresh全8がIOException | work0、A/M close、原例外identity保持。INVALID/変更0をspyで確認 |
| PT-OPS-MCTRL006 | A内workが未知Runtime、またはnull。API引数null | 未知Runtime同identity、null契約違反。成功値へ変更せずA/Mを両方close。NPE catch正常化なし |
| PT-OPS-MCTRL007 | 別threadのstop callbackをlatchで未解決に保つ | 未解決中はM保持、A未取得、future未完了。解放後だけA/whole fresh/workへ進む。timeoutや割込を実端末成功にしない |

ExpectedはSS341の順序と手書きeventから算出しProduction methodでexpectedを生成しない。全fixtureのlockは呼出順・closeを測るPT用portであり、真正systemd/flock/cgroupを偽装した受入ではない。MROOT/MPASS/MCLIENT/MTERMS/ADMISSIONLOCKの既存suiteへ関連づけ、実A取得/8Unit/原本とstart handleなしUNKNOWNのhard-timeout保全は後続native負試験で判定する。Command/環境/branch/commit、F/E/S、4coverage、静的、BUG/SSC、sanitized evidence path/hashは206へ記録する。coverage除外・skipped合格算入なし。
