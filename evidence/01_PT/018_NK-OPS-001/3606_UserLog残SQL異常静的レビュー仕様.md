# User/Log残SQL異常・静的レビュー仕様

主担当WBS-P010-01、関連WBS-P010-04追加費0。開始見積り.5/1.5/4pp、cap6。対象はUserQueryRepository search/detail、LogQueryRepository searchの未実行SQL/row不整合/close異常。元2759/2760と2036の動的HOLDを維持し、新fixture/ハーネス/故障注入・製品呼出しを行わない。拒否操作の特定や再試行、PT免除認定は含まない。

RD FUN008/009・AUT002/003・DAT003・MON、UI225/235/236/241、origin/main SS312のSSC329（borrowed repository/TWR/fatal分類）、SS332の検索page/SQL/UTC/必須列契約を正とする。JavaのTWR規則からRS→PSの逆順closeと例外suppressionを独立期待とし、製品methodでexpectedを作らない。原34PT/SQL文字列・tuple/2088byte goldenと未達counterは保持する。

|Review ID|独立期待|コードで確認する点|動的に残る確認|
|---|---|---|---|
|RV-ADM-SQLERR001|borrowed Connectionを所有せず、autoCommit=false/readOnly=trueを要求|commit/rollback/Connection.closeの発行なし。RS/PSだけTWR所有|実driverの状態/DB後条件|
|RV-ADM-SQLERR002|必須SQL NULLを0/空へ変換しない|数値getLong直後wasNull、必須文字/UTC値を明示検査。RequiredColumnはSQLSTATE22004|driver NULL/変換失敗経路|
|RV-ADM-SQLERR003|UI234§2/SS323§6の最大page999999とSS332のUser50件/Log100件から、上限は独立計算で49,999,950件/99,999,900件。超過は9001。close異常併発は通常上限応答へ戻さない|上限分岐、TWR完了後のcatch、suppressed有無でcapacityを選択|上限/RS-PS closeの各組合せ|
|RV-ADM-SQLERR004|page/total/effective/行数不整合を応答にしない|不変条件違反をSQLException、TWR外catchで一時障害へ変換|破損tuple/重複行/欠落行|
|RV-ADM-SQLERR005|RSをPSより先にcloseし、close失敗後に結果を返さない|戻り値のreturnをTWRの外に置き、内側RS/外側PSを閉じる|RS/PS単独・複合close失敗|
|RV-ADM-SQLERR006|cause/suppressed/SQL-nextにfatalがあれば元Errorを先に伝播し、非fatalならprovider graphを新catalogへ渡さない|全catchでpreserveFatalを固定例外生成前に呼ぶ。新例外は固定message/booleanだけ|fatal分類/同一object/cycle/close secondaryの実行|

001～006は静的文書レビューIDであり実行PT IDではない。current Main4217/normal20990の対象source byte、21706の全Main個別静的判断・20992六module SpotBugs0を結合し、再engine実行なし。静的判断の結合は元graphの動作、DB後条件、全分岐coverageの証明にならない。具体的な拒否対象は未特定のためPT_EXECUTION_EXEMPT/ACCEPTED_WITH_ALTERNATIVEへ昇格しない。未測定・未実行は未実施のまま。
