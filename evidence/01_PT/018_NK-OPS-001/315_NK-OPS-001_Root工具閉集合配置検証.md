# 315 NK-OPS-001 Root工具閉集合配置検証

2026-10-03、BUG537/YKT381、SS343 privileged staging、451。これは隔離VM trusted operator工具の検証でありProduction PT件数・native coverage・工程完了に加算しない。Production Sourceは91b010509e715e2b097c955d04f21c23f3529966のPG430全6run中から変更していない。

ROOTTOOL001：実stat/find/nameiで旧`/home/ubuntu/pg428-boot-tools-v5`の19classが400 ubuntu所有、子dir500Root/祖先ubuntu所有と確認。入力のclassごとにSHA-256を取得し、保存host buildの同名classが同じdigestであることを独立hashで確認、unknown byteなら一件でも拒否する。工具自体のProduction methodで期待値を生成しない。

ROOTTOOL002：既存Root700保全領域の固定new-only `pg430-deploy-tools`へ19classをコピーし、全19file400Root0:0、dir500Root0:0、全祖先Root非一般書込を確認。既存工具を編集/削除せず保持。19個のbasename→SHA map前後一致を検査し、symlink/別型/未知fileを拒否する。利用者ubuntuからclass readと保全親writeが両方拒否されたことを確認。Root工具の実行はこの固定閉集合からのみ行う。

実測：旧/新map19/19一致、metadata19file+1dir一致、一般user read/parent write拒否。current/approval/intent/DB/原本/Backup mutation0。既存VM boot58006280、全Unit PID/job空を照会済み。全BOM署名候補・配備・通常Morningの受入証拠とは別であり、Root helper終了0だけを業務成功としない。

非Git private証跡（Work PG379）：`pg430-root-tools-metadata-before.log`、`pg430-root-tools-sha-before.log`、`pg430-root-tools-after.log`。内容は固定tool byte/hash/metadataだけでcredential/署名秘密key/session等を取得していない。次の集約manifestに実hash/command/source・nativeverifyを記録する。新observerはcanonical host sourceをSSH stdinからRoot Pythonへ渡し、一般user書込可能なancestorの工具pathからRootコードをloadしない。
