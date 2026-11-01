# 3404 API default bind 原一件PT仕様

Program=API管理HTTP/ApiManagementServer.bind,start,promote,close。関連RD現行互換・UI264・SS342/SSC158312313、原Test ID PT-API-MGMT-NORM-001。PG17540群、現source6b53efeec87f3ec36a840dd8e7759656cb4aee5c、branch dev-foundation、開始HEAD68c3b944。Main SHA81c29219808b8c38764d7bcd9ec1d1e7fc32a709a158a0399237e7fe5d46cb5cは17389全体読取と一致、再読を新実績に数えない。原ApiManagementDefaultBindTest全78行とget helper再確認、SHA d12fa4fa382555316c3f280ec1040bb8850839dc4db146c816262c3157b75e82。

## 入力・操作・独立期待

全original method apiMgmt001DefaultBindUsesFixedLoopbackAndOwnedReadinessLifecycle一件のみ、抽出/改変なし。固定127.0.0.1:8091を自己所有し、Java HttpClient/Serverだけ使用。入力commitは公開fixture「7」40文字、app0.1.0/config1/schema025/protocol001で実署名/BOM/schema資格ではない。connect/request各3秒、全JVM上限180秒。初期ready=false/readiness503とliteral {\"status\":\"DOWN\"}/Cache-Control=no-store、promote後callbackちょうど1/ready=true、health200とliteral {\"status\":\"UP\"}、info200と明示順commit,app,config,schema,protocolのliteral JSONを検証する。expectedをproduction methodから生成しない。TWR終了後ready=false/二重close後callback依然1、ServerSocket自己8091再bind成功で所有解放を確認し両client/socketを閉じる。

## 観点と範囲

正常・ready遷移・二重close境界を当methodで確認。null/例外/他metric context全分岐は当一件未網羅、既API11の資格を保持し再実行/exec合算しない。whole Mainのouter CodeとFactory genuineNoCodeを当execから独立測定するが旧fullSource/counterを上書きせずscope追加のみ。四counter100未主張。実network数/JDK thread数は未測定null、外部接続/業務assembly/Root/Unit/DB/VM/実native操作なし。固定portが他owner使用中なら失敗として保存し、相手を停止/探索しない。

## 実行・証跡

実行command=python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17540_api_default_bind_one_pt_v1.py。既正常14216六Main compile/14224静的0/SDK/reporter資格をpin再認証し再buildしない。新helper17533メタデータ7+8+8、新fixedenv17534=5+3否定とstub1を先行、どちらも製品実行0。準備失敗17532はBUG2210/YKT1957として保存、新17533へ分離。raw/post/独立oracle/CRC/registry/WBSのpath/hash・環境・command/終了値・coverageは3405へ追記する。Failed/skipped/未確認はPASSへ算入しない。正式1964/53、QA051/F03/451/HOLD不変更。
