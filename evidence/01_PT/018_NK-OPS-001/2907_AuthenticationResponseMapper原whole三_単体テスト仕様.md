# 2907 AuthenticationResponseMapper原whole三・単体テスト仕様

NK-AUT-001/WBS-P007-04、FUN001/MQ021・UI222234§3.2/4.2・SS312322323314・PT-AUT-WIRE001～003/BUG023SSC012。source6b53/normal14216、Main50338664/Testd4247292全body、Actor/Role/Identity/Issued/Revoked/LoginResultの全constructor/initializerを確認。codec依存は既現Protocol158の純固定catalog契約を参照し、必要static起点とJava埋込field/layout literalのparse・DTO/record fieldsを確認。外部設定/resource/DB/JMS/認証service/暗号/hashへ接続しない。

原001は架空user7/UUID0,1/既公開合成a64とRole二つ。UI234の1-based開始/長さから独立432byte全spaceを作り、0-based0 username、64 role、69合成context、133/150 JSTの17桁日時、167の六retry/173の三attempt数字を設定。UTF8文字列を独立System.arraycopyするgoldenでProduction codecからexpected生成0。002は認証失敗/lock retry1,900/一時障害でidentity全spaceと固定利用者message（offset176）・数字を全byte比較。003はlogout24byte=17桁JST＋space7、成功/冪等同時刻・millisecond境界999999/000000/000001切捨てと元Instant不変、mapper null拒否、自JVM16thread/100固定応答の独立比較。assert/task数をTest IDへ水増し0。

PT_DEFAULT、plain値＋固定長encodeだけ、実context/session/credential/鍵を利用・保存しない。公開Test内のUUIDとa64は合成goldenで実認証材料ではなく、実session値は一切収集しない。NPE catch正常化なし、再送は値変換の冪等結果観点だけで実Inbox/serviceは別。Main一Source全physicalを対象に除外/別exec union0、他DTO/Protocolを当Mapper counterで完了認定しない。

command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15384_auth_response_mapper_three_pt.py。全normal/current/snapshot/source/Jar closure/原Testをpin、新slot/fresh compile/whole3一自JVM/session、FES/実exit/XML/CRC/環境保存。shared purev2の閉profileは無fixture/全Code/API namespace/既baselineMainP00704-TestUNKNOWN、crypto=falseを正しく維持する。独立postはUI234原表/offset-length・全golden hash・original XML/Source完全counterを照合。群3300の0.5/2/5pp固定、結果2908/manifest/実commitへ。正式/工数/費用/全HOLD不変更・通常小区切り停止なし。
