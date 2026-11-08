# MVC template 原38 有限owner・専用cwd仕様

G03.05 REWORK 2/5/9pp cap10、BUG2540/YKT2177、UI223234235/SS313323。原Animation8/MusicHierarchy6/ScenarioDetail8/Search8/Log8全38、元get10/64並行render・全literal/DOM/静的CSSJS期待を保持。二resource TWRのpool8をcontext内の明示try/finally shutdownNow/awaitTermination10assertへ変更し、context closeより先に所有threadの終端を確認する。

全38fixture/Source/currentWebMvcConfiguration・Beanとconstructor・SDKを先行確認。@EnableWebMvc sliceの明示3controllerBeanのみ、component scan/Productionbootstrap/Root/client backendなし。MockServlet GET/HEADの静的resourceと直接view.renderのみを特定し、実HTTP/server/session/auth/DB/JMS/key/VM/native/held四実行を含まないことを確認した場合のみ通常PT。対象未特定/安全前提未確認は当範囲HOLD、PG/静的は継続。

既存target/scenario-screen-traces保全のため、Unit専用new-only cwdへ現normaljarとGitに一致した公開CSS/JS/HTMLだけcopyし、元の相対path挙動をそのまま用いる。コピー元は公開Production resourcesのみ、原本/master/private物にアクセス0。全fixtureを変更後一回、独立XML/真正終端/class-init/currentCRC/必要coverage/出力hashを照合。元sourceはGitobject保全、nested構造の逆変換後に同formatterを工具として適用して元canonical全byte一致を確認、期待値や文字literalを正規化しない。

SDK20（既13＋Servlet/test/webmvc/securitycore-web/observation-commons）は既存toolchain/currentWebpomの版/hashを固定し、JDBC/JMS/serverdriverをCPへ追加0。Unit対象compile/static/最小preflight、source固定後全38 F/E/S/aborted0。対象WebMvcConfiguration限定counterは自然0をN-A/null、全体四100/Browser/IT-ST/正式受入へ転用0。TestIDは元38とPG24522manifest、環境/command/source/input/期待実際/coverage/hash/BUGを一意に対応。新unique/Source登録/leaf0、全HOLD/正式1964-53/工数null維持。

## 実Source観測による着手前仮定の訂正

PG24510 preparation記録: executor変数はpool三/executor二、Searchのtrace書込はcontext TWR外、元Future上限はSearch20秒・他四10秒。開始文の一律get10は初期仮定であり、実装・期待・元eventを巻き換えず全原10/20を保持する。原2/5/9cap10見積不変更。
