# NK-WEB-001 Page表示モデル単体テスト仕様書

PG192、FUN003/008/009・QST005/NTF、UI222/234§2/235/236、SS313§6.1/323。PageViewModel.fromとprivate constructor、全getter/isEmpty/isPaginated/previous/next/toStringを対象にする。元PAGED48は検証済電文から来る前提でも、型constructorだけでは相互整合を保証しないため表示境界で再検証する。

| Test ID | method | 入力・操作 | 独立期待 |
|---|---|---|---|
| PT-WEB-174 | web174EmptyAndSinglePage | 50/100、0/1/満杯1page | 0件はpage/pages1・first/last0、prev/nextなし、empty true。他は指定literalの件数範囲 |
| PT-WEB-175 | web175FirstMiddleAndLastPages | 50×3page/101件、100×3page/201件 | first/middle/lastの独立first/lastと前後page、端で存在しないlinkを生成しない |
| PT-WEB-176 | web176MaximumWireBounds | 999999page、count49999950/99999900、端first/last | overflow/切捨てなし、末尾nextなし、previous999998 |
| PT-WEB-177 | web177InvalidProjectionCombinations | page0/pages0/超過page・誤count/pages/first/last・固定size不一致 | 固定IllegalArgumentException、値/cause/suppressed非保持。typed DTO構築で拒否する値とfactory拒否を区別 |
| PT-WEB-178 | web178NullConfigurationAndRedaction | null data、size0/1/51/999、toString | null/config拒否、正常表示値はgetterだけ、診断固定 |
| PT-WEB-179 | web179IndependentParallelProjection | 4組literal×25並行 | 全100組の値とprev/next一致、共有可変状態/認証dataなし |
| PT-WEB-180 | web180JavaBeanDisplayContract | JavaBean introspection | 独立定義の6数値・previous/next・empty/paginatedプロパティ、protocol/sessionをgetterへ露出しない |
| PT-WEB-181 | web181ThymeleafSyntheticDom | test専用inline templateへ0/単/複数page | 明示DOMのcount/page/first/last/前後数字、0件では前後要素なし。これはProduction画面/URLの試験ではない |

期待値はUIの上限と手計算のliteral tableを使い、Production methodで作らない。成功4coverage100%/NullAway/static/negative、failed/flaky/skipped/not-runを合格へ算入しない。入力は公開数値のみ。command/環境/branch/commit/coverage/BUG・SSC/結果/evidence/hashは005とmanifestへ正式成功後記録する。現在未実装・未実行。
