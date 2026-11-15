# SSC413 ADMIN最終消去境界・独立追加仕様

SSC412に続くBUG2993/YKT2522の内部testability補足。PG33556全28FES0/既定四100とPG33560無filterbranch-line-method-class100は保存するが、BootstrapAdminService.createのencode例外finally 6instruction未達なので全Code未資格。到達不能扱い/coverage除外/合成PASSで閉じない。

BootstrapAdminServiceのprivate final PasswordHasher fieldをprivate final Function<char[],String>境界へ変え、既public noarg descriptor()Vを明示public constructorで保持し this(new PasswordHasher()::encode)へ固定bindする。package-private BootstrapAdminService(Function<char[],String> encoder)だけをnon-null内部試験口としObjects.requireNonNullでinvariant確立。外部設定/HTTP/DB/bean/roleからencoderを選択する経路を追加しない。既Productionは全て引数0呼出を維持し、PasswordHasherの公開default pin/PBKDF2-v1/validation/SQL/認可/owner/再送/正常戻り値を不変更。create内passwords.encode(normalized)を同じ引数のFunction.applyへ結ぶだけで二段のfinally消去を維持する。

新BOOTBOUND019はメモリ内throwing FunctionのRuntime/Errorを各独立に作り、NFC前24charのcaller入力、観測NFC後12charのnormalized配列の全0、同一failure、SQLがexistsまで4文でinsert/audit0、取得済resource終了/caller非操作を確認。null Function ctorはfailfast拒否。実provider/algorithm/credentialを操作せず、成功暗号期待は旧独立JCA三Testを保持する。旧18Boundary/4Hasher本文はbyte保持＋新1、定義は新群合計20/既security9、全29/5Main6physicalを同source一exec、RootNullAway/lint-Werror/CS/SB/PMD全site、CRC-init/既定・無filter全Codeの四100（instructionもmiss0）で検証する。元27/28は未資格として保全し新29へ加算しない。

費用は元開始.9/2.7/6.0と追補.9/2.7/3.9、現群計1.8/5.4/9.9 cap10を据置き。追補の内訳をresource .6/1.8/2.4、Hasher fault .2/.6/1.0、ADMIN direct fault .1/.3/.5へ再配賦（合計同じ）、今回追加予算0・手戻り実費/token不明。追加発見と再認証を完成率へ変換しない。原費用/SV/原904.85等/正本625・元190・正式1964/53・工数null、実DB/BootstrapAdminMain/native/RootActual4/VM/aru/全PGPT/ITST/HOLDは維持。
