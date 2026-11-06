# UnitStateParser 固定byte単体仕様

Program NK-OPS-001、UnitStateParser.requireStopped/valid、OPS009/UI251/SS341343、原PT-OPS-STOP001..004/追加PT-OPS-STATE-BYTE001..006。対象の費用主担当は503/485のP01804。014着手の02は転記誤りとして元欄を残しeffective04へ追記訂正、原1/3/5pp cap8不変更。正式・親全体・実停止/実環境受入とは別。

| Test ID | method/入力 | 独立期待値 |
|---|---|---|
|001|exactSevenFieldsForBothUnitsInRotatedAndReversedOrders|API/Webの固定7lineと回転/逆順28解析、受入・全byte不変|
|002|byteLengthAsciiAndNullBoundariesRejectWithoutChangingInput|null二境界は明示契約拒否、0/1024/1025byte/不正6byte/合法ASCII端32・126だが不正IDはMALFORMED_STATE、変異無し|
|003|framingEqualsUniquenessKeysAndIdentityAreStrict|LF無し/6・8line/=無し/空key/複数=/重複2/未知key/別unitをMALFORMED_STATE|
|004|eachNonStoppedValueIsRejectedWithFixedReason|Load/Active/Sub/Job/MainPID/ControlPIDを各独立不一致、全NOT_STOPPED・固定診断・cause無し/suppressed無し|
|005|failedProjectionDoesNotPoisonSubsequentIndependentBytes|失敗後2回正規7lineを受入・入力不変、cache/共有中間状態なし|
|006|independentMemoryProjectionsDoNotShareIntermediateState|2worker32配列のAPI/Web交互、戻りの独立固定Idと一致・所有workerはTWR終了|

Oracleは007の7固定行Id/loaded/inactive/dead/空/0/0とASCII/7一意/1024規約。Productionからexpected生成なし。1024bytesは長さ境界を通過後に構造で拒否、1025は長さで拒否。未知の7fieldを成功としない。外部コマンド・状態取得・Process/SystemctlStateSource/ApplicationStopGateを呼ばず、enum/診断型以外のProduct初期化をpostで禁止する。null拒否を成功入力とは扱わず、NPEcatch正常化なし。

実行: PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/012_acceptor_parser_port_qualifier.py prepare|static|run|post evidence/01_PT/018_NK-OPS-001/input/089_unit_state_parser_bytes.json [frozenHEAD]。Linux/JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15、compile/staticの後にsource固定し一回だけrun、strictpostでXML6/全physicalclassCRC/session1/四countermiss0を照合。旧exec合成・手動除外・constructor反射実行無し。coverage未実行の時点ではnull、詳細結果3593へ記録する。

BUG2354/YKT2099:旧normal20112の資源三差でguard終了1・slot未作成。是正中のPythonindent誤りもUnit無しとして保持する。normal20704 fb189と当current入力を結合。静的20114 D8は旧新全Main Java/POM入力一致と全1844class code/debug byte一致を明示しJava静的のみ再利用、旧PT/実環境成功の移転ではない。Main再compile/全回帰確認再演はしない。原実装/Mainは不変更。
