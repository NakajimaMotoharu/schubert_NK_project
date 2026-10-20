# 1301 API factory/close選択v1：新fixture警告によるcompile不合格

元exec84319/pg6150-api-factory-close-selected-v1、source **c51ea85db941ed76d73c4ec839b9e5c9d37165c0**。2026-10-20T18:35:32.769946Z→18:36:38.180033Z、真正1/Maven1/phase[0,1]。予定1955/321に対し前5/3のみ、FES0・**1950件not-run**、八target未測定（欠測placeholderを100にしない）。API新親factory TestのTWR ownerに二度明示closeして-Xlint:try二件/-Werrorで停止。全Test成功/六静的成功ではない。元のMain compileは通過したが、当sourceのPTは未実施のまま保持する。

私有PG379/pg6150-api-factory-close-selected-v1/：begin.safe.json **5319ba8f2fc85d997422e038ccee3eb39255766741dcb3039928526f6f752b64**、source.tar **1b183a095a48323f816c44ccbc3fe4cb42edc55b04002d737e114f9bc688db78**、manifest.safe.json **070a110dcf4a226d0bd5a54575c498676333e4a1f50e53e1a011abaf2b6b023a**。原commandはPTPRE039/pg6150工具・固定JDK25.0.4/Maven3.9.12/通常自己所有host、原XML/log/入力を保全、元job再発行0。

BUG1555/YKT1313を先行登録、ownerを通常localへし既外finallyの自己所有全locator解放を維持する。Production/期待close回数/警告設定不変更。元Test compilerはin-processで完全argvファイルが保存されていなかったため、予定していた「元完全引数の再利用」は実施不能として明記し推測で補わない。代わりに既POMの実executionを確認し、新固定snapshotでAPIと依存四moduleの通常 **test-compileまで** を実行するpg6153を用意。validateのformat/enforcer・Main型null/全Testの既-Xlint/-Werrorは維持し、Surefire/PT/VM/DB/サービスを起動せず、TestXML/JaCoCo実行データ0も検査する。これは静的compileの追加費で、実行PT/coverage/PTALT代替へ加算0。

compile preflight0後のみ新only6154選択v2を一回。旧6150の元結果を上書きせず、元v2/6144の六oracle失敗も保持する。個別criteria/正式1964-53/17-190/工数null/QA051final/PTALT未特定・実環境安全HOLD/原v3v4を変更しない。
