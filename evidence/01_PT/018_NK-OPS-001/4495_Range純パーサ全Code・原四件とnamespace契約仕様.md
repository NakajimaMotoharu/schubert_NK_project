# NK-WEB-002 Rangeパーサ全Code仕様

RD FUN005～007/PER004～006、UI223237、SS333§10/354、費用主担当P00904。追加 .25/.60/1.40 cap3。PG27002/26990の現Java/Test同一・Parser五physical/current旧byteを照合し、保存済みexecをunfiltered解析する。確認目的で元186/4の試験は再演しない。固定record hash/toString/enum契約は原HttpByteRangeParserTest4に既にあるため新重複caseを作らない。

もしprivate空constructorだけが未網羅なら、修正前BUG/YKTへ記録し、public final static utilityにinstanceを作らせない内部namespace invariantを明示guardで確立する。public/private署名・HTTP/Range選択・1MiB上限・byte互換は変えない。これは全Code除外やunreachable扱いでなく、private namespaceの将来の誤構築も早期拒否する実装契約。PG判断記録と一つのwhitebox constructor試験（アクセス状態をfinallyで必ず復元、InvocationTargetExceptionのcauseは固定AssertionError）を追加する。原4 source/独立業務oracleは維持し、変更したMainに必要なsame-source whole5を一回行う。

原4は正常/first range/大小文字/空・未知/数値桁あふれ/算術例外/null/FullとPartial不変条件・全generated accessor/equals/hash/string・Unsatisfiable防御配列/valueOf・並行100/有限ownerを既に規定する。期待値をproductionから生成しない。新namespace1は製品private構築不可invariantであり単にObject非nullでcoverageを増やすものではない。

原Java25/NullAway POMのsafe Mainと現Protocol175参照、全physicalSB/PMDCSformat、strictTestcompile、旧五ABI同一/内部一body差、単一exec/raw全Code/naturalNoCode保持・CRC/init/XML/FESnotrunを独立確認する。Root477は一切source変更がなければ現byte証拠を参照し不要な全回帰を反復しない。実HTTP/配信/FS/認証/DB/JMS/Root/native/VM/key/権限/四held classfile操作なし。元P00904 program全体・F02F03/全451終了依存、正式1964/53・17/190・工数nullを保持。
