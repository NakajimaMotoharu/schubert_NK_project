"""Seven unchanged storage attribute tests, confined to a new owned synthetic fixture parent."""
import os
import re
import stat
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import g07_host_class_provenance_inputs as data
import scoped_prometheus_host as run

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/storage/StorageAttributeGuard'
MAIN_UNITS={NAME:dict(module='storage',name=NAME,sha256='d4752c82283b4ab0fc11b5ba738b32b5ce43045bab4576bc210fe4c4d50c635b')}
CLOSURES={NAME:[NAME]}
METADATA=set()
UNEXECUTED=set()
ROOT=data.ROOT/'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage'
TESTS={'StorageAttributeGuardTest':ROOT/'StorageAttributeGuardTest.java'}
COUNTS={'StorageAttributeGuardTest':7}
FIXTURES={}
SESSION='PG16274-STORAGE-ATTRIBUTE-SEVEN'
METHODS=('med020LargeAssetSizesKeepTransferLimitAndUnixGuards',
         'u01SizeAccountingIncludesEmptyPartialPartsButReadyRequiresWholeRecords',
         'u02AccountingRejectsUnknownSizeBoundsAndInvalidOwnershipOrLinkAttributes',
         'a01NullInvalidAndBoundaryOsIdentityNamesAreExplicit',
         'a02DirectoryTypePermissionsOwnershipAndMissingAttributesFailClosed',
         'a02FileRequiresOneLinkExactBytesAnd0640WithoutSpecialBits',
         'a03ActualFileSymlinkHardLinkWrongPermissionAndOwnerRemainUntouched')
TYPE='dev.codex.schubert.nk.storage.StorageAttributeGuardTest'
HELPER=data.ROOT/'tools/quality/architecture/StorageAttributeFixtureJunitLauncher.java'

def source_path(row):
    return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'

def parent_state(parent):
    st=parent.lstat()
    assert stat.S_ISDIR(st.st_mode) and not parent.is_symlink() and st.st_uid==os.getuid()
    assert stat.S_IMODE(st.st_mode)==0o700 and not list(parent.iterdir())
    return dict(device=st.st_dev,inode=st.st_ino,ownerIsCurrentUid=True,mode='0700',empty=True,symlink=False)

def owned_step(name,command):
    if name!='selected-junit':return environmental_step(name,command)
    parent=run.SLOT/'owned-tmp';catalog=run.SLOT/'selected-methods.safe.tsv'
    assert not parent.exists() and not parent.is_symlink() and not catalog.exists()
    assert command[-2:]==[HELPER.stem,str(run.SLOT/'xml')]
    parent.mkdir(mode=0o700);before=parent_state(parent)
    with catalog.open('x') as stream:
        for method in METHODS:stream.write(TYPE+'\t'+method+'\n')
    catalog_hash=run.host.sha(catalog)
    actual=[command[0],'-Duser.language=ja','-Duser.country=JP',*command[1:],str(catalog),'ja-JP',str(parent)]
    result=environmental_step(name,actual)
    if result['actualExit']==0:
        after=parent_state(parent);assert before==after and run.host.sha(catalog)==catalog_hash
        receipt=run.SLOT/'xml/temp-ownership.safe.tsv';rows=[line.split('\t') for line in receipt.read_text().splitlines()]
        assert len(rows)==7 and len({r[0] for r in rows})==7
        assert all(len(r)==2 and re.fullmatch(r'case-[0-9]+',r[0]) and r[1]=='CREATED_AND_REMOVED' for r in rows)
        value=dict(before=before,after=after,sevenUniqueChildrenRemoved=True,
                   catalogPath=str(catalog),catalogSha256=catalog_hash,receiptPath=str(receipt),receiptSha256=run.host.sha(receipt),
                   actualSyntheticFileAndLinkOperations=True,actualChildPermissionChanges=True,
                   existingFilesModified=False,actualNkLowLevelNativeInvoked=False)
        result['ownedTemporaryParentLifecycle']=value
        run.host.write(run.SLOT/'owned-temp-lifecycle.safe.json',value)
    return result

if __name__=='__main__':
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg16274-storage-attribute-seven-pt-v1';run.OUT=data.BASE/'PG16274-storage-attribute-seven-pt-v1'
    run.HELPER=HELPER;run.NEW_TEST=TESTS['StorageAttributeGuardTest'];run.TEST_ROOT=ROOT
    run.TEST_SOURCE_OVERRIDES={};run.FIXTURES,run.COUNTS=FIXTURES,COUNTS
    run.EXTRA_TEST_SOURCES=();run.SESSION_ID=SESSION
    assert run.host.sha(HELPER)=='9ca2a53b0b475031b50b8872029a717a94249b4cfff166b1c5c0d004d66169b8'
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA)
    previous=data.read_checked(data.BASE/'PG16238-current2157-public-proof-registry-v1/manifest.json','deb61775f9c16b20528879ed54854353ea1edb23cdff5cc99cc00a022b8ac031')
    assert normal['source']==previous['source']==SOURCE and NAME not in previous['fullSourceUnits']
    assert TYPE not in previous['suiteNames']
    path=run.NEW_TEST;relative=str(path.relative_to(data.ROOT));text=path.read_text()
    assert run.host.sha(path)==normal['begin']['inputHashes'][relative]==run.host.sha(COMPILE/'snapshot'/relative)=='1c0dd9629f7225661dd682f967ec0ae35fd1c93928144ed9349849d6ea1676c3'
    assert text.count('@Test')==7 and set(re.findall(r'@Test\s+void\s+(\w+)\s*\(',text))==set(METHODS)
    assert not any(v in text for v in ['@Before','ProcessBuilder','DriverManager','HttpClient','RootStartupContext','KeyStore','java.sql','Linux','ChildStartupContext','TemporaryInfrastructureException','WebStartupException','FingerprintKeyRing','ResponseSnapshotCodec'])
    for name,pin in [('StorageAttributeGuard',MAIN_UNITS[NAME]['sha256']),('StorageIdentity','e19734a40b13885ac0d62b3abb117a788d9a7e0839d002d5f655d162cce3cd74'),('StorageIoException','2a1233e46a8f05a0dbf7e42034ad3e34afecf14814ebf5111527db6b6e179284')]:
        relative='src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/'+name+'.java'
        assert normal['begin']['inputHashes'][relative]==run.host.sha(data.ROOT/relative)==run.host.sha(COMPILE/'snapshot'/relative)==pin
    with zipfile.ZipFile(normal['jars']['storage']['path']) as jar:
        assert {n[:-6] for n in jar.namelist() if n==NAME+'.class' or n.startswith(NAME+'$') and n.endswith('.class')}==set(CLOSURES[NAME])
    run.step=owned_step;run.main()
