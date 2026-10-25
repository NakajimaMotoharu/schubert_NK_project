# NK-PRO-002 ページ算術・直接component境界単体テスト仕様

2026-10-25、Program NK-PRO-002、対象PayloadSemanticValidator.validate/validatePaged、Test class PayloadPaginationBoundaryTest。関連RD MSG001～011/MQ014～045/MSG-F01～F09は本Program原001の対応を保持、UI234 §7・UI233 SRCRSP01、SS322 §9、既PT-PRO-002-P06、1967/1968/PG-D668。上位設計/製品code/既期待値変更なし。

## 新規scopeと安全判定

G13選定を受ける新規通常PT群PROTOCOL_PAGINATION_BOUNDARY3_V1、主WBS-P002-02（generic payload/semanticの原Main担当）。開始見積り.5/2/5pp/cap10、値は開始eventへ固定する。既成功確認の再演ではなく、専用のpage2/最大page/一条件ずれvector追加。旧Root11/実VM/native/DB/鍵/配備/拒否操作から独立するmemory値・immutable functional fixtureのみのPT_DEFAULT。file/network/thread/RuntimeHook/権限変更/外部process/業務操作をTestから呼ばない。

Testは直接validatorのtyped interface portへ必要なpage/data/record値を渡す。Named mapperのscalar constructorが先に拒否することを避け、当componentの条件を単独で確認するfixtureであり、全named type/業務pipelineを通ったと主張しない。Expectedをproduction計算methodから作らず、以下のUI固定値/算術をliteralとして与える。recordはLine番号1/Audio有無falseで当validatorが参照する非page条件だけを満たす。不変copyとnull契約は既Program試験へ参照、新testで再演しない。

| Test ID | method | 入力・操作 | 独立期待値/算出根拠 |
|---|---|---|---|
| PT-PRO-002-PAGE001 | page001SecondPageHasIndependentExpectedBounds | SRCRSP01、size100/Effective2/Total101/Total pages2/First101/Last101/record1を直接validate | 受理。ceil(101/100)=2、(2-1)×100+1=101、min(200,101)=101、件数1 |
| PT-PRO-002-PAGE002 | page002MaximumEffectivePageKeepsExactNineDigitArithmetic | size100/Effective999999/Total99999900/Total pages999999/First99999801/Last99999900/record100 | 受理。上限page999999、999999×100=99999900、firstはlast-99。totalはN9内、long overflowなし |
| PT-PRO-002-PAGE003 | page003RejectsIndependentRangeAndOneFieldArithmeticChanges | 正常page2からEffective0、First100、Last102、record0、Total pages3へ一つずつ変更。最大pageからEffective1000000へ一つだけ変更 | 各LayoutValidationException。Page範囲1～999999、固定first/last/count/pagesに一つだけ違反。fixture constructor自体にこれらのsemantic検査は置かず実validatorへ到達させる |

事前条件：fresh利用枠>10、new-only作業/出力namespace、source commit固定/dirty重複なし、元job生存/所有を混同しない。新Test追加後の同source六module compile/package/null/static（PT実行0）と、当新class三methodだけの有限JUnitを別記録にする。旧全4222/現成功原runを確認目的で再実行しない。source/command/toolchain/実exit/XML/hash/coverage/静的解析/時刻は結果007と公開manifestへ記載する。

coverageはJaCoCoの当run/当Main全class-method-line-branch countersを未網羅も含めて記録。三新caseの成功をP06全体/Program全体/四100/全451へ読み替えない。Failed/aborted/skipped/not-runは成功へ含めない。全scope/source/runの正式閉鎖/CHR/native/QA051final/HOLDは継続未完了。新sourceへ旧PT成功を転用せず、同byte証拠は比較根拠としてのみ保存する。

障害は実装済仕様違反を確認したら修正前915、共通影響は916へ起票する。fixture構築の初回未完成/compile失敗も実結果として保存し、未実行を合格にしない。証跡は本Programの新専用provisional下に必要なsafe XML/JSON/coverageのみ、raw token/session/credential/DB実体なし。
