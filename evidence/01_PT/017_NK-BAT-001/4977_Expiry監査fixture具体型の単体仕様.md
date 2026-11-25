# Expiry監査fixture具体型の単体仕様

NK-BAT-001、SS341 §9、SS332 SSC-461、PT-F02-EXPIRY-GRAPH-001/002、EXPPORT等。元PG42958の保全済み31件を単位とし、JDKの合成Connection、Statement、ResultSetを用いる。正常時のUTC七日基準、SQL順序、元抑制例外、固定診断、借用接続の後条件の期待値は既存fixtureの独立表とする。実DBもBrokerも使わない。

成功条件はJUnit31、失敗・エラー・スキップ0、現fixture各SHAと実javac引数の一対一対応、生成classの具体例外属性を実行前に確認すること。STAGEとFINISHに注入するLinkageErrorは元インスタンスをそのまま返す。原scopeの四実装型は、単一execの行・メソッド・クラス・分岐に未到達0。六製品451・実Unit・libc操作は別。BUG-3838～3840、YKT-2995～2996。
