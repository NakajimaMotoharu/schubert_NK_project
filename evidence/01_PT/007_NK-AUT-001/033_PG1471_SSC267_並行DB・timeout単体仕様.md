# NK-AUT-001 SSC267 並行DB・timeout単体仕様

対象AuthenticationService.authenticate/LoginAttemptRepository.lockForAttempt/AuthenticationServiceTest、RD AUT001/SYS004/DIF016、UI226234、SS314§5.1/332/353/SSC267。Production Main769、選択snapshot75a871723f9e4f0ac82cf6629bfdba34f6ff49a4。実cryptoとSQL invariantを独立試験へ分割し、hash/role期限/外部9000/lock順/session上限を変更しない。旧1461/1466/1467は失敗のまま。

| Test ID | fixture・入力・操作 | 独立期待値・根拠 |
|---|---|---|
| PT-AUT-004-CONCURRENT-SSC267 | real PostgreSQL18.6/Production DDL/provisioning、同owner8worker、独立固定合成password double、三成功→別seed→12成功→20誤password | 三成功の有効session2/最古REPLACED1、12成功後session全12/有効2/LOGIN_SUCCEEDED12、20誤passwordはAUTH_FAILED4/LOCKED16、User/IP failed_count5、総LOGIN監査32。SS314 lock境界/DIF016から固定SQL後条件、doubleは実crypto性能の証拠ではない |
| PT-AUT-004-TIMEOUT-SSC267 | role設定statement1500ms/lock500msを独立query確認、別transactionがuser7行FOR UPDATE保持、realService.authenticate→Infrastructure例外→caller rollback→blocker rollback | 固定例外messageだけ/char配列全消去、session0/audit0/IP row0/User failed_count0。SS314 timeout9000・counter不増、332 rollbackから固定SQL値。SQL timeoutを成功へ変換しない |
| PT-AUT-004-REAL-CRYPTO | 既6認証caseのJCA PBKDF2-HMAC-SHA256/310000/16byte salt/256bit golden、正常/誤password/no-account/disabled/lock/window/Unicode/null/内部fault | Goldenは独立JCA、成功失敗/lock/hash省略/transaction rollback/password消去は既明示assertionを維持。production encodeからexpectedを生成しない |

実行 `python3 -B tools/quality/pg1471_auth_static_corrected.py` はnew-only専用server snapshot/target/tmpを固定、実Maven commandはprivate begin.safe.json参照（credential無し）。Ubuntu26.04.1/JDK25.0.4/Maven3.9.12/PG18.6、worker1/heap768MiB。正常・異常・null・並行・faultは認証8caseで検証、再送/JMS外側境界/全coverage/CHRは本限定受入へ含めない。BUG1108/YKT877/SSC267、診断保全BUG1109/1110/YKT878。F/E/S/flaky/not-runを合格へ算入しない。

Coverageは選択runのJaCoCoのみで100%未認定、同Main byte401資格/静的0は1474独立確認。必要fresh全6/同source native/正式451は後続。証跡 `evidence/provisional/PG1471-SSC267/manifest.json` と034へ、rawDB/log/credentialはGitへ格納しない。
