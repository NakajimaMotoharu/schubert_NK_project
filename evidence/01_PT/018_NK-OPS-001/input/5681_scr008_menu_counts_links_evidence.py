from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess

ROOT = Path('evidence/01_PT')
PMO = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
OUTPUT = ROOT / '018_NK-OPS-001/evidence/PG41446-scr008-menu-counts-links-v1'

def read(path):
    return json.loads(path.read_bytes())

def pin(path):
    return {'path':str(path),'sha256':sha256(path.read_bytes()).hexdigest()}

def find(run):
    return next(ROOT.glob(f'*/evidence/{run}-*/manifest.json'))

def source(ref,path):
    return subprocess.check_output(['git','show',f'{ref}:{path}'],timeout=10)

task = read(next(PMO.glob('1825_*')))['values']
old_model, old_dom = (find(run) for run in ('PG24476','PG24452'))
model, dom = map(read,(old_model,old_dom))
assert (model['actualExit'],dom['actualExit'],model['tests'],dom['tests']) == (0,0,16,43)
assert all(row[key]==0 for row in (model,dom) for key in ('failures','errors','skipped','aborted'))
model_original = old_model.parent/'original-manifest.json'
compile_record = old_model.parent/'compile-manifest.json'
assert model['files'][model_original.name]==pin(model_original)['sha256']
assert model['files'][compile_record.name]==pin(compile_record)['sha256']
orig = read(model_original)
compiler = read(compile_record)
base='src/schubert-nk-web/src/'
ns = 'dev/codex/schubert/nk/'
in_view='main/java/'+ns+'web/view/'
in_test='test/java/'+ns+'web/view/'
target_paths = (
    base+in_view+'AnimationMenuViewModel.java',
    base+in_test+'AnimationViewModelTest.java',
)
identity = {}
for path in target_paths:
    identity[path]=sha256(source(task['source'],path)).hexdigest()
    assert identity[path]==compiler['inputHashes'][path]
dom_fixture=base+in_test+'AnimationBrowseTemplateResourcePortTest.java'
identity[dom_fixture]=sha256(source(task['source'],dom_fixture)).hexdigest()
assert identity[dom_fixture]==dom['inputHashes'][dom_fixture]
for resource in ('templates/animation.html','templates/fragments/layout.html'):
    path=base+'main/resources/'+resource
    identity[path]=sha256(source(task['source'],path)).hexdigest()
    assert identity[path]==dom['resourceHashes'][resource]
for name in ('web/session/SessionPrincipal','web/view/TopBarViewModel'):
    path=base+'main/java/'+ns+name+'.java'
    content=source(task['source'],path)
    assert content==source(model['source'],path)
    identity[path]=sha256(content).hexdigest()
java = 'src/schubert-nk-protocol/src/main/java/'+ns+'protocol/'
protocol_delta = {}
for suffix in ('layout/media/AnimationMenuResponseData.java','layout/TypedFieldValues.java','layout/PayloadData.java',
               'header/AuthenticationContext.java','layout/semantic/UserRole.java'):
    path=java+suffix
    content=source(task['productionCoreMain'],path)
    previous=source(model['productionCoreMain'],path)
    if content != previous:
        assert suffix == 'layout/TypedFieldValues.java', path
        begin = b'  public static void requireUnsignedRange('
        end = b'\n  public static '
        old_method = previous.split(begin,1)[1].split(end,1)[0]
        new_method = content.split(begin,1)[1].split(end,1)[0]
        assert old_method==new_method
        protocol_delta[path]={'previousSha256':sha256(previous).hexdigest(), 'currentSha256':sha256(content).hexdigest(),
            'unchangedUnsignedRangeMethodSha256':sha256(begin+new_method).hexdigest()}
    identity[path]=sha256(content).hexdigest()

assert any(row['name']=='web230AnimationMenuCounts()' and row['classname'].endswith('.AnimationViewModelTest')
           for row in orig['cases'])
dom_cases=('menuKeepsThreeApprovedCardsCountsAndRoleDisplay','zeroCountDisplayDoesNotInventNumericCatalogCounts')
assert set(dom_cases)<={row['name'] for row in dom['testCases'] if row['classname'].endswith('.AnimationBrowseTemplateResourcePortTest')}
counts=model['individualSourceCounters']['AnimationMenuViewModel.java']
assert all(counts[key]['missed']==0 for key in ('LINE','METHOD','CLASS','BRANCH'))
docs=subprocess.check_output(['git','ls-tree','-r','--name-only','-z',task['canonicalDesignSource'],'--','documents']).decode().split('\0')
ui=next(p for p in docs if p.startswith('documents/200_UI/') and Path(p).name.startswith('235_'))
ss=next(p for p in docs if p.startswith('documents/300_SS/') and Path(p).name.startswith('313_'))
ui_body=source(task['canonicalDesignSource'],ui)
assert all(x.encode() in ui_body for x in ('ANMRSP01','Main/SUBTRACK件数','Opening有無','総file件数'))
current_run_path=find('PG41304')
current_run=read(current_run_path)
assert current_run['actualExit']==0 and current_run['fullProtocol'] is True
assert subprocess.check_output(['git','diff','--name-only',current_run['core'],task['productionCoreMain'],'--',
                                'src/schubert-nk-protocol','pom.xml'],timeout=10)==b''
current_raw=current_run_path.parent/'unfiltered.tsv'
assert pin(current_raw)['sha256']==next(x['sha256'] for x in current_run['evidence'] if x['path'].endswith('/unfiltered.tsv'))
direct_raw={}
for line in current_raw.read_text().splitlines():
    columns=line.split('\t')
    if len(columns)<7 or columns[0]!='CLASS' or columns[1] not in (
        ns+'protocol/layout/media/AnimationMenuResponseData',ns+'protocol/layout/TypedFieldValues'):
        continue
    assert columns[3]=='true'
    counters={bits[0]:[int(bits[1]),int(bits[2])] for column in columns[6:] for bits in (column.split(':'),)}
    assert all(c[0]==0 for c in counters.values())
    direct_raw[columns[1]]=counters
assert len(direct_raw)==2 and len(protocol_delta)==1
OUTPUT.mkdir()
record=dict(actualExit=0,run=OUTPUT.name,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    core=task['productionCoreMain'],originalModelSource=model['source'],originalDomSource=dom['source'],inputHashes=identity,
    design={p:sha256(source(task['canonicalDesignSource'],p)).hexdigest() for p in (ui,ss)},
    priorCases={'web230AnimationMenuCounts()':'999 boundary, 0, mismatched total, optional opening and role display',
        dom_cases[0]:'fixed three links and counts',dom_cases[1]:'zero display policy'},
    originalModelRaw=counts,artifacts=[pin(p) for p in (old_model,old_dom,model_original,compile_record,current_run_path,current_raw)],
    delta=protocol_delta,currentDirectProtocolRaw=direct_raw,localFooting='Old Web projection and DOM evidence with exact inputs. Current separate Protocol carrier/helper evidence. No merged coverage or current Web run.',
    firstReadExit=1,firstReadReason='TypedFieldValues became instance-owner-backed. The next read isolates the current proven carrier and exact unchanged called method.',
    actualHttp=False,actualBrowser=False,whole451=False,formalDelta=0,replayedTests=0,
    originalConditionalPriceActivated=False,script=pin(Path(__file__).resolve().relative_to(Path.cwd())))
with (OUTPUT/'manifest.json').open('x',encoding='utf-8') as file:
    json.dump(record,file,ensure_ascii=False,indent=2)
    file.write('\n')
print(len(identity),len(record['priorCases']),counts['BRANCH'])
