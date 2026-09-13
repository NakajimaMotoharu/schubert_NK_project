# NK-OPS-001 共通resource scope 単体テスト仕様書

PG170/SSC063、修正前6e59c153、BUG195/YKT154。OPS009/FIL001～009/UI237・251/SS311・333冒頭・341§6.5/6.7/7.4。対象Storage.ResourceScope.use（IO正規化を含む）・Action全責務。scopeは資源を受領後1回だけclose、正常値はclose成功後だけ返す。所有前null拒否とcallback nullable透過を区別し、NPE正常化なし。

| Test ID | method | 独立期待・操作 |
|---|---|---|
| PT-OPS-RSCOPE-001 | successfulOwnership | fixed42をbody→closeのliteral順で返し、指定releaseのclose1回。別の借用資源は各実callerの保持inode/lock PTで確認 |
| PT-OPS-RSCOPE-002 | knownIoFailures | plain IO/Storage全reasonとbody/close/両方、cause/suppressedを固定化、両失敗はUNAVAILABLE、close1回 |
| PT-OPS-RSCOPE-003 | unknownBodyFailures | Runtime/NPE/Error body単独は同一例外、close正常完了・返却なし |
| PT-OPS-RSCOPE-004 | knownBodyUnknownCleanup | 既知IO body＋Runtime/NPE/Error cleanupはcleanup同一・非成功、成功body unknown closeも同一 |
| PT-OPS-RSCOPE-005 | unknownCompoundFailures | unknown body3×IO/Runtime/NPE/Error cleanup、同一throwable再送、primary同一・固定secondary1・close1回 |
| PT-OPS-RSCOPE-006 | nullAndNullableContracts | close/action nullは所有受領前拒否、caller保持資源のcloseなし、callbackの明示null値はclose後に透過。NPE bodyは非正常 |
| PT-OPS-RSCOPE-007 | nestedScopes | literalopen/body/innerclose/outerclose、各close1回、複合時も外側資源解放・unknown同一/secondary件数、known理由維持 |
| PT-OPS-RSCOPE-008 | concurrentScopes | 独立64scope、共有可変error/状態なし、literal各index+42結果・全close64、例外scopeが他scopeを妨げない |

fixtureは公開合成Throwable/AtomicInteger/明示listのみ。Productionをexpectedへ呼ばずliteral値・例外same identity・close回数・固定reasonで判定する。全branch/line/method/class100%、NullAway/SpotBugs/Spotless・静的generic null契約を検証。環境は421。選択Storage PT＋呼出Batch/全reactor、018全scope/022 mapping・019負canaryで証跡hash/command/時刻/source/exit/4coverageを028/evidence/manifest.jsonへ記録する。失敗/未実行/skip/flakyを算入しない。

既存呼出者のBAT204/235、UNIT015、保持inode/lock PTは共通8件と別に再試験する。BUG195/YKT154の全検索対象・非該当根拠/反例/再試験は017048へ記録。実root/実子終端・IT/ST/全PGPT完了とはしない。
