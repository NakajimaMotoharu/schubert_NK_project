# DirectoryCalls既定三method独立oracle対応 結果

仕様3843/scope629。Main7aed不変更、元23504/3764四成功の確認再演0。PG24062公開Source/metadata check exit0、12method内Code三/抽象NoCode九を明示し、既定三method/元四Test ID/14assertion snippet/SS333へ対応。

|method|元PT-SCN-DDEFAULT-|独立期待|
|---|---|---|
|createPrivateFile|001/004|parent0/7/MIN/MAXでも常にUNAVAILABLE、新規error、他port呼出0|
|createPrivateDirectory|002/004|名前境界/空/dot/dotdot/slash/NUL/nullも同じ固定エラー、public directory fallback0|
|removeEmptyDirectory|003/004|名前境界/nullも固定エラー、unlink/root close等を呼ばず失敗|

共有assertFailureは固定class/reason/message、cause null、suppression0を独立に照合。004では前callerのsuppressionを次のerrorへ持ち越さず、3object間のidentity非同一とnull名のtyped失敗も確認。原abstractCalls0は九提供RejectingCallsへのfallbackが無い観測であり、native処理九種の成功ではない。現Source三defaultのbodyは各fresh StorageIoException(UNAVAILABLE) throwのみ。

抽象九: openRoot/openDirectory/openEntry/createFile/createDirectory/publish/unlink/sync/close。これらにCode分母・実行成功を付与しない。実FD/ファイル/native/所有close・他callee・全G13/451は未受入。既default三のL3/M3/C1 miss0/branch分母0は元run測定であり新測定100ではない。case別probeも未測定、method/case relationは根拠linkである。

新compile/JVM/Unit/FS/FD/native/Root/VM/原本操作0、新BUG0。unique517/候補114/pending12/whole93/正式1964PT53scope/newleaf0/工数null/G07未分類3313+22actualSecretCountnull/全actualHOLDを維持。command `python3 -B evidence/01_PT/018_NK-OPS-001/input/631_directory_method_oracle_review.py`、日時 2026-11-08T15:57:35.903742+09:00、manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG24062-directory-three-method-oracle-review-v1/manifest.json` SHA256 `9e14c46bd4baec3e41eacb98aa56db99fa8139c4bda674dd09f704a30a0c542b`。Source固定と通常pushはPG24064 publisher参照。Code/defaultの明示対応をabstract/native資格や工程終了に変換しない。
