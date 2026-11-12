# PasswordPolicy・Hasher 原6件 単体テスト仕様書

Program NK-AUT-001 / WBS-P007-01。RD AUT001/FUN001009/DAT009、UI225226、SS314§4、451/487、YKT2328 PasswordPolicy既存surrogate guardの独立証拠対応。原10source契約群の事前.25/.65/1.3pp cap2に含まれる限定通常PTであり、追加課金・追加予算・原/2の完了計上は行わない。

対象はPasswordPolicy全method/constructor・PasswordHasher全method/constructor・package annotationの3physical。原11候補（State5＋Policy3＋Hasher3）のうちState5は元window9の履歴と分けて保持し、今回確認目的の再演をしない。元190/Program全体/依存DBの受入に数えない。

|Test ID/whole fixture|入力・事前条件・操作|独立期待値・根拠|
|---|---|---|
|PT-AUT001/PasswordPolicyTest原3|ログイン1/11/12/128/256byte、新規12..128codepointとUTF8最大256、NFC・supplementary、username比較、空/末尾space/control/high-low孤立、null。各caller char配列を渡す|明示String/char配列・独立Unicode literal/tableとNFC仕様。正入力のchar値、異常IAE/nullNPE、全終了でcaller配列zero、返却clone・no cause/入力不露出。getBytes使用だけで不正とせず明示surrogate拒否を検証|
|PT-AUT002/PasswordHasherTest原3|固定salt0..15・NFDé×12、正誤入力、NFC最大256byte、新salt二回、未知/不正generation/長さ/hex/nullablehash/null/空配列|JCA PBEKeySpec310000回/256bit/PBKDF2WithHmacSHA256の独立計算とliteral {pbkdf2-v1}/96hex。production methodでexpectedを作らない。全byte passwordが照合へ反映、salt変化、unknown世代拒否、全caller配列消去、causeなし・固定例外文|

public synthetic fixtureだけを使い、実password/credential/鍵/session/DB/認証要求を作成・読取しない。SDKはPOM固定SpringSecurityCrypto7.1.1/SpringCore7.0.9/commons-logging1.4.0、JSpecify1.0.1、JDK25.0.4+7。SDK/JDK内部を自前production classへ合算せず、所有Main2の全codeを対象とする。Source Main/Test変更0、新定義0。

PG26700はAPI jarの許可3entry payloadだけを読み、公開normal hash/現source一致を確認してTest全6をfresh compileした。jar全体hash/他entry payload/actual四class binary I/O0。PG26702 Test PMD/CS0・処理error0、PG26708独立preflight0/GJF0、Main3の既same-byte NullAway/Mainstyle/SB ClassStats3指摘0を範囲限定再利用。compile/staticを製品PT成功扱いにしない。

予定command: `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1313_password_current_qualifier.py run <fixed-source>`。自己所有単一JVM/paralleloff、session PG26710-PASSWORD-WHOLE6、timeout120sec。XML全6/終了0/FESaborted0、Main2のCRC/初期化、source/byte/run、全3physical保持・line/method/class/branch未網羅0を独立postへ保存する。手動除外/oldexec合算なし、package annotationのJVM code0だけ自然非実行として別記する。

P00701/2全体のLogin/User→IP lock/5-10閾値/15分window・max2session/DB/audit/終了依存はこのpassword群の対象外であり別gate。実IT/ST/全451/正式1964PT53scope/元190/工数nullは維持する。実結果・OS/branch/source・command・終了code・期待/実値・coverage/hash・関連YKTは別実行結果とmanifestへ記録し、未実行を合格にしない。
