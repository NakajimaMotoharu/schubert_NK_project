# Morning実factoryの所有移管

WBS-P017-06、RD BAK001/OPS009/UI251/SS333/341/343/354/SSC308・BUG1414/YKT1178、1061群の追加発見。開始.4/1.2/3共有pp固定、実費/N-T/null、child/親費重複0。

openNativeはDirectory取得前にcalls/path/securityとfactory/assembly/release port、transfer状態を構築する。Directory取得はfactoryの最終呼出しで直返却。BackupWorkerRequestFiles（lock/policy）/匿名Ownerの構築はResourceScope保護action内だけで行う。assembly正常nonnullの最後にtransferを一度確定しOwnerを返す。未transfer時は成功/IO/Runtime/Error/nullの失敗を既close優先順位で一度close、transfer後は元Owner.closeが所有を引き継ぎpublish全前後gate/非上書き/再送保持/割込/後条件を維持する。null portは取得前拒否、factory IOExceptionは元identityを保持、assembly IOExceptionは既UNAVAILABLEへredact、Runtime/Errorは同identity（複合close優先順位も既ResourceScope）。外部処理結果/電文/DB/原本/Backup/VMは変更しない。これは承認済み所有契約を満たす内部実装で上位仕様変更なし。

独立test追加予定4：PT-OPS-MBPUB007取得前null/openIOException/nullDirectory、008成功移管と最終close一回、009assembly IO/Runtime/Error/nullOwnerとclose、010assembly×closeのIO/Runtime/Error全組合せ。期待はliteral sequence/count/identity/UNAVAILABLE/同優先順位の固定表で、productionから計算しない。通常temp私有filefixtureだけ使用し実原本/鍵/Backup内容なし。既MBPUB001..006/1425001と全関連684を同sourceで再試験、予定688/85（変更後実inventoryで確定）を旧source結果へ加算しない。

全764Main/六format/三static/全storage四miss0・取得前portとrawDirectory直返却/transfer確定後新確保call無しの実bytecodeを要求。対象native-only未実行methodや他class未網羅は未完と明記する。新signature/配備/VMはBUG1414/YKT1178全体と必要全回帰/同source資格の後だけ。実結果1064とpublicmanifestへsource/command/tool/日時/exit/XML/coverage/hash/BUGを保存。工数null/正式1964/53/QA051final/F03/全四100/CHR/451は不変、小区切りでは停止しない。
