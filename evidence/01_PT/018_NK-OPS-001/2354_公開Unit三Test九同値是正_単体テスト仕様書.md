# 公開Unit三Test九同値是正 単体テスト仕様書

2026-10-28、PG-D748/BUG1984/YKT1732/NK-OPS-001/変更F03。開始見積2/5/8pp cap10、共有68残32/reset1793599188、専有費/N/T null、原見積/v3/v4不変更。前群の実装sourcefbとsaveef21557a0/push64481真正0を保持する。

## 対象・独立oracle

SS321/341/342§3/4/5/7、343§6.6/6.8/8.2と元1553/1555、全14source/終了依存2350を維持する。変更はArtemisServiceUnitTestのtrue四、CleanupServiceUnitTestのroot四、Supplementaryのtrue16/Service33/TimeoutStopSec四/30s五/Unit五/-Xms五/-Xmx六、九全82String参照だけ。定数型はString/private static final、追加class/公開API/Main/config/POM/他Test変更0。

原三whole Test・全helperは全文確認済み。原四ARTUNIT001～004はCleanup依存/専用Broker identity・固定private credential RO bind宣言・120/60秒/vendor143・2GB/JVM・hardening/無余計command、四CUNIT001～004はroot Cleanup/Expiry entry・固定credential数/名前・依存/30分又は10分/60秒/noSIGKILL/限定cap-RW・Restart等を検査。五UNIT-SUP001～005はBackup/ADMIN/Caddy二dropinの全schema/key/value/単一又はreset順・閉JVM ABI/予算不等式、12非空canary/1null guardを検査する。期待値は承認済SS/1553を原literalで維持し、Productionからexpectedを生成しない。

全method/helper/control/正負assertionは、九定数宣言だけを除き全82参照を元String tokenへ戻して原sourcefbの全tokenと独立比較する。誤値/参照/宣言欠落/型/判定変更等の非同値metadata反例を確認し、元期待値を書換えない。null/異常/canaryは自己public textの入力に対するもので、実Unitを変異する試験ではない。並行/再送/transaction/実resource closeは純設定検査に非該当とし実証済みにしない。

## 安全条件・予定実行

PT_DEFAULT：三wholeTestは自己所有snapshotのpublic Unitだけを読む。Artemis/Cleanupの`nk.pt.repository`は新専用copyを指定、Supplementaryは唯一のfrozen classpath resourceを指定する。実systemd/Unit/Root/credential target・DB/鍵/VM/ネットワーク/サービスを一切実行・照会しない。Product jarを実行classpathへ置かず、明示13methodだけをJUnitで選択する。拒否Testの部分抽出ではなく安全に分離された通常公開設定PTである。

手順：PG12570 plan/独立逆→exact三Test source固定→六normal/PT0→一freshJVM whole13/三suite→当三Test PMD/CS→独立XML/全input・resource byte/唯一classpath解決・classloadと全Main1843不変/physicalTest差分→trace/集合/完成/公開scan。全体回帰/実Unit確認を暗黙起動しない。normalのskipをPT成功へ算入せず、実13のF/E/S/flaky/aborted/not-runは0を要求する。

実command/対象source/branch/JDK/tool/開始終了/exit/入力/期待根拠/実際XML・公開出力/hashはmanifestへ保存する。設定PTのためProduction Java四counterはNOT_APPLICABLE_CONFIGURATION、0/0を100%と呼ばない。Test branch実行をMain coverageへ換算せず、Main/設定不変更でも別sourceのnative/正式全scope資格を転用しない。C02 contract/scope/qualityは終了依存未完のまま、正式1964-53/17-190/工数null/QA051final/全HOLDを維持する。元successful19/22/5や前群21を算術加算せず、今回13は変更Testへの必要回帰として区別する。
