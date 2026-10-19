# F03残enum21内部命名・独立値catalog仕様

実行追補BUG1479：元5732-v1はNoTests guardで終了1/新五case not-run。POM/guardは維持し、新v2へprotocol独立PayloadGoldenVectorTest三件（SS322/323の64layout固定hash）とWeb HttpByteRangeParserTest四件（SS333の固定interval/境界/null/100parse並行）を必要なreactor契約として追加する。PT_DEFAULT、通信/外部data/サービス無し。全12件/7suite・各六module最低一suiteの一致を要求する。下の当初五caseは新規fixtureの内訳であり全実行期待件数は12へ訂正、元失敗証拠を上書きせず新Main/Test sourceはfe8aと同byte、変更は工具/記録だけ。既成功確認の無根拠反復ではなく当新sourceに必要なreactor限定契約であり、正式/全体へ合算しない。

2026-10-20、BUG1478/YKT1237、WBS-F03主担当（共通費再加算0）。NK-OPS-001/NK-AUT-001/NK-MSG-001/NK-BAT-001/NK-DAT-001、411/451。PG5732/5734のsourceは次clean commit、群1332開始見積.5/2/5pp固定。対象は915 BUG1478の14enum/21private field、先行protocol27と合わせ37enum/48field。外側の実起動/回収/DB/permission/所有コード不変更、SS正本変更無し。

## 独立oracleとTestID

各fixtureは対応moduleの`EnumValueCatalogCompatibilityTest`。全値/名前/順序は明示literal、expected生成にProduction methodを使わない。既SS/固定試験表を参照し、Mainから自動生成しない。

|TestID/class package|期待値の根拠・確認内容|
|---|---|
|PT-F03-ENUM-API001 / api.security|SS314 §5 User5/IP10、SS321 §6 SYNC1MiB/ASYNC0/WEB_LOG64KiB、SS331/SSC006のnk.async.work/nk.dead.letter。既LoginAttemptStateTest/OutboxPolicyTest/ArtemisConnectionFactoryProviderTestの独立表と照合。全getter、閉変換、null/空/未知/大小字違い。factoryは作らない|
|PT-F03-ENUM-STO001 / storage|SS342/343 §6固定Web/API ID、既ServiceCredentialIdTestの明示五＋五ID/owner/kind表。全getter/二role選択/null拒否、credential実体は読まない|
|PT-F03-ENUM-BST001 / api.file|SS343 §6.4（1001行付近）AES四固定名とcurrent必須/previous任意、SS342/343の固定八Unit対応。全getter、DBus/native/file操作無し|
|PT-F03-ENUM-BAT001 / batch.repository|SS331/332§11/341、既CleanupRepositoryTest/CleanupStepValuesTestの九固定SQL名/上限1000・logs10000/step対応。SS341/343既定SUCCESS0/WARNING10と十stepのbackup二件。SQL実行無し|
|PT-F03-ENUM-OPS001 / batch.platform|SS341/342/343固定Unit名・停止順・Rootサービス五・観測八・start対象五、SS343 SSC106/107/125固定directory/intent名とMorning/Cleanup担当。全getter/controlGroup/ownedBy全service＋nullを明示catalogで比較。Unit操作無し|

全14型についてJDK ObjectStreamClassのenum既定serialized field0/UID0を確認する。公開enum名・定数順序・値が上表と一致し、private fieldをserializeしないJDK enum契約を維持。1181固定enum streamは既protocol側の独立文法試験として保持するが、別sourceのPTへ合算しない。shared immutable final enumなので新並行/再送状態・資源取得・transactionを追加しない。

## 実行・照合

462/PTPRE006=PT_DEFAULT：有限合成literal/通常ローカルJVM/自己snapshot・target、offline。`pg5732_enum48_selected.py` のwrapperは六moduleformat/compile/型null/限定五PT/package/JaCoCo/SpotBugsを行う。Test選択無しmoduleがあるためfailIfNoSpecifiedTests=falseはreactor依存用であり、全五suite/五caseのXML集合一致/FES-flaky-rerun0を別に必須検査する。未選択全体を実行済扱いしない。全1664物理Main/六module静的0、対象14enumの実line/method/class全miss0と存在するbranch全miss0を要求する（元々branch無しは0/0と記録、除外追加無し）。module全体coverage未達を隠さない。

新clean sourceで一度だけ実行、元begin/archive/source/command/開始終了/exit/XML/coverage hashをnew-only safe manifestへ保存する。次`pg5734_enum48_static.py`で同source全849Main/当六compile1664byteを入力にPMD/Checkstyle、元6dbとの37file全変更をenum内の明示private renameモデルと全37実javap ABI/opcodeで照合。nested enum以外の外側処理はsource全byte不変を要求する。CP番号/表示padding/private名以外は同義化しない。PMD警告exit4を保持し当48field警告消失とF03全体受入を分ける。

拒否PT代替0、実VM/DB/Artemis/認証/credential/Unit/intent操作0。PTALT001/002の未特定操作、元failed-cohortと実所有条件は保留。新全体/実native/CHR/451正式/QA051final/工数率は別未受入。実結果とhashは次結果文書へ保存し、通常小群終了後も許可済み後続作業へ継続する。
