"""Freeze existing twelve Browser oracles with identity-only source rebinding, no login."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate
from pg3564_current_browser_resume_sources import SOURCE
from pg3138_browser_cohort_ready import JAVA,classpath,SHARED,ROOT

SLOT='pg3578-current-browser-ready-v1'
OLD='a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'
JAVA_INPUTS=SHARED+['tools/quality/vm/050_s1/NativeNkBrowserBusinessCohort.java','tools/quality/vm/050_s1/NativeNkBrowserBusinessOracleTest.java']
ORACLES=['tools/quality/pg3136_browser_rows_oracle_test.py','tools/quality/pg3166_browser_tls_witness_test.py']
PINNED=JAVA_INPUTS+ORACLES+['tools/quality/pg3136_browser_rows_oracle.py','program/characterization/baseline/current/artifacts/CHR-U01.json','tools/quality/pg3578_current_browser_ready.py']


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def require_ready():
    out=W/SLOT;value=json.loads((out/'manifest.safe.json').read_bytes())
    if not(value['actualExit']==0 and value['sourceQualified'] and value['productionSource']==SOURCE and value['credentialReadOnlyQualified'] and value['plannedCases']==12):
        raise ValueError('actual current Browser readiness required')
    if value['inputs']!={n:sha(ROOT/n)for n in PINNED}or value['classes']!={str(p.relative_to(out/'classes')):sha(p)for p in(out/'classes').rglob('*.class')}:
        raise ValueError('frozen Browser oracle drift')
    return value


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed Browser preflight required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);classes=out/'classes';classes.mkdir(mode=0o700)
    generated=out/'identity-only-sources';generated.mkdir(mode=0o700)
    sources=[];identity_deltas={}
    for name in JAVA_INPUTS:
        raw=(ROOT/name).read_text()
        if name not in SHARED:
            if raw.count(OLD)!=1:raise ValueError('one independent positive identity per oracle and client required')
            updated=raw.replace(OLD,SOURCE)
            if updated.replace(SOURCE,OLD)!=raw:raise ValueError('identity-only transformation required')
            p=generated/Path(name).name;p.write_text(updated);p.chmod(0o400);sources.append(str(p));identity_deltas[name]={'from':sha(ROOT/name),'to':sha(p),'changedLiteralCount':1,'behaviorAndAssertionsUnchanged':True}
        else:sources.append(name)
    operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();inputs={n:sha(ROOT/n)for n in PINNED};start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    commands=[[str(JAVA/'javac'),'-Xlint:all','-Werror','-cp',classpath(classes),'-d',str(classes),*sources],[str(JAVA/'java'),'-cp',classpath(classes),'dev.codex.schubert.characterization.NativeNkBrowserBusinessOracleTest']]
    commands.extend(['python3','-B',n]for n in ORACLES)
    commands.append([str(JAVA/'java'),'-cp',classpath(classes),'dev.codex.schubert.characterization.NativeNkBrowserBusinessCohort','preflight',str(out/'credential-ro')])
    phases=[]
    for i,command in enumerate(commands,1):
        with(out/f'phase-{i}.private.log').open('xb')as log:
            if i==len(commands):
                with management_gate(P/'current-management-critical.lock'):r=subprocess.run(command,stdout=log,stderr=log,timeout=90)
            else:r=subprocess.run(command,stdout=log,stderr=log,timeout=90)
        phases.append(r.returncode)
        if r.returncode:break
    fixed=operator==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()and not subprocess.check_output(['git','status','--porcelain'])and inputs=={n:sha(ROOT/n)for n in PINNED}
    value={'actualExit':next((c for c in phases if c),0),'sourceQualified':fixed,'operatorSource':operator,'productionSource':SOURCE,'plannedCases':12,'phases':phases,'credentialReadOnlyQualified':len(phases)==len(commands)and not any(phases),'inputs':inputs,'classes':{str(p.relative_to(classes)):sha(p)for p in classes.rglob('*.class')},'identityOnlyTransforms':identity_deltas,'startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rootBrowserStarts0':True,'formalAccepted':False}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    for p in classes.rglob('*.class'):p.chmod(0o400)
    print(json.dumps({k:value[k]for k in ['actualExit','sourceQualified','plannedCases','phases','credentialReadOnlyQualified','rootBrowserStarts0','formalAccepted']}));return value['actualExit']or(0 if fixed else 1)


if __name__=='__main__':raise SystemExit(main())
