# 857 Transfer root信用境界と暦境界

NK-OPS-001/WBS-P017-07.02、UI251/SS333§12・341・343/SSC118/451、PT-OPS-TRANSFER3048-001/002。855/856と同じ境界・原本保護群0792で0.3/1/3pp固定内、leaf費/全体費の重複加算なし。Main a9/PG2802不変更、native/VM操作0。

001: 所有UIDだけ不一致、GIDだけ不一致、ACL未取得null、非空ACL、read-only filesystemの五独立fixture。全てrootの最初の信用確認でIOExceptionを期待し、配下の既存三byte `{17,23,41}` とdate/rootを保持する。ACL最大44byteの境界もassert。effectiveUidを信用根拠へ代用すれば試験失敗する。期待値は固定byteとSS信用条件から独立算出、Production結果の再利用なし。全fixtureはJUnit専用一時directoryであり原Transfer/Backupへ接続しない。

002: date directory `00000101` は保持（year0非許可）、`00010101`/`99991231` は正規空directoryとして非再帰削除。固定期待target0/success0/failure0/retained1/bytes0、WARNING/PROTECTED_RECORDS、元root保持。表記が8桁でも業務日付範囲を自動承認しないことを独立確認する。

実行予定=既存四と新二の全六Test method、FES/aborted/notRun0、exact3026六jarとfixture/依存を固定。pg3048_transfer_security_selected.py、全完成payload/Javaformatの静的検査後だけnew-only実行。既acceptedScope/global四100/正式1964-53を変更せず、Test-only新whole3689への統合は未実行。開始時刻/終了code/XML/exec/全classcounterは実行後追記。
