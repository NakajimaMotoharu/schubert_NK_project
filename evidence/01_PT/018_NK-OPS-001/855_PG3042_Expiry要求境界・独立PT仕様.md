# 855 Expiry要求の原本時刻・固定grammar境界PT

Program NK-OPS-001、主担当WBS-P017-07/費用leaf P017-07.02（.01/.03へ二重計上0）、CleanupWorkerRequest.Expiry/PriorExpiry/consume、OPS009/BAK001/UI251/SS341・342・343/SSC104111117、451。Mainはa9/PG2802から変更しない。Testだけの新群、開始見積り0.3/1/3週次共有枠pp（events0792）を固定、他費不明のため実費null。

PT-OPS-EREQ3042-001: literal run/cutoff/startで独立構成し、終端=start/1microsecond後/9999年末microsecond上限を許可、開始前/1nanosecond過剰/10000年/開始nanosecond過剰を拒否。四nullable原本identity fieldはconstructor契約で拒否。redaction文字列が固定で、時刻・UUIDを診断へ含めない。所定例外をassertしcatch正常化しない。これはclaimの形状契約で、削除権限の獲得ではない。

PT-OPS-EREQ3042-002: 独立literal NKEXPIRYSKIP2 goldenの全16必須fieldを一件ずつ未知keyに置換。原本開始/終端のnanosecond、終端年上限、原本ID/attempt上限超過も拒否する。全失敗入力byteは消費後全0と照合、parserのProduction encodeをexpected生成に使わない。正常/境界/異常/欠落/nullを対象とし、並行・再送は既EREQ suiteの既試験を参照、本群でnative処理やDB削除を発行しない。

実行条件: 独立JUnit class launcherで既全3685/542/1643/static0のexact3026 jarsと既fixtureをhash固定し、新Test-only一classをjavac -Xlint:all -Werror、全ExpiryWorkerRequestTest六methodを実行する。正常既存四methodと新二methodを一緒に実行しFES/aborted/notRun0、XML・agent exec・対象class counterを記録。全体3687への統合は後続変更群とまとめて必要時に実施し、旧3685を新Test全体合格へ読み替えない。静的/全branch未実行分は未完を維持。旧仕様文は五＋二=七と誤記したが実runnerは@Test六件を取得、BUG1264/YKT1030で是正し原input/XMLは保全する。

実結果: PG3044/exec5693 actual0、source5d2b2f0ad、新Test二を含む実六/FES-aborted-notRun0。XML SHA256=808937cf9871b1376cdc8be1517ae538f152004a2c17499cf7d53e9842c7b3da、server manifest0c93385d382a994a49357ca03cae40ad9d0bb22c29284d2a7e1e8740431692b6、payload4e82a8e0、execa2c8faf7、coverageXML720528b3。PriorExpiryは13L/2M/1C全covered、BRANCH11covered/5missedで四100未達（旧hostのみ7missedから二分岐減）、native合算/全体加算0。実command=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<記録済pyflakes> python3 -B tools/quality/pg3044_expiry_boundary_selected.py`、PG379/pg3044-expiry-boundary-selected-v1/manifest.safe.jsonとaru PG3044-candidate-v1原XML/logを保全。環境=既記録Java25.0.4・Linux aru、秘密情報を含まないsynthetic fixtureだけ。Productionが期待値に違反すれば修正前BUG/YKT起票する。新未実装機能のTDDではないため既処理の失敗を無条件にTDD扱いしない。
