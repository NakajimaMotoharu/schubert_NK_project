# F02 ImageIOとDOM直接Fileの型付き単体仕様

WBS-F02-b、SS311、BUG-3487、YKT-2780。Controller／ProtocolからのImageIO File read/writeとDocumentBuilder File parseの6呼出しをPT-F02-FILECALL001～006で禁止と判定。借用InputStreamと他の所有者は007～010で許可する。型付きのowner、method、File引数から判定する独立期待であり、画像やXML自体はロードも実行もしない。

既File/Archive/Path/FileHandlerの合成判定を、変更工具で再確認する。現Protocolの認証済み物理入力は別runで確認し、当工具の成功を全六包装／P451合格へ加算しない。
