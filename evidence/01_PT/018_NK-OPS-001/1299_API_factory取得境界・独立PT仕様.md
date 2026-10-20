# 1299 API factory取得境界：S3a製造・独立PT仕様

NK-MSG-001/NK-OPS-001、RD MQ001003006008/SYS004・UI231253、SS321342354/SSC315/BUG1553/YKT1307/PG-D464予定。主WBS-P018-05、P005-03/F03参照追加費0、1490凍結1/4/10維持・S3a内数.25/1/3ppは非加算。設計only PR173→main8f608f9b7f03311230dbe7ec5ea3ddc2d1ac8feb、未受入code/tool/evidence混入0、添付100上限一回失敗・再送0。S2元25471/6144のMain/Test固定中は当製造を発行しない。

PT-API-FACT315001=ArtemisConnectionFactoryProviderの三profile/全12setter独立golden、一回取得・成功live返却・user/password無し。windowだけliteral1048576/0/65536、他call2000/failure10000/TTL30000/initial3/reconnect-1/retry1000/mult2/max30000/durabletrue/preACKfalse/topologyfalse。既connectorの固定loopback/port境界/null/未知値は既Testへ接続する。expectedにproduction profile.windowBytes()を呼ばない。

002=各setter1～12のIAE/ISE/NPE/Errorを各自己所有未接続factoryへ注入し、設定prefix・同一primary/close一回/正常live未返却を独立literalで検証。取得自体の例外/nullとprofile/supplier nullは未取得close0。003=primary/closeの全型組合せ・同一Throwable、closeError対非Errorprimaryだけfatal優先、別secondaryのみ一度suppressed、provider raw text外部公開0。有限fixtureはfinallyで自分のlocatorをsuper.closeし、connection/sessionを開かない。

004=ApiBrokerContexts親の取得前owner/lock/password supplier・三容量・成功phaseをactual JVM順序で確認。三providerの全正常/各位置null/Runtime/Error、正常返却済みだけ逆順close・元primary同一性/個別secondary・未取得close0/password copy0、注入borrowed constructorの既責務・live close S2再確認を維持する。最後の取得後はfinal field格納だけで追加owner/List/phase allocationをしない。

着手前判定 **PT_DEFAULT**：通常JDK/Maven・自己所有未接続Artemis locator/proxyと固定goldenのみ、実VM/current/Root/Unit/DB/鍵/原本Backup/failed-cohort/intent/permit操作0、拒否境界probe0。三profile/入力loopをJUnit件数へ水増ししない。全関連既API/必要Web・guard、六format型nullSpotBugs/原XML/全Main・全六Jar/物理差/無除外静的/当実四counter100を確認し、不足は補完しない。

command/対象commit/run/OS/JDK/tool/日時/終了code/実入力・期待・実際/coverage/BUG/manifest path/hashは新only元runと結果へ保存する。raw log/秘密はGitへ出さない。S3bのnative返却前UNKNOWN保持・ApiProcessMain外側資源との接続は別未完。関連変更をまとめた必要fresh全体/全理由/trace/native/CHR/451を要求し、旧sourceのPT/native/coverageを新sourceへ合算しない。正式1964-53/17-190/工数null/QA051final/PTALT未特定代替0を維持する。
