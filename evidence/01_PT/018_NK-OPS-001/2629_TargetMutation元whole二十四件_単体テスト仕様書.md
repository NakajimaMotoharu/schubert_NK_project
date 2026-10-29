# 2629 TargetOperation・UserMutation 元whole二十四件 単体テスト仕様書

2026-10-30 JST、dev-foundation、開発source6b53、群3015開始0.5/3/5pp cap10、PG-D879。Target元全203行/Mutation元全548行・全helper/initializer/callback、Main九Source計579行と新DTO六件・IdValue/UserId/NotificationId/QuestionId/TypedFieldValues必要経路を読了。先行1920/2058は旧レビュー参照、現合格へ転用しない。Target8＋Mutation16を元whole2suiteとしてPT_DEFAULT、一実JVM/execで実行。Main/Test/fixture新規改変0。

## program・追跡・適用性
TargetOperationInput=既canonicalP015-07、CancelForm=P016-21、QuestionDeleteForm=P016-23、UserMutationInput/UserStatusForm/UserRoleForm/PasswordResetForm/UserUnlockForm/UserChangeForm=P016-17。Test二pathはUNKNOWN/null。関連SCR017/021/022/023・FUN009/010/013・AUT002003・UI224225236・SS313314323、SSC177。Main九完全Sourceの内UserChangeFormはabstract sealed interface/noCodeの自然metadata、他八全closureは各一physical。branchのないwrapper六Sourceは自然0/N/Aとして記録し、四counter100に補完しない。

## 独立oracleと全Test ID
PT-TARGET001..008（target001..008）:
001=CANCEL/DELETE requestのN12+UUID36をliteral48byte（ASCII000000000042＋合成UUID）とactualcodec比較、operation/confirm/display値とredacted文字列。
002=ID1/12桁最大/zero/過大/符号/空/全角/不一致/leadingzero、無効toRequest拒否。
003=四requiredfieldのmissing/null/empty/duplicate/null-element。
004=operation/confirm/UUID閉集合・大文字/space拒否。
005=未知fieldとnull-key拒否、CSRFのみtransport許容（権限発行なし）。
006=top-level null/未対応selector例外。
007=入力map消去後snapshot/immutable。
008=自己所有8thread/100有限task・各get5秒、JDKmap/値だけ。

PT-USER-CHANGE001..016（change001..016）:
001..004=STATUS/ROLE/UNLOCK/PASSWORDの独立literalgolden、ID1..999999999999/version0..999999999、size60/68/60/324・version位置13/17/12/268、tokenは+9、value位置12を手書配列（zero/spacepadding）。expectedにproductionlayout/encoder呼出なし。
005=operation/unknownfield、006=path/hidden ID、007=N9version、008=confirm/UUID、009=role/boolean閉集合。
010..011=NFC/password12..128codepoint/256byte・emoji/controls/surrogate/username一致・trusted target不足、scalar/書式だけでaccount変更しない。
012=null/map/key/list/element/欠落/複数値、013=immutable/redaction、
014=close二回/closed後例外/別DTO値寿命、015=8thread/100task・invokeAll後get30秒、016=wire field names/displayだけ・入力からauthorityを付与しない（実API self/last-admin認証は非対象）。

## 実行・環境・残件
予定 `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14296_web_target_mutation_whole_twenty_four_pt.py`。固定14216六Jar/Mainと元二Test・固定Reporter・新-only一session、実F/E/S/timeout/exit/unique XMLを照合し14298独立postで完全九Source/noCode metadata/自然branch0・CRC・必要counterを測る。BUG2098再発防止として既14282のtested headers parserを利用し、元JVM四prefixをraw stageへ構造化結合。入力の合成secret/UUIDは通常logへ出さず、報告counterのみ。

副作用は自己所有純値/有限thread・new-only host試験出力のみ。取消/削除/role/password等の名称はDTO変換で、実DB/業務処理/権限変更/HTTP/token発行/VM/Root/鍵/permit/cohort/graph9操作なし。既拒否の代替fixtureではない。未網羅/natural0/noCodeを明記し100へ偽装せず、独立結果・hash/関連BUG・実環境は2630へ。新受入/正式/工数null/全HOLDは別保持。
