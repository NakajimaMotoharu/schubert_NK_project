# NK-WEB-002 起動用Web暗号鍵所有 PT仕様（PG367）

Program `NK-WEB-002`、対象予定class `WebNativeCodecs.create/close`。RD AUT-001/MON-003/SYS-004、UI226/242/253、SS314 §7.2.2/324 §9/343 §6/352 §11.2、471 R1/D01/D05/D06。候補Web native入口の固定5 credentialから、sessionとWeb Logのcurrent key/versionだけを用途別codecへ移す。previous rotation・revoke codec・HTTP受入は本単位では未接続であり、readyを通知しない。

| Test ID | 観点・fixture/input | 独立期待値 |
|---|---|---|
| PT-WEB-NKEY001 | synthetic 32 byteの相異なるsession/log keyと固定`v1`、所有配列を渡す | `create`後に元の2配列は全byte `0`。session暗号化は`v1`、codec使用後も入力keyに依存しない。close後は両codecが再利用不可。SS343のborrowed copy/用途分離と既存codec仕様から算出 |
| PT-WEB-NKEY002 | null source、session copy失敗、log copy失敗、片方の不正長 | nullはNPE契約。取得/構築失敗時も取得済配列全消去、構築済session codec close。成功を返さず、秘密値を例外・logへ出さない |
| PT-WEB-NKEY003 | APIなど別service IDの資格情報、閉鎖済credential | fixed Web IDのみ選択し、`ServiceCredentialSet`の目的拒否/閉鎖拒否を伝播。暗黙fallbackはなし |
| PT-WEB-NKEY004 | borrowとcloseの2 thread競合 | 同一ownerで返るcodecは所有済か、close済拒否だけ。秘密再取得・例外補完なし |

実行: JDK25.0.4/Maven3.9.12、`./mvnw -o -q -Dmaven.repo.local=<fixed> -Dnk.pt.repository=<tree> -pl src/schubert-nk-web -Dtest=WebNativeCodecsTest,WebNativeCodecsCredentialTest test spotbugs:check jacoco:report`。PG367 source確定後、対象commit、結果、JaCoCo class四指標、JUnit hash、manifestを次番号の実行結果へ記録する。RED runは合格算入しない。NullAway/SpotBugsおよび必要依存suiteを確認する。秘密実体・raw keyは証跡に保存しない。
