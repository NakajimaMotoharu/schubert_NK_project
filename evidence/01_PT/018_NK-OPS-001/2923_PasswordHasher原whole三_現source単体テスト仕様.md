# 2923 PasswordHasher原whole三・現source限定PT仕様

NK-AUT-001/AUT-001/DAT-009、UI226§3/SS314§4、PT-AUT-002、WBS-P007-01。source6b53/normal14216固定、Main af26da67/Test a44c27a8/全helper PasswordPolicy/initializer全文読了。原全3Testと一Source一Codeを対象に一fresh JUnit/JVM/sessionで実行、元Policyは既資格helperで原PolicyTest確認再演なし。元Main baselineP00701/TestUNKNOWN保持、current1810に新Hasher Source/whole suite重複無し。群3312元0.5/2/5pp固定、当source資格を新設計/機能/受入へ加算しない。

| 原Test ID/method | 入力・操作・独立期待値 |
|---|---|
| fixedSaltIndependentPbkdf2VectorAndNfcMatch | 公開salt0..15、é×12とe+combining acute×12、独立JCE PBKDF2-HMACSHA256 310000/256bit・NFC一致、別値不一致/upgrade false、元char[]消去 |
| encodeUsesFreshSaltAndFull256BytePassword | é×128=256UTF8byte、二encodeは各salt16byteを独立JCE oracleへ渡し全hex96一致、二salt相違/末尾別codepoint不一致・input消去 |
| invalidStoredGenerationAndInputsAreBoundedAndConsumed | 世代不明/欠落/95hex/nonhex/空/null、固定例外message/causeなし、入力char[]は異常でも消去、null境界/空password拒否 |

期待値はProduction methodで生成せず元JCE SecretKeyFactory/PBEKeySpecから独立計算する。別Python hashlib.pbkdf2_hmacとUnicode NFC/UTF8・salt16/iteration310000/derived32byte・prefixを検算し、oracle側の検算と製品一致を元JCE assertionから確認した事実を区別して記録する。標準Spring Security crypto7.1.1はnormal固定Jar/hash6e8bb233…、additional secret空/hex・世代pbkdf2-v1は承認SS314正本。性能値はこのPTでIT/ST合格へしない。

公開合成Unicode passwordとTest内saltだけ、実password/credential/秘密key/実login/DB/JMS/network/VM/Root/Graph/permission操作なし。標準自JVM乱数だけ、provider registryの変更なし。専用postはcrypto=true/publicSyntheticTestPasswordsUsed=true/actualCredentialValuesUsed=false/actualSecretKeysLoaded=false/childLocalJcaRegistryRestorationTested=falseを明記し、sharedpure crypto=falseやSHA256 NO_KEYSを誤用しない。

command：python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15452_password_hasher_three_pt.py。rawと専用15454post draftを事前lint0で準備、元真正terminal/実hash固定後にpostを初回実行。全Input/current/snapshot/Jar/Test/launcher/reporterをpinし180秒上限・実XML/FES/一sessionCRC/OS-JDKprefixを確認、全Source一class Code全methodの四counterをpassive測定、未達は未達/追加除外0・旧exec union0。独立15456は全source/元3ID/SS正本/oracle/typed counter/flags・意味反例、Product再演なし。結果2924/実manifestに実日時/OS-JDK/branch/source/command/exit/hash/coverageを保存。正式1964/53・歴史17/190・工数null/QA051final/全HOLD不変。
