# 純粋表示28methodの境界・null・所有・並行PT仕様

群2402/着手前1-3-7pp/cap10、source65bcd70a1dec722bd70be03468d9343142a7e789。PG10434六module正常compile、10436全14同値定数/全元token、10432 raw六/CS0/処理0を再実行せず参照する。今回Main/Testソース変更なし。旧四methodの確認再演が目的ではなく、同sourceで未実行の残24methodを含む一つの28method runとして、三Testの境界/null/所有/並行/DOMを閉じ、完全15Main class countersを得る。旧四execとの合成・件数加算0。

ProgramはNK-WEB-001表示部品、関連WBS-P016-04/08/11及びRoute/File/AnimationList共通参照。主責は元Test sourceのP01604/08/11を保持し、予算はG03.01へ一回だけ・関連部品費を再加算しない。

## 既存独立仕様との一意対応

仕様正本は同Programの006_Scenario階層表示/016_Animation一覧表示/020_Music階層表示単体テスト仕様書。各表の全Test ID・method・fixture・入力/操作・期待値/正常/境界/異常/null/例外/並行・非該当再送をそのまま適用し、勝手に変更しない。Test IDは**PT-WEB-182～193、PT-WEB-230～237、PT-WEB-246～253**の28。前群032等のhyphen無し略記ではなく各原仕様の表記を保持する。ソースから勝手にTest IDを推測せず、仕様表とclass#methodを全件joinしてmanifest/cases.jsonに固定する。

Scenarioは固定二game/三route/二file、個数0/10/11・0/50/51・0/500/501、prefix -1/0/99/100/整数端、入力/結果list所有・逆順と未知表示名、固定redactを確認する。Animationは固定main/sub相互関係・0/50/51/件数不一致/孤児/重複/zero size、Musicはcategory0/1/20/21・section0/1/100/101・最大合計19999980/99999900・重複/危険segment/独立percent literalを確認。全期待はTest固定値/表・独立JDK整数/文字列表現で、Production projection/encoderで生成しない。

## 独立性・実行の事前条件

三Testの全method/helper/field/lifecycleと、追加Main AnimationListViewModel/Video/Row、RouteListViewModel/Card、ScenarioFileListViewModel/Card、既八Main・Protocol record constructor/DisplayPath/PathSyntax/requireUnsignedRangeを読取確認。純粋値投影/collection/URI文字列のみで、display pathはファイル解決しない。全三classはcompile-time固定fieldのみ、lifecycle/static block・DB/HTTP/startup fixtureなし。合成SessionPrincipalは表示入力でありLogin/認証/権限変更・鍵操作をしない。

既concurrent methodのexecutorはtry-resource所有、8thread/64又は100task、Future10秒有限待ち。三合成HTML methodはStringTemplateResolver/inline template/合成DOMであり実Browser/HTTP/JavaScript実行ではない。既literalのHTML文字列はescape検査入力で、注入操作を外部へ行わない。closed helperのreflectionは表示classのgetter/propertyだけ、既Setで閉じる。これらは元八DB依存enum群や不明拒否操作の代替経路でなく、個別依存を確認した独立した通常PTである。

PG10450 preflightで28methodの完全catalog/三suite/source/SHA/依存・Main15を固定。新launcherはその28組以外を拒否し、package/class discoveryなし。PG10452を一回起動し、失敗/skipped/aborted/container失敗0以外は成功にしない。失敗時は修正前BUG/YKTへ登録する。PG10454 independent postで元XML/summary/真正終了・当source/session/CRC/15完全Main/全Main1843・非対象Test byte・禁止probe/classload0を照合する。source/依存・normal不一致なら実行せずHOLD。

当sourceの15完全Main classを全counter測定、0/0の非適用と100%を区別し、旧exec合成0/未達は未達のまま保存。新Test ID0、正式1964/53・個別17/190・工数null・QA051 final・全安全HOLDを維持。実template/HTTP/MQ/CHR/native/IT/ST/全451の代用としない。実行command・OS/JDK/tool/時刻/exit/input/expect/actual/coverage/hash・sourceは各manifest/後続2070へ。
