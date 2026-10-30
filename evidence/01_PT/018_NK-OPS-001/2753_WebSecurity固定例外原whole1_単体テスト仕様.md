# Web security固定例外 原whole1仕様

2026-10-30、主費用P015-02、着手前.25/1.5/3pp、source6b53/normal14216。NK-WEB-001/FUN-001/AUT-001～004/MQ-004、UI226/234、SS314§3.1/352、SSC043。元web.security.ExceptionValueContractTest全1/PT-F03-EXC012/exc012LoginFailureAndLockDelayKeepTheirClosedValuesを変更せず実行。全Test/Main二型とReason/initializerは既読、fixed例外構築だけでLogin/session/CSRF/context/鍵/credential/HTTP/DB/Root/VM操作なし。

期待値=既存各reasonでfixed literal `login exchange rejected`/cause null/reason同一、null reasonはNPE。lock delayは固定0/1/899/900を保存しfixed literal `login temporarily locked`/cause null、MIN/-1/901/MAXはIAE。許可範囲0～900と固定文言が独立oracle、production methodからexpected生成なし。reason列挙の互換性全域や外側Loginは本群で認定しない。pure値型なので資源競合/再送は非該当、外側の同条件を推定しない。

全二Source/三physical=MqLoginExchangeException（Reason含む）/MqLoginLockedException。既registry816のSource/caseと重複なし。command `PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14712_web_security_exception_one_pt.py`、一fresh JVM/一原method/一suite F/E/S/not-run0。独立14714は資格済v2を使用（BUG2109/2752、一method metadata反例の是正済み）。全closure/原環境/全input・六Jar・静的14224/一session-CRC/八反例/四counterを照合、自然branch0はN/A、未達保持、旧coverage合成0。manifestに日時/環境/source/branch/commit/command/exit/入力期待case/実XML/exec/counter/hash/owner、結果2754。正式/工数/全HOLD不変。
