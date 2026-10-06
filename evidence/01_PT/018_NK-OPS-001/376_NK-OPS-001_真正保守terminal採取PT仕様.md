# 真正保守terminal採取PT仕様（SSC196/PG477）

Program NK-OPS-001/NK-ADM-001、SYS002004/OPS009/TST004/AUT001002/DAT009/UI212225226242251/SS342343/451。API-Web既四profile不変更。Production default agent無しの追加I/O0、業務・skip・権限・receipt・deadline不変更。

PT-OPS-NC196001: TerminalNativeCoverageProfileTestの二role/session/Unit/namespace/phaseをliteral vectorで照合。startup service/forwardingを拒否、default及び無関係agentは採取0。

PT-OPS-NC196002: null/missing/zero/大文字/長さ/末尾LF/異role/Root/追加option/異path/duplicate/null要素は非成功、初期化の固定IOExceptionを照合する。expectedは固定agent option文字列、productionから生成0。

PT-OPS-NC196003: NSS fixtureは独立passwd/group golden。Inspector991:976/[976,982,986]、Bootstrap999:981/[980,981,982,986]を照合し、API-Web旧四cgroup/role対応を全組確認する。

PT-OPS-NC196004: literal公開JaCoCo header、固定version/session、clone不変、terminal新一回・before-exec拒否/agentread0・再試行拒否。人工agentはcomponentのみ、native受入に使わない。

実入口はInspectorLauncherのwrite帰還後とBootstrapAdminMainの全owned run帰還/finished後。公開agent取得/heldfile/失敗/nullable契約は既NC193/NCHECK193/NEXPORT193、実入口のdefault外部JVM/新profile真正Unit、source/run/hash/static/coverageは後続結果377へ追跡。初稿RED/compile失敗・未実行を合格に加算0。JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/PG18、privateExec/秘密/DBraw値Git禁止。同群選択→必要fresh全6/frozen→signed同source→既原本/旧Backup/全DB独立保護の正規新run Inspector＋非空DB/別合成credentialBootstrap20→同INV/kernel/全scope正常帰還/退役/新single NoMatch0の順。global100/正式/ITSTは実証まで未受入。
