# NK-WEB-002 共有session依存単体テスト仕様書

PG230。対象`WebApplication.startWithSessionDependencies/startWithValidatedDependencies`、RD AUT-002・SYS-001/006、UI225/226/232、SS311/313/314/321/342/352。API0102を受ける`ApiSessionInvalidHandler`は`SessionRepositoryFilter`のrepositoryと参照同一性を検査するため、Log MVCへ渡すhandlerをWeb security chainと同じ`SpringEncryptedSessionRepository`から作る。受入範囲はWeb側の共有dependency登録までで、実NK CHR-L01ではない。

| Test ID | JUnit method | 入力・操作 | 独立期待・根拠 |
|---|---|---|---|
| PT-SCR-124 | `WebApplicationTest#scr124SessionFactoryWiresLogMvcUsingSecurityRepository` | 隔離PostgreSQL/Flyway・Artemis、Log MVC config、session factory、GET `/login` | SS314/352の同一repository契約。factory呼出1、Log MVC Controllerの依存解決成功、Login200/タイトル`schubert NK - ログイン`、発行cookieのsessionがfactoryへ渡したrepositoryで取得できる。期待タイトルはQA-045承認DIF-001から固定文字列として記載 |
| PT-SCR-125 | `WebApplicationTest#scr125NullSessionFactoryStopsBeforeBorrowingResources` | factory null、DB/JMS禁止proxy | 起動前NPE、DB/JMS borrow0。JDK null契約とSS342の起動順 |
| PT-SCR-126 | `WebApplicationTest#scr126InvalidSessionDependenciesStopBeforeHttpBind` | factoryがnull map/型不一致mapを返す。portを別socketで予約 | NPE/IAE、factory呼出規定値、HTTP bindせず、既存予約socketが維持される。SS342の閉じた起動条件 |

選択commandはJava25 Maven `-pl src/schubert-nk-web -Dtest=WebApplicationTest test jacoco:report`。正式commandは`sh tools/quality/030_run_pgpt_verify.sh PT-WEB-20260924-20`、対象commit`883b33f1`。正常/異常/null/依存起動順を対象とし、並行/再送はこの構成methodでは非該当（既存JMS consumer/worker PTで検証）。`WebApplication` instruction/line/method/class100%、分岐は存在すれば100%、全reactor・静的0、failed/flaky/skipped/not-run0、同一source/runの全scope/hashを認定条件とする。実行日時、OS/JDK/tool、branch/commit、command、終了code、input/expected/actual、coverage、関連BUG/SSC、証跡path/hashは正式runの`evidence/manifest.json`と036を正とする。秘密値・raw session IDは保存しない。
