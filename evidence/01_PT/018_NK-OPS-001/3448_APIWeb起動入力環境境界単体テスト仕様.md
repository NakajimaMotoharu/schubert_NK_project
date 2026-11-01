# API/Web起動入力の環境境界 独立単体テスト仕様

PG17990/event3705、source6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備、HEADbd801e101ad6b52248d36229b400f8d76f2b18ab/dev-foundation。主F03/関連P01805追加費0、固定1/3/6pp cap10、fresh82/18/reset1793774153。NK-OPS001/SYS002004/UI243253・origin/main8b91944d（fetch17:43真正0）SS342343§4/6、PG279/新PG-D1114。

2895/2896/2929/2933/2934後続を確認。両StartupInputs全42行、両ConfigurationLoader、両NonSecretConfig、ServiceCredentialLocation/NonSecretConfigSource、ChildStartupContext.isDescriptorKeyとouter定数initializerを読取。新二はinjected Mapのguardだけ、旧原Inputs四ずつは同一execで全Source測定に必要repeat八。Web原Login/Mockを新群へ含めない。旧source/成功確認だけの再演/保留Test抽出0。

|Test ID|入力・操作|独立期待値|
|---|---|---|
|API-ENV-GATE001|configroot正規、無関係LANG有り、誤root/空/末尾slash/正規化alias、config欠落/null、未知SCHUBERT_NK_*|正規exactrootだけvalidate正常、異常はAPI non-secret environment unavailable/cause null/suppressed0。すべてsource.read0|
|WEB-ENV-GATE001|同境界・Web固定location|同条件でWeb non-secret environment unavailable、全source.read0|
|既API-INPUT001～004|source API/DEBUG/pool8/読取一回、位置欠落/source故障/誤root/null Values|原literal/呼数/例外identity保持、必要repeat四|
|既WEB-INPUT001～004|source WEB/DEBUG/port8080/読取一回、位置欠落/source故障/誤root/null Values|原literal/呼数/例外identity保持、必要repeat四|

固定CREDENTIALS_DIRECTORY文字列は非秘密location値だけでdirectoryを開かず、inode/ACL/実credentialを認証しない。新未知keyはChild.isDescriptorKeyの定数二名比較だけへ到達、NativeIo/default constructor/inputs/verify/FDの採用はしない。Mainに含まれるproduction factory/ServiceConfigFiles outer初期化/環境getenvは呼ばない。旧原八のYAML/Map既定parseはJDK SHA256の非秘密canonical UTF8 hashを実計算するためcryptoOrKeyOperationsInvoked=true/publicDigestOnly=true/actualSecretKeysLoaded=falseとして専用postで開示。旧2929訂正を保持し、crypto=false sharedpure profileへ強行しない。

新二・原八はmemory/Path値/YAML/CPU hashだけ、explicitファイル/DB/JMS/HTTP/Thread/clock/credential/permission/Root/native/VM/実起動0、JDK内部初期化効果null。并行/再送/実owner後条件は外側責務で未実施。期待値は手書literal/null/読取counterだけでProduction expected生成0。

全二Source/四Code（各outer/Values）を新十件四suite一JVM/一execで測定。旧partial二をjoint履歴保存/新単一exec置換/union0。両Sourceのbranch分母は自然0なのでN/Aを明記し、strict四100や実readiness/起動資格へ読み替えない。line/method/classは実測100時だけ三counter100として記録。正常Jar/現source/snapshot/全closure/CRC/単一session・XML/FES/公式filter/安易な除外0を確認する。

command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17990_startup_environment_ten_pt.py。normal14216/静的14224再用、Java25.0.4/親180秒。3449と公開manifestへOS/JDK/時刻/終了code/branch/HEAD/command・input/Main/Test/class/exec/hash/coverage・独立oracle/BUGを保存。quality新二/普通必要repeat八を区別、正式1964/53/歴史17/190・新WBS受入0/工数null/QA051final/451/全HOLD維持。
