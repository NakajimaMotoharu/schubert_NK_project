# NK-OPS-001 Web接続設定単体テスト仕様書（PG286/BUG261/YKT195）

対象`WebNonSecretConfig.parse/validate/value/canonicalSha256`とweb.yml.template。RD SYS002/004/DAT001/MQ001、UI212/243/253、SS343 §4/5.2、471 D01/02/03。旧018/063～064の15key部分認定は履歴のまま、新対象20keyへ補完する。Current baseline/外部wireは不変更。

`PT-OPS-WEB-CFG-007`のfixtureはSS literal URLで、DB `jdbc:postgresql://127.0.0.1:<port>/<lowercase identifier>`、MQ `tcp://127.0.0.1:<port>`。port1/65535、DB長63を受理し、0/65536/先頭0/非literal/uppercase/64文字/userinfo/query/fragmentを拒否する。pool max2/min1・connect3sは固定、API pool/任意role/common層接続設定は拒否。例外messageは固定非秘密値。実接続・接続credentialは本parser試験対象外。

既存CFG001～006を回帰し、expectedはSS343の20行をtest内GOLDENへliteral列挙した独立文字列・JDK標準SHA-256から算出する。Production.value/hashでexpectedを作らない。templateも同じ20key固定値へ明示一致検査する。API-CFG001～006では同様のURL・固定8/min2/connect3sが既に存在し、commonのprotocol/zone/mode限定は維持する。LOAD/INPUTとMAINはsource階層と順序を回帰する。

REDはBUG261起票後にCFG007だけを実行しunknown拒否でexit1。修正後はWeb CFG/LOAD/INPUT/MAIN全suiteとAPI相当suiteを限定再試験する。command/結果/source/hash/coverage/未実行範囲は088。全体正式gate前はBUG/YKTを完了認定しない。
