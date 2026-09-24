# NK-OPS-001 API起動入力結線実行結果

PG279/PT-OPS-API-INPUT-001～004、branch`dev-foundation`、JDK25.0.4/Maven wrapper/Linux。選択4PTはfailure/error/skipped0。初回reactor選択commandは依存Protocolに対象testがなくexit1、次のskipTests installはJacoco checkが残りexit1、いずれも不認定。`-DskipTests -Djacoco.skip=true install`で依存artifact再生成後、対象4件PASS。対象class/Valuesの選択Jacocoはinstruction/line/method/class missed0。正式全reactor・53scope/hash/固定source commit前なので本段階を正式合格へ算入しない。秘密値を保存しない。
