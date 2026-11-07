# 未対応directory既定拒否四件・通常PT仕様

Program NK-SCN-001共有storage/WBS-P008-03（原開始4326のP00901はmedia metadata照会で誤帰属、実装前4327でP00803原子公開基盤へ追記訂正、元event/見積0.5/2/5pp cap7保持）。RD FIL001..009/UI241/SS333§7.3・§7.6・§12、SSC049/068/118。対象DirectoryCalls interfaceのcreatePrivateFile/createPrivateDirectory/removeEmptyDirectory三default Code全体。九abstract methodはCode無し、NoCodeを手動coverage除外にしない。StorageIoExceptionは既存pure IOException value依存だけで資格加算しない。current110/原UNBOUNDでtarget全Code proof未結合、UNKNOWNは未実装ではない。

新UnsupportedDirectoryDefaultsPortTestだけをcompile/実行、九abstract portは必ずAssertionErrorの独立実装、native adapter・元LinuxDirectoryCallsTest/helper・実FD/path/FS/I-Oを生成/compile/実行しない。入力整数はopaque値でOS FDではない。SS333§7.3/SSC049の未対応default無操作UNAVAILABLE、§7.6未対応private directory拒否、§12空directory能力未対応はunlink/再帰/closeで代替しないという独立oracle。defaultは常に固定例外で名前policyを承認しない。

|ID PT-SCN-DDEFAULT-|操作/fixture|独立期待|
|---|---|---|
|001|createPrivateFile、parent0/7/INT MIN/MAX、part名|全UNAVAILABLE固定StorageIoException/メッセージtransfer storage operation failed、cause/suppressed無し、abstract呼出0。0640 fallbackをしない|
|002|createPrivateDirectory、child/空/dot/dotdot/slash/NUL名|同じ無操作拒否、createDirectory/openRoot等0。名前の安全性を受理しない|
|003|removeEmptyDirectory、child/空/dot/dotdot/slash名|同じ無操作拒否、unlink/sync/close/root操作0、再帰代替無し|
|004|三operationの例外objectを順番に取得、先行だけsuppressed追加|例外全distinct、後続cause/suppressed0、先行だけ1を保持、abstract呼出0。null名のnegativeは最終source/manifestで明示|

Source allnormalphysical/interface全三Code・L/M/C100、branch0は自然N-A率null、code無し九abstractは無実行項目で成功PT数にしない。一session/exec/CRCとsource/Test/compile/static/command/hashを独立post確認、metadata否定と実PTを混在させない。JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15/PMD7.28-CS14.3、storage normal22084一jar+JSpecify+JUnitのみ、Main7aed unchanged/六静的22086再利用。runner442 prepare/static/run <source>、自己Test一fileproc:none/Xlint-Werror、Test static・全graph/command preflight→commit固定→初Unit120秒/Test10秒。期待値はProductionのreason getterをexpected生成へ使わずSS独立literal/enum契約をassert。失敗/abort/skip/not-runは合格不可、実native/Root/VM/DB/鍵/四held全HOLD、実FS互換/全451/正式1964-53/newleaf0/工数null/IT-ST未完。日時/OS/JDK/branch/source/input/command/exit/expectedrecipe/actualXML/counter/hashは独立manifestへ。通常区切り後も477継続、fresh残10%以下で新規停止/5%保全。
