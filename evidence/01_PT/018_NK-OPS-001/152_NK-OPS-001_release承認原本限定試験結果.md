# PG313 release承認原本限定試験結果

関連018150/SS34311.1/SSC096、ReleaseApproval.approval001～008/RootReleaseApprovalReader.approvalRead001～008。codeとtestを同時実装し、Productionで期待値生成せずliteral NKRELEASEAPPROVAL1/version/64lowerhex/LFを使用。root原本は固定 `/etc/schubert-nk/release-approval/current` のみ、公開claims model自体は承認能力でない。RootStartupContext再照合→真正PID1 host-view→root/group属性・ACL・同device/保持inode→固定原本同byte→callback全BOM作業中保持→inode/名前/全ancestor再照合→全close→context再照合後だけ値を返す。readerはsignature検証/approval発行の代用品でない。

初回03:38:00 exit1、ResourceScope8/Approval8成功、Reader8のEOF fault1未到達。BUG289/YKT222を修正前起票、既存65537byte reader専用の残1byte条件を193byte bufferへ流用したtest誤り。実EOF一点でposition変化＋注入回数1をassertする別modeだけ追加、Productionと拒否期待は不変更。旧RED XML2/coverage1/rawloghashはprovisional/PG313-approval-REDに保存。初回dirty test source全hashは退避前に未採取なので後のhashを流用・正式認定しない。

再試験03:40:02、選択92件/static0、provisional/PG313-approval-GREEN/manifest.json。directory-device negative追加と共通fixture全利用再試験03:43:06 exit0、選択100件/F-E-S0/static0、10JUnit/3coverage/3static/sourcehash/command/OS/JDK/Maven/loghashはprovisional/PG313-approval-GREEN-3/manifest.json。

Coverage: Approval全6counter missed0（line21/method7/class1/branch10）、Reader host全60branch0＋NativeIo3line/3method0、真正root factory7line/1method未実行。非root hostの固定factory拒否をactual root Unit positiveに読み替えない。限定commandはcleanではなく旧同Production byte coverageを残すため、全module coverage/正式run合格には用いない。署名発行・全BOM・schema期待・専用DB begin・R2業務process・R3実NK CHRは未結線、fullgate false。鍵/署名具体化の一次根拠は[JDK25標準algorithm](https://docs.oracle.com/en/java/javase/25/docs/specs/security/standard-names.html)、公開vectorは[RFC8032§7.1](https://www.rfc-editor.org/rfc/rfc8032.html#section-7.1)。秘密鍵は作成/保存していない。
