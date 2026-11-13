# MqLogin既知graph内fatal保持・独立単体仕様

NK-WEB-001/NK-MSG-001、製造owner WBS-P005-02。FUN001/AUT001..004/MQ021..036、UI226/232/234、SS312SSC329330/321SSC332334/314/322323352、BUG2834/YKT2359。開始価格はPG .15/.45/.9pp（上限1.5）、必要な同source通常PT .4/1.2/2.4pp（上限3.5）。原費用と別、各一回。

対象MqLoginClient.exchangeの既知例外catchは元graphをUNAVAILABLEへ捨てる前に既JmsRequestReplyException.preserveFatalを呼ぶ。直接Error/未知NPEは元どおり、通常の既知不正・非fatalは固定INVALID_INPUT/UNAVAILABLEを維持。新catalogへprovider cause/suppressedを保存せず、元finallyでpassword/request/sentclone/reply/dataを全終了消去し、相関枠を返す。認証付与・DB・実MQ・session・鍵・新再送は行わない。

新Test ID `PT-WEB-LOGIN-GRAPH-001` は一つの通常@Test。独立作成したError objectをcause/suppressed/SQLnext/JMSlinkedへ保持する各既知例外をsynthetic callbackから送る。期待は同一Error（assertSame）、全char/送信byte zero、send一回、pending0、同一一枠clientのfresh要求が元独立golden成功すること。非fatal循環graphは有限帰還し既UNAVAILABLE・cause/suppressed無し、全消去・枠解放。identifier/clock callbackの既知型も同様。期待Errorはtestがnewした値、期待wireは元UI232/234固定offsetから生成しproduction methodをexpected算出に使わない。

元MqLogin whole7（WEB054..059＋UNKNOWN001）の全入力/期待値・二finiteworkerを維持してwhole8。元Client10/Registry7・Protocol130の全source/Test/resource byteを既保存manifestへ照合した必要な接続品質を、同一source/runのfresh155件で実施する。これは一Main変更後の同scope品質であり、新定義は1だけ。旧154の成功exec/coverageは合算しない。165protocol source/176physicalは元読取・Root資格のbyte一致を確認し、公開JAR/compiledTestを不変依存として使用可能。新Web Main7（package2）のRoot Java25/NullAway/SpotBugs/全source静的と変更TestのRoot静的はfresh。

既ProtocolのIndependentNamedFieldOracleはTSVに固定した公開protocol型だけのClass.forNameを使う元whole130内の独立oracle。generic閉域工具はこのreflectionを許可していないためguardを緩めず、既資格済みLogin normal callerの同じ全scope方式を使う。元helper/TSV全hash・対象public型・物理176・SDK・resourceを固定し、別class/actual4/Root/authorityfixtureへ広げない。

全188物理class、自然no-Code、標準javac switchmap4を元byte/Code/JaCoCo公式filterで照合し、全scope四counterと対象Mainを記録する。未網羅は残し、100%未満を全合格扱いしない。新Main/Test source・全XML/TestID・一session・CRC・NullAway/静的・source/run・OS/JDK/command/終了/hashを独立postへ結び付ける。秘密のないsynthetic文字列のみ、actual4.class/VM/Root/DB/実MQ/Backup/credential/native操作0。正式451/元190/IT/STはこの155件のみで完了にしない。
