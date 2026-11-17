# SSC451/452 同source全Protocolの単体試験仕様

Program 002_NK-PRO-002、対象 FieldCodec/PayloadCodec/PayloadSemanticValidator。関連RD NK-PRO-001/002/003、UI232～237、SS322/323/333/354、SSC451/452、BUG3111/3180～3182、YKT2583/2647/2649/2650。

Core8e32d13078、Profile4779、169Main/176physical、36Testsource/156定義。原152のassertion/独立golden/五TSV/64layout389field69型は保持。LargeResult negativeの一呼出型だけを非公開LargeResultDigestへ移す逆変換で元source SHAを照合済み。publicnamespace四は公開type/constructor無し/publicfield無し/固定static API集合を確認し、private反射/空instanceなし。対象case: fieldCodecHasOnlyTheEightDesignedStaticOperations、semanticValidatorRetainsBothDesignedEntryPointsOnly＋原normal/boundary/null/error/golden。全156のTest IDはprepare expectedCasesとJUnit classname.nameで一意対応し、他Program参照は追加費0。

入力と独立期待:原golden bytes/SS offset/固定SHA/record literal/異常UTF8/数値境界/NFC/null/未知/例外/有限worker fixtureを無変更使用する。新namespaceの期待集合は設計で固定した8/2/1/2操作。expectedをproduction codecから作らない。実DB/JMS provider/Root/VM/native/鍵等を起動しない。

実行環境:hostLinux/Java25.0.4/Maven3.9.12、Root ErrorProne2.50/NullAway0.14.1/JSpecify、PMD7.28/CS14.3/GJF1.36.1/SpotBugs原規則。command: `PYTHONPATH=tools/quality python3 -B tools/quality/pgpt_closed_host_profile.py run evidence/01_PT/018_NK-OPS-001/input/4779_ssc452_profile.json <固定Unitcommit>`。実行前static/ABI/全caller481compileを要求する。

coverageは同singleexecの全176physical/actualCodeを未filterでline/method/class/branch100（instructionも不足検出）、自然NoCode0/0だけN/A。全条件/全例外/negative・NPE契約と独立XML/CRC/initを照合。Failed/flaky/skip/notrun/旧exec合算0。実行/coverage/対象Unitcommitは未確定・未実行、結果/証跡hashは対応結果文書へ記録し、現時点PASSなし。全六module/451/正式1964-53/元17-190は別終了依存。

## 実行前source固定補足

Corea013a6d676／Profile4782（4782_ssc452_grammar_profile_v2.json）へ更新。BUG3183/YKT2651: 先行nonnull selector側のequals比較へ統一、MIME不適合nullはprivate nullable-return helperで明示し元reject/入力/期待保持。全API差0/全caller481と新169Main/176physical/156全PT・全Codeは当sourceで確認する。原8e static83は旧source限定であり新sourceのPASSへ流用しない。156未実行。
