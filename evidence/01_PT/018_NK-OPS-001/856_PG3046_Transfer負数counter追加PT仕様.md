# 856 TransferCleanup signed counter独立境界

PT-OPS-TRANSFER3046-001、NK-OPS-001/WBS-P017-07、OPS009/UI251/SS341/343/SSC118/451。主担当は855と同じP017-07で重複leaf受入を行わない。同群0792の境界matrixへ同一counter契約の小差分を追加し予算0.3/1/3pp内、実費配賦null、追加token予算なし。

対象TransferCleanup.Outcome constructor: target/success/failure/retained/bytesの非負条件およびsuccess<=target、failure=target-success。既matrixはsuccess<0/failure<0の二独立条件を未試験。literal tuples `{1,-1,2,0,0}` と `{1,1,-1,0,0}` を追加し、両方IllegalArgumentExceptionを期待する。外部結果から期待値を作らず数学的不変条件から算出。既存四JUnit method全件を実行し、Linux retained FD/元root不変/正常削除/境界保持/IO拒否/元byte不変をまとめて再確認する。fixture以外の削除/VM/原Backupへの操作は0。

実行工具pg3046_transfer_counter_selected.py、exact3026 Main jar六つと既fixture/依存hash固定、Test-only compile -Xlint:all -Werror/独立class launcher/JaCoCo。対象Outcomeのline/method/class/branchを測定し未達なら未達のまま記録する。新全体統合は後続groupとまとめ、旧3685や限定試験を新whole合格へ足さない。null/未知/並行・再送は既同suite/TransferCleanupFailureTest参照、本追加は二signed境界だけ。

実日時/source/実四testcase/終了code/XML/exec/counter/証跡hashは実行後追記。秘密/原本DB/鍵/sessionは非格納。
