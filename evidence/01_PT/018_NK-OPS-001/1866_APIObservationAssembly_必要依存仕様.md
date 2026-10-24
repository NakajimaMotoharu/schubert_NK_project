# API観測assembly・同経路必要依存仕様

2026-10-25/WBS-P018-09/group2098、sourcefdc229c9a/保存HEADfcf3b0d4a。開始0.5/2/4pp・cap10、fresh56残44、元/v4/v5固定。直前44と全4222の確認再演をしない。新PG前に正式mainのSS342/351と現caller/Lifetime/Manager/context/worker/pump/attempt/binding/ResourceScope/retentionの12公開artifactを限定照合する。

| ID | 着手・終了依存/確認する独立根拠 |
|---|---|
| ASMDEP01 | 現callerは既Poolから管理SDK contextを先に保持しinitialize、Managerは借用contextで内側。新workerとRO attemptはPoolより内側で保持し、UNKNOWN停止時はSDK/Pool以降を解放しない。 |
| ASMDEP02 | ApiProcessLifetimeはstop/fail通知だけ。API Unit60秒、Manager既30秒、親30分を新たなworker待機時間へリセットしない。workerの残時間supplierは既予算を借りるが現callerは未供給。 |
| ASMDEP03 | STDは詳細SQL/workerを起動しない。DEBUGだけ借用Poolの独立RO attempt→cleanup-confirmed cache→SDK metadata。SDK renderへJDBC I/Oを入れない。 |
| ASMDEP04 | failure通知はlifetime.failを呼ぶ責任、UNKNOWN retaining policyは取得前準備。新assemblyをcallerが初期化前に保持し、worker停止確認後だけSDK closeへ進む。実Main接続と実停止/nativeは別HOLD。 |

実toolのPATHS重複/存在/原source byteを確認する。限定metadata反例は製品PTに加算しない。既受入/正式1964-53/原190新受入0/工数null・QA051final/HOLDは不変更。結果1867から明示remaining port付きassemblyの普通fake PG/PTへ進み、実API/DB/VM/Root/配備/鍵/UNKNOWN拒否操作を試さない。
