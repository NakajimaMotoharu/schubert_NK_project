# MediaRange配信port単体仕様

Program NK-MED-001 / MediaRangeService constructor/deliver/respond、FUN005～007/PER004～006、UI223/235/237、SS311/333§10/11、411/451、746。既存6native試験を置換・再実行せず、当sourceの新しい最大数constructorと配信portをmemory-onlyで検証する。旧全体1964/53と当source資格を混ぜない。

|Test ID|目的・固定入力・独立期待値|
|---|---|
|PT-MED-PORT001|通常200/2..4の206/suffix3/1MiB上限/先頭Rangeだけ/末尾超過416、全headerとbyte区間、64KiB以下read、source一回close|
|PT-MED-PORT002|HEADはbody呼出0、downloadは不正Rangeでも200全長・attachment/octet-stream|
|PT-MED-PORT003|descriptorのtype/id/disposition各不一致はsource0回、INVALID_DESCRIPTOR|
|PT-MED-PORT004|設定0/21/MIN/MAX拒否・1/20受理、default20の21回目BUSY/RetryAfter1、再入で全枠解放とbinding優先|
|PT-MED-PORT005|source/header/body/write/readのIOExceptionはUNAVAILABLE・原因/パス露出0、同instance cap1の次配送成功|
|PT-MED-PORT006|RTEは同じ例外identityで伝播、finally後の次配送成功|
|PT-MED-PORT007|411のnon-null requireNonNull契約を全引数で違反時拒否、side effect0、枠不消費。予期したguard NPEのnegativeでありproductionのNPEcatch/正常化ではない。Main NullAway資格は別で記録|
|PT-MED-PORT008|own2thread/latchでcap1の二回目BUSY、先行解放後の次配送と別response/byte一致、有限join/close|

MemoryChannelは物理path/FD/native/DB/HTTPを持たない。bytesは(i*19+7)の独立固定fixture、期待区間はSSのliteral値で選びproduction parser/factoryをexpectedに使わない。Response全headerはliteral、immutableとoutput非closeも検査。旧native fixtureの認証/ファイル所有は未証明のまま、P00904全体を受入しない。

PG18642正常Main jarをsource/hash/全Main入力/CRCで照合して再利用し、新TestのみJDK25 javacでcompileする。8method全class単位で一回実行し元XML/OS終端/単exec/sessionを独立postする。全対象physical型・適用line/method/class/branchを報告、interfaceの実装を偽ってcoverageへ加算しない。静的・環境・command・日時・commit・入力・結果・関連BUG/hashは009結果/manifestへ保存。新不具合は修正前に915/916へ起票し、old成功を新sourceへ合算しない。
