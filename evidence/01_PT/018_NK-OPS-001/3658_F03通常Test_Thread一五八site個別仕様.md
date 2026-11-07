# F03通常Test Thread一五八siteの適用scopeと所有未証明の分離

WBS-F03、411§9/10/451/SS351352。原1/3/7pp cap9。元347のうちloader93は3656/3657で限定分類済み、残254からDoNotUseThreads158を選ぶ。規則のJ2EE application thread禁止と、JUnitで競合/停止/割込を検証するthread使用を分ける。ruleだけでscope免除せず、全siteの原属性/source/hash/line、JUnit import・class/package・enclosing method、同正常Main Jarに当Test classが入らないことを個別確認する。

対象53明示Test内158siteだけ。前提未証明は未分類のまま。独立Java AST parse-onlyで実method/line範囲を検査する。定義/利用を一律成功へせず、bounded join/cancel/close/latch等の寿命・決定的scheduleやassertionの正しさは別のPT責務であり、本規則分類の成果へ混ぜない。CloseResource/Map/volatile等の別規則と全Test/global F03は残す。Product/Unit/PMD/既成功試験再演0、source/規則/抑制変更0、held source/外部/VM/DB/Root/native操作0。

補足の追加発見：今回の3654/3656の「402」規約番号参照は411の誤記。修正前915/916に登録し、元spec/event/予算/hashを保持した追記訂正を行う。上位仕様・実装・oracle変更なし、追加文書是正費按分は不明null。原1/3/7cap9と区別する。

期待=原347と既93分類を不変保持、対象158のsource/AST/非Production witnessが一致したsiteだけsidecarへ個別NOT_APPLICABLE、残96は未分類のまま。synthetic metadata否定条件でMain path/誤package/class/method/範囲/混入Jar等を拒否。正式1964PT/53scope/unique430/whole94/新leaf0/工数null、451と全HOLD不変更。
