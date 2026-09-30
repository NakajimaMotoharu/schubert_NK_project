# 285 Transfer実清掃（実装前）

NK-OPS/NK-BAT、TransferCleanup / OwnedTransferDirectory.removeEmptyChild、RD FIL006/OPS009、UI237/251、SS333§12・341§7/8、SSC117/118。

PT-OPS-TRANSFER001：実Linux FD/一時synthetic rootの20260929にcanonical UUID.part(3byte)とready(2byte)を作りmtime<固定cutoff。期待値target2/success2/failure0/retained0/bytes5、date消去・root保持。期待値は手書きfixture length/Files.existsで独立算出する。

002：mtime=cutoff/未来、未知名、不正日付、非canonical UUID、symlink（外部target不変）、hardlink、subdir、owner/mode/ACL違反を保持してWARNING。深さ2以上へ入らずsize不正でもregular古fileの清掃には生成制約を流用しない。

003：保持rootのpath置換でも別rootを削除しない。empty dateだけ実rmdir、非empty/symlink/fileでrmdir失敗・元内容保持。read-only host adapter未対応能力はmutation0。guard失敗/root metadata異常/null・閉鎖能力/FS不明は非成功、削除0又は正確な既実処理を保持し隠さない。独立native＋注入失敗で全branch/例外を追加する。

PG/PT並行、最初の未実装失敗は障害に算入しない。実行環境/JDK25/対象commit/結果/coverage・sanitized manifestは後続286へ記録。現時点NOT-RUN、親Cleanup実接続・DBterminal/native外部経路は別未受入。
