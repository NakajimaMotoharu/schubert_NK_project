# F03 六module静的品質引渡し

W66-HANDOFF-F03-20261117-01 / owner WBS-F03 / 2026-11-17T01:00:02.742316+09:00 / Core e4794ddf45487268883334d0f8773d89bd47dcba。

|module|Main source|旧architecture比変更|旧style比変更|当候補static|
|---|---:|---:|---:|---|
|src/schubert-nk-protocol|165|10|10|PROTOCOL_STATIC_0_WITH_46_EXACT_DISPOSITIONS|
|src/schubert-nk-storage|25|4|4|CURRENT_SOURCE_APPLICABILITY_PENDING|
|src/schubert-nk-bootstrap|87|64|64|CURRENT_SOURCE_APPLICABILITY_PENDING|
|src/schubert-nk-api|283|36|36|CURRENT_SOURCE_APPLICABILITY_PENDING|
|src/schubert-nk-web|262|34|34|CURRENT_SOURCE_APPLICABILITY_PENDING|
|src/schubert-nk-batch|200|48|48|CURRENT_SOURCE_APPLICABILITY_PENDING|

SSC447 Protocolは全152PT成功/FESnotrun0、Root/PMD-CS-SB適用未分類0・175ClassStats/物理集合一致・同162CRC-initXML。親二raw100だが全Protocol4method/58branch/4line/85instruction不足でModule全品質未受入。他五moduleを当runで解析/試験済みとはしない。

現行WBS-F03/2-1..3の原HOLD「六module静的ゲート・Root11対象の許可」は操作ごとに維持し、Actual4 classfile/Root2試験の禁止範囲を触らない。次は各moduleの現在source/tool/profile/証拠scopeを結び、既承認の必要な差分検査だけを取得する。正式1964試験を含む別source成功を当候補合格へ転用0。F03の四判定は未受入。
