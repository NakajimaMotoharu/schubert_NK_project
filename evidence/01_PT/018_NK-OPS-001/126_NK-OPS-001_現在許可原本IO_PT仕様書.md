# 現在許可原本IO（PG303・実装前）

NK-OPS-001 StartupPermitFiles、RD SYS002/004・OPS009/UI251/SS343 SSC089、D03～05。root専用/run/schubert-nk/startup0700・file0600単一link/tmpfs RWの借用保持directoryを使用する。親がM/A排他・固定Unit全終端・現在boot/真正namespaceを先に確認する責務は本IOの成功で代替しない。読者は書換え・復元・修復をしない。

PT-OPS-PERMITFILE001～008: 001 INVALID原本新epoch→独立公開permit→ISSUED/readback/実byte hash順、002 旧boot/epoch/activation/current digest・不一致/未発行/破損拒否、003 全型/owner/mode/link/size/ACL/tmpfs/RW/rootUID条件、004 全read/write/force/close/atomic rename/dir sync失敗と部分結果保持、005 inode/metadata/directory入替・symlink/同epoch再発行拒否、006 interruption/null/未知例外identity・compound close priority、007 並行呼出しの不混在/一回発行、008 nativeNio入出力/strict atomic move・constructor・root lifetime。各期待値は123の手書きgolden、独立JCA hash、実Linux file属性/原本状態から作る。同Productionmethodでexpectedを生成しない。

現在record置換だけは親排他下で保持directory内の新0600part→Java Linux provider ATOMIC_MOVEへ限定し、fallback rename/copy/delete-before-writeなし。permitはCREATE_NEW/no-replace publication。全fileforce/ownerclose・dirsync・実byte読み戻し前に成功しない。未知/失敗でpartまたは公刊結果を削除しない。元の破損currentを自動修復しない。最大8192byte、currentを再確認してpermitとのbindingを確認する。

全件not-run/合格0、実装後127へ実環境/command/対象commit/coverage/結果/hash/関連BUGを記録。実backup・fullroot/Ops/schema/issuer・外部business起動・CHR未達と区別する。
