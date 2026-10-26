# 2101 Direct enum期待入力十三の型・定義対応仕様

2026-10-27、G03.01/群2447開始.5/2/5pp cap10、source370/正常10632変更0。残named51からRole.ADMIN/USER七、ResultCode.AUTHENTICATION_FAILED/LOCKED三、ArtemisQueuePressureClient.Pressure.NORMAL/WARNING三の候補を分離する。Pressureは同client内のenum、値recordはValueであり、名称だけから型階層を推定しない。

明示三Main sourceのenum宣言/定数、現source SHAと正常入力、各Testの実import又は同package/影の同名型不在を確認する。期待側はenum memberそのものの固定選択で、wireValue/fromWire/認証/DB/JMS/Main getterから値を生成していないことを限定レビューする。ResultCodeのwire mappingや当業務の期待roleの適切性、各fixture全体までは本確認から認定しない。

原constructor型/値保持本文/原AST行/hashとsourceを結合し、元named51全row参照を保持、十三以外の38/別method66をpendingへ残す。前固定49/既是正二を新計上0。元DB/Password/JMS/Root/native等のTest/fixtureは実行せず、enum source/opaque member入力を読むだけ。target classload/compile/製品PT/新coverage/外部操作0、別harness0。

独立postはraw式の型head/enum member/String/numeric文法を別経路で照合し、未知member/getter/同名入力変数をliteralへ読み替えない反例を確認する。結果2102/同番号公開manifestへcommand/時刻/環境/source/hash/actual exit/未確定を保存。原owner/cost/正式1964-53/17-190/工数null/QA051final/安全HOLDは不変更。
