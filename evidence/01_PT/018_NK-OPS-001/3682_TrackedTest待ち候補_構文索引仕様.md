# Tracked Test待ち候補・構文索引仕様

411/451/BUG2432・2443/YKT2177。原85/83候補の限定完了は保全し、横展開としてGit indexのcanonical src/.../src/test/java/*.java tracked regular filesを明示listへ固定する。RootFailedStart関連/保護二file/非regularはpath文字列・index modeでIO前除外し、除外sourceをstat/hash/read/parseしない。現在preflightは対象956/除外2、開始後差分があれば実物を記録する。

NORMAL_METADATA：own JDK toolだけcompileしJavacTask.parseだけ使用、analyze/generate/call/processor/元Test/製品compiler/classloader/fixture/VM/DB/Root/native/秘密raw0。source型表記内のstring/char/textblockはliteral除去・改行/tab除去し、initializerは識別子/型/CALL形状だけを出力、literal値を公開しない。get/join/await/wait/park/parkNanos/parkUntil呼出しと参照、引数数・位置・所属method/class/import/宣言を索引する。get等は名前だけでFuture/危険/安全と判断せず全receiverをUNKNOWNとする。

独立postは明示list/除外前提/source hash/同Git/全位置・空非空argument/Tool classpath・parse-onlyを確認する。新corpusの索引数を旧83型分類へ加算したり検索だけでYKTを閉鎖しない。新Test/PT/coverage/unique/whole/正式加点0、動的HOLDを維持。実際のtyped future/barrier/latch等を次群でowner/型と全original Test graphへ対応付け、必要なPG/PTだけを選ぶ。原2/5/9pp cap10・WBS-F03 REWORK、N/T・専有費不明null。

候補確認履歴（加点0）：ServiceDatabaseAdmissionTestは@BeforeAllの実PostgreSQL/DriverManagerありHOLD、fixture抽出やhook無効化で再演しない。JmsReplyEnvelopeContractTestは既PG18602全四成功/20790保存契約joinがあるので確認再演しない。Api/WebConfigurationLoader.productionはNative ServiceConfigFiles factoryを含みwhole scopeの起動HOLDを維持する。これらを未実装と推測して新fixtureや重複Testを作らない。
