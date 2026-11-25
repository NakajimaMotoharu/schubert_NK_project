# NK-PRO-002 Protocol並行試験の終了時診断

対象はProtocolの試験用 ProtocolFixtureWorkers と、SS322・323・354、UI234・235で固定された既存の並行試験。BUG-3911、YKT-2997。製品の変更はない。

| Test ID | 入力・操作 | 独立した期待値 |
| --- | --- | --- |
| PT-PRO-002-P09 | 8 workerでログイン要求の固定入力を同時encode | UI234のオフセットから手で固定した384 byteへ全件一致。元の10秒Future期限とLatch解放を維持。 |
| PT-PRO-CATALOG-STATE001 | 同じ64 layoutの列を2 workerが独立TSVから照合 | 元TSVの64組と両方が一致。元の10秒待ちとLatch解放を維持。 |
| PT-PRO-QA054-011 | 独立した2 workerでREQUESTとMENU_VIEWEDをencode | UI235の独立byte期待値と個別に一致。元の両10秒期限を維持。 |
| PT-PRO-WORKER001 | 一次AssertionErrorと固定の待機失敗を同時投入。別の代理では終了失敗だけを投入。 | 一次例外は同一実体。抑制1件はAssertionFailedError。単独失敗は呼出側へ返る。各代理の呼出順はcancel、10 SECONDS。 |
| PT-PRO-WORKER002 | 一次AssertionErrorとJavaのInterruptedExceptionを固定代理で投入。 | 一次は同一実体。抑制1件に元割込みをcauseとして保持。割込み旗を再設定し、試験側で片付ける。 |

製品JAR、元TSV、試験ソース、XML、コマンド、終了コードをPG45670の証跡で固定する。変更対象の選択実行。六製品全体の451および実通信への判定は残る。
