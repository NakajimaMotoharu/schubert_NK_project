# API/Web標準metric組立 十二同値命名 PG/PT結果

2026-10-27、source5a16139a752e2404cd6c26504760f4568ac413fd/dev-foundation、仕様2243/原1793・1795/BUG1929/YKT1678/PG-D712。二TestのString十二/76参照のみ、Main/RD/UI/SS不変更。原全26tokenの独立逆復元・metadata負例28に合格し、元期待値/独立golden/phase順/例外identity/GC-close順/10秒期限を保持。新TestID0、過去の26成功を当sourceへ移植せず変更後の元26を一回だけ実行した。

|検証|公開manifest（provisional配下）|SHA256|結果|
|---|---|---|---|
|同値plan|PG11670-standard-composition-literal-plan-v1/manifest.json|af6206742ae9e6e6f362b5a0d4695d137890ed373b2f9c4167781c974b982b3a|十二/76、actual0|
|独立逆復元|PG11672-standard-composition-literal-source-post-v1/manifest.json|c5cc4222f1ab8f7d755820f1db78f41815c4a37efdfe76179afb909452e62a11|全原26/28負例0|
|normal六compile/package|PG11674-standard-composition-literal-six-compile-v1/manifest.json|15a6eeb057afdb021d0403af21625b84664c7df00c9da343954cfe02762a4ce1|format/NullAway/JSpecify/lint-Werror/Enforcerを含むactual0、PT0|
|元26通常PT|PG11676-standard-composition-literal-host-v1/manifest.json|0b1d596e787572a815067ee1abaf91b5ef18f7b0c89a26c0a6fd58dfa46b570b|26/二suite、failed/error/skip/abort0、target0|
|実static|PG11678-standard-composition-literal-static-v1/manifest.json|d8819401772f3a93f4ed5eceb2b2a7ceb7373583b393b74690f2ca1b6f5ae73e|raw20→8/duplicate十二解消、PMD processing0/CS0、gate1を保持|
|独立XML/exec/全byte/coverage|PG11680-standard-composition-literal-post-v1/manifest.json|d70ecaf62d1eea0b4f28d2a989819429032ccf30328687113d34cc0bb75457f6|actual0、CRC不一致/範囲外Product hit0|
|現8理由|PG11681-standard-composition-owner-context-v1/manifest.json|f95d9c351fa88d09670621a26d29bd918851b1e05c733a30db40ffffbd38d225|既thread四再認証＋closed入力四新source点検、全raw保持|
|理由独立確認|PG11683-standard-composition-owner-context-post-v1/manifest.json|85d75233029ef6a6149dc2539dd90c73af5e4e40e1472f9cb0dddd420e69293c|現XML/span/method/case、八metadata負例0|
|担当trace|PG11682-standard-composition-literal-trace-v1/manifest.json|13bf63d703563dadf0f6e53520e280439a73a286ff87e3a3ada300d82500b522|既983row中二SHAのみ/他981同一、主/費用P018-09保持|
|trace独立|PG11684-standard-composition-literal-trace-post-v1/manifest.json|050a1eda3c2bce3ca67206f06ea7cfb3ccb2797a2738ba58a6041ff39e62bd15|1808/1810/不明2、元予算・受入不変、全監査before/after同HOLD1|

一exec/session=PG11676-STDCOMPOSE-JPだけ、normal六Main全1843byte同一・Test全1962の二SourceFile由来だけの物理差を独立確認。selected MainはApiStandardMetrics LINE21/METHOD6/CLASS1/BRANCH7、WebStandardMetrics18/6/1/4、各miss0、計39/12/2/11全正分母で四100。完全API467/Web358の全classを別に測定し、全artifact四100ではないことを保持する。helpersの一部実行を全helper又は全module100へ換算せず、旧exec/nativeとunionしない。

残Close四は006/011のfresh memory RegistryをSUT前に即一度closeし、implicit reclose無しをassertする必須契約。Thread四はJ2EE禁止の非適用を専用JavaSE JUnitのown4worker/64有限atomic-recording task・get10秒/TWR及び当source013成功に限定。理由はR四/CONTEXT四でraw保持/currentWhole pending、実DB/外部所有・Root終了/actual serviceの証明にしない。JUnitはown SDK/公開自己JVM MXBeanのみ、強制GC・socket・DB・VM・保留操作0。

環境=Linux/JDK25.0.4/Maven3.9.12/JUnit5.13.4・Platform1.13.4/JaCoCo0.8.15/PMD7.28/CS14.3、実command/時刻/入力hash/終了codeは各manifestのbegin/stages/依存束へ。再現はimmutableな同OUTを上書きせず別new-only runで必要時のみ行う。原成功の確認目的再演なし。初回event生成の未登録categoryはappend前に拒否、登録済IMPLEMENTATIONへ訂正、製品source/job/元成功に影響なし。正式1964PT/53scope、個別17/190、工数null、QA051finalHOLD/全安全HOLDは未変更。全F03/451/IT-STの完了ではない。
