# 2903 純Login policy原whole十五・現source単体テスト仕様

Program NK-AUT-001/実作業WBS-P007-01、AUT001/FUN001009・UI225226242・SS314§4/5・331332、元2395/2396と2317/2318の独立literal・境界・null・並行history・消去を維持。source6b53/normal14216のMain四/Test四全文/initializer/helper読了、現1777registryで対象全未登録。原Username3/PasswordPolicy3/State5/Sequence4=15method/4suite、assert反復をTest IDへ水増ししない。旧e49/736の成功は歴史として保持し現sourceへ輸入0。

UsernameはNFC/trim表示1..64UTF8byte、Locale.ROOT比較key最大96byte、U+0130×32/display64-key96、ギリシャsigma/ownJVMトルコlocale変更finally復元と全Unicode scalarのJDK最大増幅3/2。Passwordは合成char配列だけ、Login1..256byte/creation12..128codepointかつ256byte以下、NFC/補助面/username case差同一拒否/末尾space/control/不正surrogate/全null・成功失敗の入力zeroize。期待のUnicode literal/長さ/ゼロ配列はProduct出力から生成しない。実password/credential/hash primitive/照合/実認証は対象外。

State/KindはUSER5/IP10、15分窓終端一致を含みlock終端一致は失効、Retry-After独立ceil0..900、lock中同instance不延長、成功clear/並行に分岐した不変history、時計逆行/Instant上限/不正Optional/null拒否。Sequenceは元2395の独立USER00:15:04/IP00:15:09・全900秒/2700境界・history独立性をliteralから照合しProductをexpected算出へ呼ばない。実DB/Repository/session/再送は別必須gateで今回非該当、実Clock readなし。

PT_DEFAULT：標準JDK正規化/文字列/配列/record/Instant/Duration/OptionalとJUnitのみ。外部通信・ファイル・credential・Graph/分類器・DB/JMS/native/Root/permit等0、原whole四を通常JUnitで選択しHOLD Test抽出0。Main Usernameの原baseline owner/costP01809と他MainP00701を保持、今回change-ownerから再配賦せずTest四UNKNOWN。新scopeの権限や外部受入を与えない。

command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15368_pure_login_policy_fifteen_pt.py。全normal/current/snapshot・Main4/Test4/実Jar一classずつをpin、新slot/fresh原Test compileと本人一JVM/session。共有postv2の全Code/無fixture/namespace一致/既baseline条件の閉profileで完全四Sourceを分析、公式record/enum filterだけ・手動除外0、B0/非空四100/未達を分ける。独立postで全15XML/CRC/source/独立literal表・counter・消去assert/意味反例を確認、動的成功と静的/正式を混ぜない。群3297開始1/3/8固定、共同metadata費は先行Time群へ含め二重加算0。結果2904/manifest/実commitへ。工数率/専有実費/tokennull・正式1964/53・歴史17/190・QA051final・全HOLD不変。
