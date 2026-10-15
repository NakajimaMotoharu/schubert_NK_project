# 855 Expiry要求の原本時刻・固定grammar境界PT

Program NK-OPS-001、WBS-P017-07、CleanupWorkerRequest.Expiry/PriorExpiry/consume、OPS009/BAK001/UI251/SS341・342・343/SSC104111117、451。Mainはa9/PG2802から変更しない。Testだけの新群、開始見積り0.3/1/3週次共有枠pp（events0792）を固定、他費不明のため実費null。

PT-OPS-EREQ3042-001: literal run/cutoff/startで独立構成し、終端=start/1microsecond後/9999年末microsecond上限を許可、開始前/1nanosecond過剰/10000年/開始nanosecond過剰を拒否。四nullable原本identity fieldはconstructor契約で拒否。redaction文字列が固定で、時刻・UUIDを診断へ含めない。所定例外をassertしcatch正常化しない。これはclaimの形状契約で、削除権限の獲得ではない。

PT-OPS-EREQ3042-002: 独立literal NKEXPIRYSKIP2 goldenの全16必須fieldを一件ずつ未知keyに置換。原本開始/終端のnanosecond、終端年上限、原本ID/attempt上限超過も拒否する。全失敗入力byteは消費後全0と照合、parserのProduction encodeをexpected生成に使わない。正常/境界/異常/欠落/nullを対象とし、並行・再送は既EREQ suiteの既試験を参照、本群でnative処理やDB削除を発行しない。

実行予定: 独立JUnit class launcherで既全3685/542/1643/static0のexact3026 jarsと既fixtureをhash固定し、新Test-only一classをjavac -Xlint:all -Werror、全ExpiryWorkerRequestTest七methodを実行する。正常既存五methodと新二methodを一緒に実行しFES/aborted/notRun0、XML・agent exec・対象class counterを記録。全体3687への統合は後続変更群とまとめて必要時に実施し、旧3685を新Test全体合格へ読み替えない。静的/全branch未実行分は未完を維持。

結果/command/source/hash/対象counterは実行後追記。環境=既記録Java25.0.4・Linux aru、秘密情報を含まないsynthetic fixtureだけ。Productionが期待値に違反すれば修正前BUG/YKT起票する。新未実装機能のTDDではないため既処理の失敗を無条件にTDD扱いしない。
