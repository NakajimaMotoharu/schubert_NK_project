# Process照会所有・例外優先順位 PT仕様

再是正追補: v2/936/元5950も1164成功だがstatic四指摘で最終1、成功へ算入しない。getter/Start前wrapperのconstructorはnullable参照storeだけ、取得を囲むowned actionの冒頭でrequired()して直ちにnull拒否し、その後だけ次getterへ進む。null wrapperのcleanupは実資源0を確認してno-op、nullをbody成功にしない。Systemctlの三getter後拒否とは分離する。これにより未知valid-resource取得後のcall/heapをconstructor成功経路へ置かず、静的抑制・不可能branch除外無しで再資格する。

是正追補: 053b1aacb/PG5404-v1元34092は1163/137試験FES0だがstatic二件で最終1、BUG1447/YKT1211を修正前起票。有効resource返却後のcallを増やさずnull側のみObjects.requireNonNull、NPE型/即時拒否を維持する。NativeReaderの未網羅9行6branchも同群で閉じるため、package限定monotonic port（native既定System.nanoTime固定・外部override無し）を追加し、QUERYOWN007で取得前invalid、wait前期限0/有限wait false/非0exit/wait後期限0、阻止drainのget timeout/interruptとfinally cancel・全所有closeを固定tick/別latchで決定的に確認する。試験目的のsleep・時間競争・Production expected生成無し。新source v2予定1164/137/論理1155/独立105、whole予定3896/562/1664未実行。初稿六method/1163は初回source履歴であり現行へ合算しない。

NK-OPS-001 / OPS009 / UI251 / SS341343354 / SSC308 / BUG1414・YKT1178 / PG-D432。
対象はSystemctlStateSource四箇所・InspectorUnitProbe.NativeReaderの通常/streaming各四箇所、ProcessResourceScope.acquire、StdIo/SafeStream/QueryProcess。原237分類の残十二を対象とし、全工程・実VMの受入ではない。

全callbackは取得前に生成し、ラッパーNEWとconstructor開始を実getter/Startより前に置く。返却後の成功経路はcast・参照格納・returnだけ。ProcessResourceScopeはcommonのIO正規化を持ち込まず、旧useのIO/Interrupted/StopGateと未知Runtime/Errorの優先順位、interrupt再設定、固定secondaryを保つ。旧useのopcode/handlerも独立照合する。Systemctlは三getter後にnull admission、Inspectorはgetterごと即時拒否という異なる既契約を維持する。streamingの残期限/virtual drain/早期stdin/stderr一回close/キャンセル、固定command/env/読取上限/zeroizationは変更しない。

新Test ID QUERYOWN001..006（ProcessResourceScopeTest六method）:

- 001: 正常/IO/Interrupted/StopGate/Runtime/Error × cleanup正常/StopGate/Runtime/Errorの全24、固定winner行 `Ncre/bbce/bbce/bbce/bbbb/bbbb`。bはbody、その他はcleanup identity。旧useも同じ独立表で確認し、その結果から新expectedを作らない。known body＋unknown cleanupだけcleanup優先、Interruptedならflag保持。その他body優先＋固定COMMAND_FAILURE secondary。
- 002: factoryのIO/Runtime/Error identity、三null portはfactory未呼出、null返却はbody/release未呼出。
- 003: 既suppressed/同一Throwable再使用のidentityと固定secondary、self-suppression防止。
- 004: 二並行scopeをbarrierで重ね、別owner/inner→outer解放順と各一回を確認。
- 005: Systemctl全getter×null/throw、null時三getter取得と他stream解放、throw時既取得のみ解放、wait未呼出/owned destroy一回。
- 006: Inspector通常/streaming全getter×null/throw、当getter即時拒否/後続未呼出、既取得のみ解放、null process返却拒否。

fixtureは独立fakeProcess/Closeable/call列/atomic count/固定Throwable、実業務操作なし。既Systemctl八method・Inspector十一methodを同source選択へ追加し、元の期待値は維持する。予定1163 invocation /137suite /1154論理method（反復一method十回）、独立104=既98+新6、関連1059。新whole予定3895PT/562suite/1664Mainは未実行。

command `python3 -B tools/quality/pg5404_process_query_selected.py green --group factory`。source固定commit後に一回起動、原session/exit/XMLを回収、六format先行/NullAway/ErrorProne/三static/全storage四100を確認。selected physical767（前765＋OwnedQuery/StdIo各一、前群追加二/削除一もregistry保全）を全照合。target全四counterはmissも公開し、未実行や別source/nativeを加算しない。独立bytecodeでfactory/port型/ラッパーpreallocation/旧use不変を確認してから原十二の限定分類を更新する。実日時/OS/JDK/tool/command/source/隔離fixtureDB/owner/exit/coverage/hashはprivate実行manifestと公開allowlistへ。credential/rawXML property/原本DB/Backup/鍵の公開0、正式1964/53・QA051final保留は維持する。
