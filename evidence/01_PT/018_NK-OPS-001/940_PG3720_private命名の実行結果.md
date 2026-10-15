# private190候補・実静的・Main反映結果

NK-OPS-001/F03、仕様939、PT-3714-001～003、BUG1317～1319/YKT1083～1085、SS311/354/451。base5224→Main4c9b2de2dcc22f80a64cd1a1151ec691352c0cdb、dev-foundation。Linux aru/JDK25.0.4、固定GJF1.36.1 skip-reflow/PMD7.28.0/Checkstyle14.3.0。

独立純6 PASS：field/method/constructor shadow・nested/lambda/array/null、未知位置/public/record/Serializable拒否、no-op/値・引数・method変異、canonical ancestor alias、継承member衝突、wildcard bounds/別captureと再参照golden。consumer純1も成功。Production PT件数へ加算しない。

元PG3714はprotocol最終proofでactual1。PG3716/18の読取診断で原本/候補全byte不変、byte不変TypedFieldValuesの6bindingだけjavac内部capture番号差、実field set一致。BUG1319を修正前3751de417起票、f97193afdで公開TypeMirror構造・型境界/capture identityを保持して是正。元失敗・診断/初期witness表記TDD失敗を保存し、旧成功三提案は再演しない。

PG3720（23:03:42～23:04:19Z）元三成功提案を参照、残三提案→固定format→全六の別最終verify actual0。849 source、90変更file、190 private symbolだけ、63serialized非変更。全resolved symbol/AST/literal/公開ABI・new field存在/old不在・原本/型classpath不変。manifest15061644c19d9215537527c96a294f1e2028ccbbe839edc9b029b11fd6726116。

PG3722の元job actual0、固定PMDの実exit4/処理error0/raw2027（2217から187 method-name＋3 type-nameだけ減、他21rule不変）、Checkstyle actual0/指摘0。PMDreportb031ab624e072d8441c0bbfb983aae752593a78351af233acbdc3deae3134090、Checkstyle297c3fe4144b46bad7ac0af6becdddfd2d98da1fb96c677023ea543747d8c2e2、manifest40d819b234d4d081fe214c877f9d8d534c9dce3d1372a28b69a0ec2c3c8b6bfa。全規則・tool/aux固定、抑制0。

PG3724 stage/apply actual0、all849/old-new90 SHA・全70生成物不変更・正規tar/path/差分・durable intent/dirsync、4c9b2de2dでMain反映。public PG3728-private-field-hygiene-v1/manifest.json SHA aa99c242ab86ef919be412d02ad0f7f1a497635663920bdc8bfb41cbad173441 に190 mapping/849source/90差分/六proof/全raw集計を接続。秘密/DB値/実session等を含めないsource-only証跡。

新Main全体（期待3714/545/1643）/当native/coverage/CHRは未実行、実配備4856/PG3420不変更、F03未受入、正式1964/53・17/190・工数null・QA051final不変更。旧4856 native/coverageは新4c9へ加算0、BUG1317の最終閉鎖は後続品質依存待ち。
