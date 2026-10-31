# Artemis startup proxy原whole3仕様

2026-11-01、PG17200-ARTEMIS-STARTUP-PROXY-ORIGINAL3/WBS-F03、開始1/2/4pp/cap5。Source6b/normal14216、Main SHA6b92bf3c、Test15f71ae9を固定。全元Test約190行/Main全体を確認、部分抽出・新fixture0。元3@Testをfresh compile/一所有JVM/session/180秒で実行する。

OPS-MQ029：固定六addressと0→5のcallback順、immutable copy、公開constructorのdefault経路はunusedSession proxyの最初のaddressQueryでliteral AssertionError。このproxy以外の実session取得/接続はない。030：nullとdetailed未提供拒否、六段階の失敗で後続callback0、元独立固定message/callsを確認。031：空/不足/過剰/null要素/全null圧力map拒否、fatal同一性と後続0、六callback null拒否。

全default client constructor/初期化はliteral Map/Setとread関数参照、ThreadLocal.withInitial(Optional::empty)のみ。Role fields/approved、Queue limits、Address capacities、ArtemisReadinessClientの最初のaddressQueryまで確認。実broker/EmbeddedActiveMQ/transport/session生成/JMS send/consume/credential/Root/VM/DB/Thread0。AddressSettings/Acceptor等別Testは実brokerのためwholeHOLDで実行しない。

既Sourceの旧15775 Evidence値原3は再実行せず、旧counter/proof保持。今回も全一Source二Codephysicalを測定し、Evidence未実行/未達を含める。旧execとの合成0、全Source受入増0。独立oracleは固定順序0..5/六key/保持copy/例外identity/null/unknown session method文字列。CRC/session/元XML/JVM/normal/静的六module既14224限定参照/全counter/四held六nativeとRootFailed/Cycle/inactiveを受動確認する。Test IDとdocSS321/342、関連MQ001/002/009/010 SYS004 UI231/251/253を束縛。結果3353、registry/WBS3354へ、正式1964/53/工数null/全HOLDを維持する。
