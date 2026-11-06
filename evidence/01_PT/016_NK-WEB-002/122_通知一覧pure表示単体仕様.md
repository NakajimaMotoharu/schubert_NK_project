# SCR020 通知一覧pure表示 単体仕様

NK-WEB-002/WBS-P016-20、FUN-108/NTF-001/002/003/008/QST-010（表示層の部分）、UI224/236、SS313/332/PG-D347。NotificationListViewModel公開success/invalid/getters/toStringを経由しprivate row/link/encodeへ到達。旧NotificationController carrierは保持し再演/合算せず、元未登録282を未試験と断定しない。

新Test NotificationListProjectionPortTestの全14 @TestをPT-WEB-NLIST001..014としてmethod順に一意対応し、結果123で確定する。独立固定行・UTC/JST・50件pageのfirst/middle/last/clamp・状態/type/Unicode100/削除済summary・重複/件数/並び順/invalidform/nullを検証する。期待リンクはUI236の固定文字列で、Production UriUtilsからexpectedを生成しない。immutable map/list・入力copy・自己所有2worker/8taskのactor分離も確認する。

Fixture: synthetic displayPrincipal、immutable NotificationRecord/PagedResponseData、実NotificationSearchForm.bind（backend無し）。Spring7.0.9 UriUtils.encodeは固定current aux JARのjavap metadataでactive methodが文字処理のみと確認、HTTP/URL解決/Context/DB/JMS/Root/VM/実session/key/held4は呼ばない。classinit範囲をpostで点検し、未知のbackend依存が見つかれば未受入として保持する。合成context値はTest内で生成しlog/manifestに保存しない。

shared012/frozen059でprepare/static→Git固定→選択全14→単一JaCoCo/normalCRC・全physical/four100/strictpost。同D8正常PG20112/SB20114は再演せず参照。compiler $1 switchmapはreportへ保持してjavap属性と空codeを独立分類、手動除外0。開始はfresh API120秒receiptをstart_fieldsで結合済み。終端は新APIをend_fields(before=開始receipt.observation)へ結合しcached群前値を末尾へ流用しない。F/E/S/flaky/not-runをPASSへ含めず、実行環境/command/source/exit/hash/障害は結果123/manifestへ保存する。正式1964/53・新leaf0・工数nullと実画面/全PGPTの未受入は維持。

## 固定Test ID・method対応

|Test ID|method|独立期待値/入力操作の目的|
|---|---|---|
|PT-WEB-NLIST001|emptyReturnsPlainView|空一覧/頁なしlink/TopBar固定文字列|
|PT-WEB-NLIST002|allStatesProduceApprovedLabels|全5状態と3区分の独立label/JST/9field|
|PT-WEB-NLIST003|pagingLinksKeepFiltersAndClamp|50件pageの先頭/中間/末尾/clampと固定URI|
|PT-WEB-NLIST004|invalidFormsStayUnpaginated|invalidform表示・validform誤使用拒否|
|PT-WEB-NLIST005|wrongEffectivePageRejects|requestに合わないeffectivePage拒否|
|PT-WEB-NLIST006|rowCountMismatchRejects|総数と行数不整合/空頁への余分行拒否|
|PT-WEB-NLIST007|duplicateIdsReject|通知ID重複拒否|
|PT-WEB-NLIST008|inconsistentStateAndDeletedSummaryReject|type/state・Unicode101・削除済概要不整合拒否|
|PT-WEB-NLIST009|orderRulesAreIndependent|時刻降順と同時刻ID降順を別vectorで照合|
|PT-WEB-NLIST010|nullBoundariesReject|actor/form/pageData/collection/要素null拒否|
|PT-WEB-NLIST011|outputCollectionsAreImmutable|外側List/内側Map変更拒否|
|PT-WEB-NLIST012|copiedInputDoesNotChangeRows|callerのmutable input変更後もsnapshot維持|
|PT-WEB-NLIST013|unicodeSummaryBoundaryAndDeletedLiteral|Unicode99/100と削除済literalの正常境界|
|PT-WEB-NLIST014|parallelViewsKeepActorsSeparate|自己所有2worker8taskのactor分離/10秒join|
