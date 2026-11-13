# Transfer列挙例外の製造仕様

BUG2765/YKT2359、MSGF07-09/UI237・251/SS33312/312/352。既DirectoryIteratorExceptionから固定IOExceptionへ変換する一箇所だけ、元fatal cause/suppressedのError identityを保持する。非fatal固定文/checkedIO/unknown型優先、全streamclose/retainedRoot/二段の実FD・unlink・guard・countは全元byte逆変換で不変。PG28486 GJF-CS0のみ、Maincompile/NullAway/fullstatic/whole6・IO8/PT/coverageは実nativeHOLD未実施、BUG2765OPEN。部分Test抽出/代替fixture/実Root・DB操作0。
