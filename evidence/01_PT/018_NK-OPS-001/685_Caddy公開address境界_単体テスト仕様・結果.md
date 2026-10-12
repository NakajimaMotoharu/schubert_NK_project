# 685 NK-OPS-001 Caddy公開address境界（限定PT）

関連SS342343/SSC178/451、UI251、OPS009、WBS-P018-01（設定境界subset）。開始event0512、凍結0.1/0.25/0.75pp。既CaddyPublicCaMetadataTestのowner/mode/size/link試験は重複製造しない。対象CaddyPublicConfiguration.site(String)、class CaddyAddressBoundaryTest。

| Test ID | 入力・独立期待値 | 結果 |
|---|---|---|
| CADDY-1746-001 / caddy1746001MissingBodyAndPartialBracketRejectBeforeUri | 固定globalの後body/newline欠落、片括弧、colon一文字、非hex、IPv4mapped hex IPv6をliteral入力、全IOExceptionで閉鎖 | PASS |
| CADDY-1746-002 / caddy1746002Ipv4ZeroAndIpv6UnspecifiedHaveExactTlsLoginUri | literal0.0.0.0と[::]、独立URI https/55160/loginと一致 | PASS |

既SS342 directive fixtureを入力に利用、Expectedは独立URI/例外、Productionで生成0。解析受入でありHTTP/実bind/CA/Directory/所有/root資格ではない。新Testsource072dde49e5ad3cd8dca995617bd691a97c14e392、Main2741不変更。LAN Ubuntu26.04/x86_64/JDK25.0.4/Jupiter5.13.4/Platform1.13.4/JaCoCo0.8.15、専用class/XML/exec、元fixture/JAR/libraries hash固定。

実行command=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<fixed pyflakes> python3 -B tools/quality/pg1746_caddy_address_selected.py`、actual0/exact2/FES-aborted-notrun0/Werror0/MainCRC0、SHA55d840e9189e885b613911107cc673c004129da7a499a726281f450a8fd39d94。独立pg1747_caddy_exact_qualification.pyでunique2/XML/source/JAR/fixture/library/exec/counter資格0/SHAd28c0718dda236f3bb1507562a4d26997d148d484d8161d2a4b005312fb44cb3、再実行0/VM操作0。

残870L/169M/9C/684B（直前686Bから2B減）、四100false、fresh全3614未実行。正式1964PT/53scope/wholeleafdelta0/工数率null不変。private WorkPG379/pg1746-caddy-address-selected-v1・pg1747-caddy-exact-qualified-v1、LAN PG1746-selected-v1/PG1747-selected-qualification-v1、公開685_manifest.json。関連BUG1159/YKT927の未来生成器予防確認、Production障害発見なし。

未達：TLS例外/CA有効期限/証明書extra bytes/Directory walk同inode/owner/再照合、native/current/source/全品質/trace。P018-01をACCEPTEDとしない。
