# 十二Source別既coverageと現method対応 結果

仕様3833、Test ID NK-OPS-METHOD-COVERAGE-12。Production Main7aed8eace7c844c2f79f2e39db766faf914890d5不変更。新Product実行0、元成功PT再演0、元exec合算0。既10runの96caseを再加算しない。

|Program/class|全physical|元LINE covered/miss|元METHOD covered/miss|元CLASS covered/miss|元BRANCH covered/miss|
|---|---:|---:|---:|---:|---:|
|ArtemisAddressSettingsReadinessClient|3|68/0|9/0|2/0|10/0|
|ArtemisRoleReadinessClient|2|86/0|8/0|1/0|28/0|
|ApiJdbcPool|1|14/0|2/0|1/0|0/0|
|WebJdbcPool|1|14/0|2/0|1/0|0/0|
|WebServiceMetricBinding|1|30/0|6/0|1/0|8/0|
|QuestionWorkListener|1|7/0|3/0|1/0|0/0|
|WebLogListener|1|7/0|3/0|1/0|0/0|
|TransactedEventListener|1|41/0|5/0|1/0|6/0|
|DirectoryCalls|1|3/0|3/0|1/0|0/0|
|ServiceDatabaseAdmission|2|48/0|5/0|1/0|32/0|
|ServiceDatabaseSource|2|66/0|16/0|1/0|24/0|
|AuthenticationService|1|54/0|5/0|1/0|24/0|

現method分母に対する当12Sourceの全17physical/87methodは、元XML測定67Code、元標準compiler filter8Code、抽象NoCode12へ個別対応。2pool/2listenerのgroup値を個別Sourceへ分離した。branch自然ゼロ5SourceはN-A/率nullを保持し、測定100へ変換しない。標準filterは元Address record7/Admission synthetic initializer1のみ、元bytesを保持し独立実行済みと主張しない。

PG23982登録exit0、PG23984独立SAX exit0（external entity無効）。class集合/全method name+descriptor/Code有無/原Source SHA/class SHA/原post ID/元JUnit96成功集合/個別counterを照合。15metadata否定を確認。XMLにID欄はなく、class IDは元独立post、coverageは元XMLと出所を分離した。原case IDの() suffixは比較時のみcanonical化し保存値は不変更。

BUG2514/YKT2252: XMLにexec/classinfoのID欄を仮定した工具KeyErrorを修正。BUG2515/YKT2253: 二旧postにはcaseTimings summaryがないため元JUnit XMLの共通読取へ、比較の片側suffix除去も両側canonicalへ是正。23990/23992/23994に初失敗・各修正前sourceを保全。新製品障害・仕様変更ではなく工具手戻りとして分離する。

全method exactPerMethodOracleはNOT_VERIFIED。runCaseRefsは元runの成功集合であり、各methodと独立oracleの一対一対応とはいえない。依存delegate/実DB/JMS/native/Root/VM/ログイン等は未受入のまま。登録名寄せ、whole暫定93、候補114/pending12、正式1964PT/53scope、新leaf0、工数率null、全G13/451未受入を保持する。

証跡 `evidence/01_PT/018_NK-OPS-001/evidence/PG23984-pending12-method-coverage-independent-v1/manifest.json` SHA256 `119621379ad6e8e2a0dd941a81db18556fbf8b6df056d5decee20c067d6a68ee`。Producer manifest SHA256 f1be310f054918c9b477f7023957c09459aa8cf147c42348570f9536f3df3363。入力pin605/追加JUnit pin610、二工具607/608、原command・exit・日時・hashを各manifestに記録。追加JVM/compile/製品/PT/backend0。source固定はPG23986 publisher参照。
