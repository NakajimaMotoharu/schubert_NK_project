# NK-WEB-001 Scenario階層表示単体テスト仕様書

PG193/FUN004/SYS006/PER003/TST001～005、UI222/223§4/234§5・8・9、SS313§4・6/323。GameListViewModel/RouteListViewModel/ScenarioFileListViewModelと各nested Cardのfactory/constructor/getter/toStringを対象。検証済wire recordが入力というpreconditionを明示し、認証・MQ・URL routing・実画面の代用にしない。

実装前照合で初稿のRoute/File上限100/10000をUI234の50/500へ訂正。File factoryはprincipal/game/prefix/routeName/listを受け、routeName非nullと見出し`prefix: routeName`も確認する。source未実装なのでTDD草案訂正、BUG対象外。

| Test ID | method | 入力/操作 | 独立期待 |
|---|---|---|---|
| PT-WEB-182 | web182GameDisplay | USER/ADMIN、2game literal | code/title/href/topbarだけcopy、Current順とURL一致 |
| PT-WEB-183 | web183RouteDisplay | 両game、prefix00/01/99、route名/件数 | ASCII2桁・指定名維持・game/prefix URL、上位/scenarios |
| PT-WEB-184 | web184FileDisplay | prefix01/99、file ID1/999999999999 | title/display path/件数維持、数値IDの/scenarios URL、game上位link |
| PT-WEB-185 | web185NullBoundaries | 各factoryの全引数null/collection null要素、共通TopBar.from直接null | constructor/factory拒否、部分modelを返さない |
| PT-WEB-186 | web186PrefixBoundaries | -1/100/Integer端、0/99 | 範囲外固定例外、正常はASCII00/99 |
| PT-WEB-187 | web187SnapshotOwnership | mutable list変更・結果list変更 | 入力変更非波及、結果list不変、DTO参照を保持しない |
| PT-WEB-188 | web188ClosedBeanContract | getter introspection | topbar/primitive/String/closed Card listだけ、書込getterなし |
| PT-WEB-189 | web189SyntheticEscaping | title/name/display pathのHTML文字をinline test templateへ | text一致、script/img nodeなし、protocol/auth診断露出なし |
| PT-WEB-190 | web190ConcurrentProjection | 独立100組/8thread | 各literalの値・順・URL一致、共有状態なし |
| PT-WEB-191 | web191ListSizeBoundaries | 0/最大10・50・500/最大+1 | 空/最大を保持、超過固定例外。重複レコードはsemantic判定ではなく個数境界用fixture |
| PT-WEB-192 | web192PreserveSourceOrder | 逆順title/route/file、未知route名literal | 並び替え/固定map再推測/非空title選択をしない。入力の検証責務はclient/facade |
| PT-WEB-193 | web193RedactedDiagnostics | 階層6classと共通TopBarのtoString | 各固定redacted、TopBarViewModel[REDACTED]、値を含まない |

期待値はUI223・234とCurrent templateの独立literalで定義する。数値URLやtitleをProduction factoryからexpected生成しない。上限はUI234の10/50/500、routeは2桁、file IDは12桁を使用。全line/method/class/branch100%、null negative/static、失敗/skip/flakyは不合格。合成DOMは画面互換やHTTP成功の証跡に算入しない。

実行command/環境/日時/source commit/結果/coverage/関連BUG・SSC/evidence path/hashは007とmanifestへ保存する。選択12PTとstatic再試験は成功、BUG212/YKT168を起票・修正済だが正式回帰前であり部分成果数に加えない。
