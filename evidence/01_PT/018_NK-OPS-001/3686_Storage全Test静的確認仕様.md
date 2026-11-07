# Storage全Test・静的品質確認仕様

NK-OPS-001/F03、411/451/SS311352354。storage moduleのtracked regular Java Test全29をindex metadataで固定する。これはPMD/Checkstyle/GJF dry-runによるsource静的確認だけで、全29の元Test compile/run、child main、native/FFM、filesystem/process/access変更、Root/VM/DB/credential操作を実行しない。Root11/元保護二file・四held及び拒否対象未特定操作のHOLDを維持。保護名/非regularはIO前除外し、source typeをruntimeへ変換しない。

原2/5/9pp cap10、F03 CONTRACT_AUDIT/SOURCE_REQUALIFICATION。normalMain7aedのprotocol/storage JARをsymbol metadataだけへ使用、JDK25/PMD7.28 record patch/Checkstyle14.3/GJFと既pinルール不変更。新しい共通工具は明示scope JSONとfrozenlistだけに従う。engine class-init logでProduct初期化0を独立確認し、file/rule/tool/JDK/SDK/source hashとsource不変・実exit/XML・format非変更を照合する。raw/未分類/非該当/実違反を分け、未分類やprocessing errorを合格としない。coverage/PT/unique/whole/leaf加点0。

既証跡の限定照合：PG5906 storage30はMain/旧sourceのartifact、PG11928はStorageAttributeGuardTest fixtureの旧source失敗、PG14664/14666はMain二sourceだけ。これらを現全29Testへ拡張したり旧失敗を消さない。既current-sourceに使える個別診断があればhash・位置・適用性を結合し再実行を避ける。現全29に一致した範囲を確認できないため当明示静的scopeを一度測る。元成功PT、Main静的六module、VM/nativeを確認再演しない。

実違反はBUG/YKTを修正前登録し、許可済みPG/必要な独立PTだけを選ぶ。runtime前提がHOLDの対象は静的根拠と未試験を区別して保留し、fixture/hook置換・拒否試行へ進まない。正式1964PT/53scope・工数null・QA051 final保留を維持する。
