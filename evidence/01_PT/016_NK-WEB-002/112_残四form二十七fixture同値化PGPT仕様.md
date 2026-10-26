# 残四form・二十七fixture同値化PG/PT仕様

NK-WEB-002/WBS-F03（関連P01507費0）/群WEB_REMAINING_FOUR_FORM_LITERAL_PGPT_V1、着手前3/6/10pp cap10、共有使用23/残77/reset1793599188。基点sourcee7c2e2c89、BUG1886/YKT1637/PG-D689。関連RD FUN009010013/QST001/AUT002003/UI224225236/SS313314323、元016055/065/069/083の独立期待を維持する。

対象はUserCreateFormTest八、UserMutationFormTest十六、TargetOperationFormTest八、QuestionSubmitFormTest八、計40method。MainはUserCreateForm/QuestionSubmitForm/TargetOperationInput/CancelForm/QuestionDeleteForm/UserMutationInput/UserStatusForm/UserRoleForm/PasswordResetForm/UserUnlockForm、全TestとMain全文のread済み。実認証/保持session/DB/HTTP/JMS/鍵/Root/VMなし。Protocol codec/固定layoutはactualにだけ使用し、expectedは旧Test独立offsetから構築したbyte配列のまま。

PT_DEFAULT：入力は既存の公開合成文字列/固定UUID、未知/欠落/空/多重/null/Unicode-NFC/byte・codepoint境界/enum/確認/immutable snapshot/close・redaction/8worker100task/Future5・10・30s/TWRを保持。UserMutation.invokeAllは有限100taskで各pure form/codecのみ、外側専用JVM240sを維持。秘密情報取得/ADMIN業務発行/authority付与・hash生成なし。Main→Protocol既normal jarとclosed40methodだけを選択、extension自動検出/parallel/package discovery無効、保留Testの抽出なし。

|Test ID|目的/fixture/操作|独立期待と後条件|
|---|---|---|
|PT-USER-CREATE001..008|合成username/password/role/flag/UUIDのform bind|固定372byte/offset0,64,320,325,326・redaction/char所有終端・旧assertion全維持|
|PT-USER-CHANGE001..016|STATUS/ROLE/PASSWORD/UNLOCKの型境界|固定60/68/324byte・ID12/version9/UUID36・scopeはformのみ/実authority更新0|
|PT-TARGET001..008|CANCEL/DELETE formの型境界|固定ID12+UUID36=48byte・owner/session/token発行なし|
|PT-QST-FORM001..008|質問本文1..4096byte/NFC/close/null/合成UUID|固定4144byte・body0/UUID4096・期待値はencoder呼出で作らない|
|PT-FORM-REST001|元27warningの同値private定数化|独立逆展開で全元token復元・誤値/欠落/annotation改変拒否、全Main/他input保持|
|PT-FORM-REST002|新固定source正常build/40PT/static/独立元結果|F/E/S/aborted0のみ成功、原43raw→duplicate27消滅・残resource8/thread8は未分類を保持、CS/processing0|
|PT-FORM-REST003|新一execと全Webartifact|完全358物理の全counterをmiss込み実測、対象Mainごとの四counter/未達を明示、旧exec合算0|

tool10974plan/10976inverse→source commit固定→10978六正常compile（PT0）→10982元40通常PT→10980当四static→10984独立XML/exec・全Main/他Test・全Webcounter→10986/88 trace。OS/JDK/version/branch/commit/実command・終了/入力/期待/実際/BUG/証跡hashを公開manifestへ保存し113結果から参照。元成功の確認再演・制限探索・保留二工具アクセス0。正式1964-53/17-190/工数null/QA051final/全451未完を維持、小群で止めず継続する。

## 実測後追加発見・BUG1887（原開始見積は変更しない）

source05eの原40method成功/10980 raw16/10984対象九Main四100は中間証跡として保持する。QuestionSubmitFormだけL2/M1未到達であり全対象100ではない。PG-D690により既PT-QST-FORM001で `UUID.fromString(TOKEN)` と `form.operationToken()` を比較し、007でclose後同accessorのIllegalStateExceptionを確認する。Production methodでexpectedを作らず、固定合成UUIDをJDKで解釈するだけ。既8method数/byte goldenは不変。

UserCreate create006/008とQuestion qstForm007のfirst/invalidの四fixtureにTWRを追加し、元の二回close・closed後DTO/表示検証も保持する。10994独立チェックでこの四TWRと二assertだけを逆構造展開して05eの全tokenへ復元、誤値/不足/対象外改変を拒否する。Main/他input保持。一つのform接続経路を受入まで進める同2499群内の追加是正で、原3/6/10 cap10は固定/追加費を重複計上しない。

新sourceを再固定し、11000六正常（PT0）→11002既40method必要PT→11004当四Test実static→11006元結果/単一exec/完全Web/対象十Main四counterを独立照合する。旧40成功/execを合算しない。resource移管四/thread八の残rawは別の具体文脈として未受入を維持し、件数を推測で0へ変換しない。10986/88 traceは中間source05eでは未実行、最後のsource資格後に実際の番号/manifestを113へ記録する。

BUG1888追加：11000はsource9eのTWR explicit close警告で実1/PT0、11002/04/06は未実行のまま維持。close正常性は六callをassertDoesNotThrowへ明示し、二回close/closed拒否/新accessor独立比較は維持。10996が六置換/二static importだけを逆展開して9e全tokenへ復元する。修正sourceを再固定して新番号11008正常→11010原40PT→11012当四static→11014独立counterへ。元buildの再実行や警告抑制はしない。開始3/6/10/cap10不変、追加発見/手戻りを分ける。

11016/11018追加：最終raw12のsource/rule/非座標属性/messageと原10690 IDを結合し、四factoryからTest Form recordへの所有移管（closer=f::close、record.close→closer.run、利用側TWR/finally）と、四JUnit試験の8worker100task/TWR/Future5/10/30s/専用JVM240sを具体レビューする。元PMD gate1は保持、TestはJ2EE runtimeでなく普通JUnitである根拠を限定し、他ruleやMainへ一般化しない。原40PT/対象十Main四100はsource9cのまま参照、確認再演0。CloseResource四のowner transferが不明なら未分類保持、PT実行免除/全F03受入へ変換しない。
