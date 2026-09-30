# 286 Transfer実清掃：限定結果

Source `9ac9455eee98327dc98e8047c6958b118845689b`、dev-foundation。2026-09-30 16:00:14 JST、host Linux/Java25.0.4/Maven3.9.12/JaCoCo0.8.15。仕様285/TRANSFER001..003のTransferCleanupTest4件、StorageのLinuxDirectoryCallsTest5件を含む全6 clean2,560PT/375suite F/E/S0/static6module0・exit0。

独立fixtureの実Linux held FDで旧file2件/5byte削除、空の日付dir rmdir、境界/未来/未知/不正mode/symlink/hardlink/階層/日付の11保持、外側file不変、交換後旧FDだけに作用、guard失敗時mutation0を確認。再帰削除0・host観測能力のmutation拒否を確認した。root/UID/GID/null不正は拒否する。

Storage全4指標missed0。TransferCleanup未網羅B/L/M/C=16/8/0/0、残IOException/交換/条件分岐の追補と真正Cleanup callerは未実行。helperの実FD成功をS2 native/正式100%へ算入しない。

エビデンス：`evidence/provisional/PG388-cleanup-dependencies/manifest.json` SHA-256 `757a2f32494a28f02e086c14a76803a971278092051c0c28fc2185b4d62139ed`。sanitized JUnitのTransferCleanupTest/LinuxDirectoryCallsTestとSSC118/333§12のfixture根拠を対応付ける。所定toolchain/Maven全6 cleanコマンドは同manifest/456 trigger、実行logはwork/pgpt-runs/PG379/pg388-six.log。dump/credential/tokenはGit格納0。
