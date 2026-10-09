# Inspector実bodyのguard・private claim境界PT仕様

NK-DAT-001/NK-OPS-001、P004-04（guard/claim）とP018-03.02（UID同値）、DAT-009/OPS-009/FIL-006・UI212/241/251・SS3436.7/6.17/341/352。PG-D408409の分類5内部整理。開始前既leaf内subset low.2/base.6/high1.5/LOW、親/共通/global全回帰予算追加0、N/T/個別実消費は不明。

| Test ID | 入力/操作 | 独立期待値/後条件 |
|---|---|---|
| PT-APP-925001 | Operation-owned実bodyへguardがIOException（private diagnostics入り）を返す。独立temp credential fixture、既real JDBC fixture | InspectorCredentialException/no cause/suppression0、credential file read0/DB progress0・全保持dir閉鎖。failstopを成功/INTERRUPTEDへ変えない |
| PT-APP-925002 | private owner readerからSS343 literal NKMAINTOWNER1正常claim又はmalformed原文を一件取得 | 正常は明示boot/run/deadline/Parent値・cleanup absentのdataだけでUnit/Rootadmissionを意味しない。malformedはIOException固定maintenance owner unavailable/no cause/suppression0・owned readbuffer消去/dir閉鎖 |
| PT-APP-925003 | private owner file欠落/reader I/O拒否 | 元InspectorCredentialException分類保持（generic parser IOExceptionへ誤変換しない）、秘密/raw例外原文の公開0・全資源解放 |
| PT-COMMON-925004 | 第1capture UIDは固定200、第2captureだけ全4UID202へ変化 | 外側冗長UID比較を削除しても内側UID検査でIOException・buffer消去/manager前後比較の弱体化0。既一回目UID不一致・Root caller非0も既suiteで回帰 |

正常/欠落/null/境界/unknown/競合/再送は既Application/entry/guard/credentials/ChildBroker/Caddy suitesを同群で回帰。期待値は手書きcanonical metadata・SS所定拒否・SQL後条件、Productionでexpected生成0。providerは観測/所有portに限定し実startupを合格化しない。新main変更群は独立selected後、必要fresh同source全六を実行する。実source/command/tool/exit/counter/hashは未実行として後記、失敗/flaky/skipped/not-run加点0。
