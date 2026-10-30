"""Independent four separate Source/exec exception profiles; no cross-exec counter union."""
import reviewed_whole_pure_source_post_v2 as core
import pg14726_web_four_exception_values_v2 as original
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

RAW_PIN='775f3829a8e4596d67a9f65a5767e9e733fbc5262ad10e870a6b4ca078b7c7ab'
OUT=data.BASE/'PG14728-web-four-exception-posts-v2'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    group=data.read_checked(original.OUT/'manifest.json',RAW_PIN);verify(group['invocation'])
    assert group['actualExit']==0 and group['packagePositiveChecks']==4 and group['packageNegativeChecks']==5 and group['originalMethods']==group['originalSuites']==group['originalProductJvms']==4
    records={}
    for package,(_,_,name,pin,owner) in original.ROWS.items():
        info=original.original(package);raw_folder,post_folder=original.folders(package);record=group['originalRuns'][package]
        assert record['folder']==raw_folder and record['tests']==1 and record['source']==info.SOURCE
        raw=data.read_checked(data.BASE/raw_folder/'manifest.json',record['sha256']);assert raw['cases'][0]['classname']=='dev.codex.schubert.nk.web.'+package+'.ExceptionValueContractTest'
        internal='dev/codex/schubert/nk/web/'+package+'/'+name
        profile=dict(rawFolder=raw_folder,rawSha256=record['sha256'],postFolder=post_folder,kind='REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES',originalTestsAlreadyCounted=False,sources={internal:dict(path='src/schubert-nk-web/src/main/java/'+internal+'.java',sha256=pin,module='web',closure=[internal,internal+'$Reason'],owner=owner)})
        core.verify_profile(info,profile)
        path=data.BASE/post_folder/'manifest.json';post=data.read_checked(path,data.sha(path.read_bytes()))
        assert post['actualExit']==0 and post['tests']==post['suites']==1 and post['crcMismatch']==0 and post['metadataNegativeVectors']==8
        records[package]=dict(folder=post_folder,sha256=data.sha(path.read_bytes()),tests=1,suites=1,fullSourceUnits=post['fullSourceUnits'],owners=post['owners'])
    assert len({v['folder'] for v in records.values()})==4
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalGroupSha256=RAW_PIN,independentPosts=records,originalMethods=4,originalSuites=4,originalProductJvms=4,productTestsReexecutedByPost=0,coverageExecUnion=False,oldSourceTransferred=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
