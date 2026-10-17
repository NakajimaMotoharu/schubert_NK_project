"""Strict current physical candidate beside immutable historical acceptance/measurement.

BUG1390/YKT1156; G13.07. Neither Git bytes nor counters grant runtime or WBS authority.
"""
import hashlib
import json
import pathlib
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT=pathlib.Path(__file__).resolve().parents[2]
COUNTERS=('LINE','METHOD','CLASS','BRANCH')
MOVES={
 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/LinuxSystemdQuery.java':'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/SystemManagerObservation.java',
 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/LinuxSystemdSession.java':'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/LinuxSystemdSession.java'}


def require(value,message):
    if not value:raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def canonical(path):
    require(type(path)is str and bool(path)and not path.startswith('/')and '\\'not in path
            and all(p not in ('','.','..')for p in path.split('/')),'canonical trace path')
    return path


def git_files(source):
    require(type(source)is str and re.fullmatch('[0-9a-f]{40}',source),'immutable trace source')
    return subprocess.check_output(['git','ls-tree','-rz','--name-only',source,'--','src','program/characterization'],cwd=ROOT).decode().split('\0')[:-1]


def eligible(paths):
    return {p for p in paths if ('/src/main/java/'in p and p.endswith('.java'))or '/src/main/resources/'in p or p.startswith('src/deployment/')}


def git_artifacts(source,paths):
    require(type(source)is str and re.fullmatch('[0-9a-f]{40}',source),'immutable artifact source')
    require(len(set(paths))==len(paths),'duplicate Git artifact request')
    request=''.join(source+':'+canonical(p)+'\n'for p in paths).encode()
    data=subprocess.check_output(['git','cat-file','--batch'],input=request,cwd=ROOT);position=0;result={}
    for path in paths:
        end=data.index(b'\n',position);header=data[position:end].decode().split();position=end+1
        require(len(header)==3 and header[1]=='blob'and header[2].isdigit(),'Git artifact missing/non-blob: '+path)
        size=int(header[2]);blob=data[position:position+size];position+=size
        require(len(blob)==size and data[position:position+1]==b'\n','complete Git artifact bytes')
        position+=1;result[path]=blob
    require(position==len(data),'no trailing Git artifact bytes')
    return result


def descriptor_digest(artifacts):return sha(json.dumps(artifacts,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())


def current_measurement(candidate,historical_source):
    proof=candidate['measurement'];path=ROOT/canonical(proof['path'])
    require(path.is_file()and sha(path.read_bytes())==proof['sha256'],'current candidate measurement hash')
    value=json.loads(path.read_bytes())
    require(type(value['actualExit'])is int and value['actualExit']==0 and value['FES']==0
            and value['productionSource']==candidate['source']and value['oldSourceNativeImported']is False
            and value['acceptedLeafDelta']==0 and value['formalAccepted']is False and value['effortPercent']is None
            and value['F03Accepted']is False,'candidate technical measurement, not acceptance')
    require(value['canonicalAcceptance']['source']==historical_source
            and value['canonicalAcceptance']['automaticSourceRebinding']is False,'historical acceptance preserved')
    modules={};remaining={k:0 for k in COUNTERS}
    root=ROOT/canonical(value['coverageRoot'])
    for module in value['modules']:
        name=module['module'];require(name in {'api','batch','bootstrap','protocol','storage','web'}and name not in modules,'all-six candidate modules')
        xml=root/name/'site/jacoco/jacoco.xml';raw=xml.read_bytes()
        require(sha(raw)==module['coverageXmlSha256'],'current candidate XML hash')
        tree=ET.fromstring(raw);counts={}
        for node in tree.findall('counter'):
            kind=node.attrib['type']
            if kind in COUNTERS:
                require(kind not in counts,'unique measured root counter')
                counts[kind]={key:int(node.attrib[key])for key in ('missed','covered')}
        require(set(counts)==set(COUNTERS)and all(min(c.values())>=0 for c in counts.values()),'four complete current counters')
        require(all(value['moduleCounters'][name][k]==counts[k]for k in COUNTERS),'current candidate counter drift')
        modules[name]=counts
        for k in COUNTERS:remaining[k]+=counts[k]['missed']
    require(len(modules)==6 and remaining==value['remaining'],'all-six actual candidate totals')
    return {'source':value['productionSource'],'run':value['run'],'mainClasses':value['mainClasses'],
            'tests':value['tests'],'suites':value['suites'],'remaining':remaining,
            'modulesFourCountersClosed':sum(all(c[k]['missed']==0 for k in COUNTERS)for c in modules.values()),
            'moduleCounters':modules,'acceptedLeafDelta':0,'formalAccepted':False,'effortPercent':None}


def verify_candidate(inventory):
    candidate=inventory['currentPhysicalCandidate'];old=inventory['artifacts']
    require(candidate['version']==1 and candidate['historicalSource']==inventory['source']
            and candidate['historicalDescriptorSha256']==descriptor_digest(old),'immutable historical descriptor binding')
    require(candidate['acceptedLeafDelta']==0 and candidate['scopeChanged']is False and candidate['effortPercent']is None,'candidate no acceptance/effort/scope promotion')
    require(candidate['relocations']==MOVES,'only two approved SSC295 relocations')
    design=candidate['design'];design_raw=git_artifacts(design['source'],[design['path']])[design['path']]
    require(sha(design_raw)==design['sha256']and 'SSC295 固定manager読取のbootstrap共通化'.encode()in design_raw,'canonical SSC295 design provenance')
    paths=[a['path']for a in candidate['artifacts']];old_paths=[a['path']for a in old]
    require(len(paths)==len(set(paths))==len(old_paths),'current candidate no missing/extra/duplicate family')
    expected=eligible(git_files(candidate['source']))
    tracked=subprocess.check_output(['git','ls-files','-z','src','program/characterization'],cwd=ROOT).decode().split('\0')[:-1]
    require(set(paths)==expected==eligible(tracked),'current physical candidate exact Git/worktree scope')
    original={a['path']:a for a in old};used=set();blobs=git_artifacts(candidate['source'],paths)
    for artifact in candidate['artifacts']:
        prior_path=artifact['historicalPath'];require(prior_path in original and prior_path not in used,'one-to-one historical candidate lineage');used.add(prior_path)
        prior=original[prior_path];path=artifact['path']
        require(path==MOVES.get(prior_path,prior_path),'no unapproved artifact relocation')
        require(artifact['owner']==artifact['costOwner']==prior['owner']==prior['costOwner']
                and artifact['kind']==prior['kind']and artifact['acceptance']=='UNASSESSED','unchanged single cost owner; no acceptance promotion')
        require(sha(blobs[path])==artifact['sha256'],'current candidate Git byte mismatch')
        actual=ROOT/path;require(actual.is_file()and not actual.is_symlink()and sha(actual.read_bytes())==artifact['sha256'],'current candidate physical byte mismatch')
        if artifact['kind']=='JAVA':
            module=path.split('/')[1].removeprefix('schubert-nk-');name=path.split('/src/main/java/',1)[1][:-5]
            require(artifact['module']==module and artifact['class']==name,'current Java module/class/path identity')
    require(used==set(old_paths),'all historical families retained')
    result=current_measurement(candidate,inventory['source'])
    return {**result,'physicalArtifacts':len(paths),'relocations':len(MOVES),'historicalSource':inventory['source']}
