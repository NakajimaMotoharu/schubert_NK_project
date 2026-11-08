# Login・User表示 原28 有限executor所有仕様

G03.05 REWORK 1/4/8pp cap10。BUG2533/YKT2177。UI225/226/236、SS313/314、QA055承認固定文。

原Login8/Locked4/UserCreate8/UserDetail8を全method保持し、Future10秒に加えfinally.shutdownNow→awaitTermination10秒assertを4ownerへ実装。異常時もcleanupを有限化し、全他rawbyte/期待値/annotationは逆変換で不変検証する。

実施前: 全fixture/source/SDK/読込resourceとfragment閉包を確認、製品Java CP0、MockのGET表示のみ、実HTTP/POST/login/session/アカウント/権限/DB/Root/VM/native/実鍵は0。固定期待DOM値は元Testの独立literal、production値からexpected生成0。

新source固定後、変更4fixture全28を単一jobで実行、F/E/S/aborted0、元XML全caseと一致。独立postで固定source/hash・元全rawbyte逆変換・各DOM出力hash/redaction・SDK init閉包・所有終端を照合。HTML対象につきJava coverage null/N-A、旧execや人工100を加えない。正式受入/新unique/leaf/source registry加点0、全HOLD維持。証跡は016/PG24416へ格納。

実行: PYTHONPATH=tools/quality python3 -B evidence/01_PT/016_NK-WEB-002/input/041_login_user_dom_bounded_qualifier.py prepare|static|preflight|run|post （run/post source必須）。
