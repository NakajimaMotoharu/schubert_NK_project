# F03 非Throwable同一性28・用途確認仕様

群F03_NON_THROWABLE_IDENTITY_CONTEXT28_V1/event2773、source2f4290e7・save45aef62bb、共有85残15・着手前1/2/4pp cap10、主担当WBS-F03。2406/2407の元56型証拠・独立postの未分類28だけを扱い、型解析/既成功PT/全回帰を再演しない。源hashが変わったsiteは確定しない。

対象はrequest同一scope5、Thread同一性9、opaque owner/baseline7、既receipt継続4、ThreadLocal scope順序1、current repository instance2。原比較site/型/周辺処理と、private constructorの捕捉・実worker生成・owner thread捕捉・同receipt返却・ThreadLocal push/pop・同repository注入をsourceで静的に追跡する。SS324の保存結果/owner一致、SS313314のcurrent repository、SS343の同producer receipt、SS351のrequest lifetimeを上位根拠とし、それより詳細な内部identity判断はPG-D771へ残す。仕様を変更しない。

判定はSTATIC_DIAGNOSTIC_CONTEXT_REVIEWED_DYNAMIC_HOLDであり、用途の必要性を記録するだけ。全実経路/例外/競合が正常、false positive確定、PT_EXECUTION_EXEMPTとはしない。coverage/PT/新規個別受入0、raw8472・既是正953不変。前参照3231へ当28のみ結合、元rawを削除しない。元28全IDと source/位置/型/担当を照合し、誤source・集合欠落・既分類混入・製品PT偽計上等をmetadata反例で拒否する。

新fixture/製品実行/新型解析/権限操作/実process/VM/DB/Root/native/intent-permit操作/鍵/保留二工具へのアクセス0。ソースのメソッド名を読むこととそのメソッドを実行することを区別する。読み取りレビューの既出根拠は再利用し、判定不能ならUNKNOWNを残す。結果は2409とPG13042公開manifest、終了時は当初/v3/v4/v5/群開始見積を不変に、共有消費と専有不明を分離して保存する。
