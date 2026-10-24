"""Independent four public Unit-data contracts; never systemd, packages, credentials or runtime."""
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import unittest
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8146-c02-four-profiles-pt-v1'
BASELINE='0d90f7838b18882c057f4ab5f5429f25f1e20380'
DIRECTORY='src/deployment/systemd/'
FILES=('schubert-nk-backup.service.template','schubert-nk-bootstrap-admin.service.template',
       'caddy.service.d/schubert-nk-startup-policy.conf','caddy.service.d/schubert-nk-stop-policy.conf')
SPEC='evidence/01_PT/018_NK-OPS-001/1732_C02未対応四設定_単体テスト仕様書.md'
# Fixed independent SS342/343/341 profile, never produced from current files/methods.
ORACLES=(
"""[Unit]
Description=Schubert NK dedicated database backup worker
After=postgresql.service
Requires=postgresql.service
Before=schubert-nk-api.service schubert-nk-web.service caddy.service
[Service]
Type=oneshot
User=schubert-backup
Group=schubert-backup
SupplementaryGroups=schubert
WorkingDirectory=/opt/schubert-nk/current/operations
UnsetEnvironment=JAVA_TOOL_OPTIONS JDK_JAVA_OPTIONS _JAVA_OPTIONS CLASSPATH LD_PRELOAD LD_LIBRARY_PATH
LoadCredential=backup-request:/run/schubert-nk/backup-request/backup-request
LoadCredential=backup-pgpass:/etc/schubert-nk/credentials/backup-pgpass
ExecStart=/usr/bin/java --enable-native-access=ALL-UNNAMED -Dfile.encoding=UTF-8 -Duser.timezone=UTC -XX:+ExitOnOutOfMemoryError -Xms128m -Xmx512m -XX:MaxDirectMemorySize=64m -XX:MaxMetaspaceSize=192m -XX:ReservedCodeCacheSize=128m -cp /opt/schubert-nk/current/operations/batch.jar:/opt/schubert-nk/current/operations/lib/* dev.codex.schubert.nk.batch.file.BackupDatabaseWorker
Restart=no
RemainAfterExit=yes
TimeoutStartSec=30min
TimeoutStopSec=60s
KillMode=control-group
SendSIGKILL=no
RuntimeDirectory=schubert-nk-backup
RuntimeDirectoryMode=0700
RuntimeDirectoryPreserve=yes
ReadWritePaths=/srv/schubert-nk/backup
UMask=0077
NoNewPrivileges=true
CapabilityBoundingSet=
AmbientCapabilities=
MemoryMax=1024M
LimitNOFILE=65536
PrivateTmp=true
PrivateDevices=true
ProtectSystem=strict
ProtectHome=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
ProtectKernelLogs=true
ProtectClock=true
ProtectHostname=true
RestrictSUIDSGID=true
LockPersonality=true
RestrictNamespaces=true
RestrictRealtime=true
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
StandardOutput=journal
StandardError=journal""",
"""[Unit]
Description=Schubert NK initial ADMIN (one-shot only)
After=postgresql.service
Requires=postgresql.service
[Service]
Type=oneshot
User=schubert-api
Group=schubert-api
SupplementaryGroups=schubert schubert-read schubert-web
WorkingDirectory=/opt/schubert-nk/current/api
EnvironmentFile=/etc/schubert-nk/api.env
UnsetEnvironment=JAVA_TOOL_OPTIONS JDK_JAVA_OPTIONS _JAVA_OPTIONS CLASSPATH LD_PRELOAD LD_LIBRARY_PATH
LoadCredential=db-api:/etc/schubert-nk/credentials/db-api
LoadCredential=bootstrap-admin-username:/etc/schubert-nk/credentials/bootstrap-admin-username
LoadCredential=bootstrap-admin-password:/etc/schubert-nk/credentials/bootstrap-admin-password
ExecStart=/usr/bin/java --enable-native-access=ALL-UNNAMED -Dfile.encoding=UTF-8 -Duser.timezone=UTC -XX:+ExitOnOutOfMemoryError -Xmx256m -cp /opt/schubert-nk/current/api/api.jar:/opt/schubert-nk/current/api/lib/* dev.codex.schubert.nk.api.bootstrap.BootstrapAdminMain
SuccessExitStatus=20
Restart=no
TimeoutStartSec=30s
TimeoutStopSec=30s
SendSIGKILL=no
MemoryMax=512M
UMask=0077
CapabilityBoundingSet=
AmbientCapabilities=
NoNewPrivileges=true
PrivateTmp=true
PrivateDevices=true
ProtectSystem=strict
ProtectHome=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
ProtectKernelLogs=true
ProtectClock=true
ProtectHostname=true
RestrictSUIDSGID=true
LockPersonality=true
RestrictNamespaces=true
RestrictRealtime=true
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
StandardOutput=journal
StandardError=journal""",
"""[Service]
User=caddy
Group=caddy
SupplementaryGroups=
Type=notify
Restart=no
TimeoutStartSec=30s
TimeoutStopSec=30s
SendSIGKILL=no
KillMode=control-group
NoNewPrivileges=yes
CapabilityBoundingSet=
AmbientCapabilities=
UMask=0027
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
ReadWritePaths=/var/lib/caddy
ExecStartPre=
ExecStartPre=/usr/bin/caddy validate --config /etc/caddy/Caddyfile
ExecStart=
ExecStart=/usr/bin/caddy run --config /etc/caddy/Caddyfile
ExecReload=""",
"""[Service]
TimeoutStopSec=30s
SendSIGKILL=no""")
ADDITIVE={'LoadCredential','ExecStartPre','ExecStart','ExecReload'}
KEY=re.compile(r'[A-Za-z][A-Za-z0-9]*')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lines(text):
    if not isinstance(text,str) or '\x00' in text:
        raise ValueError('public template text required')
    return [v.strip() for v in text.splitlines() if v.strip() and not v.lstrip().startswith(('#',';'))]


def parse(text):
    section=None
    rows=[]
    seen=set()
    for line in lines(text):
        if line.endswith('\\'):
            raise ValueError('continuation outside declared single-line subset')
        if line.startswith('['):
            if line not in ('[Unit]','[Service]','[Install]'):
                raise ValueError('section outside declared subset')
            section=line[1:-1]
            continue
        key,sep,value=line.partition('=')
        if section is None or not sep or not KEY.fullmatch(key):
            raise ValueError('malformed declared directive')
        identity=(section,key)
        if identity in seen and key not in ADDITIVE:
            raise ValueError('ambiguous duplicate singleton')
        seen.add(identity)
        rows.append((section,key,value))
    if not rows:
        raise ValueError('nonempty declared profile required')
    return rows


def exact(index,text):
    actual=lines(text)
    expected=ORACLES[index].splitlines()
    if actual!=expected:
        raise ValueError('independent ordered profile mismatch')
    rows=parse(text)
    if len(rows)!=len(expected)-sum(v.startswith('[') for v in expected):
        raise ValueError('all declared directives preserved')
    return rows


def values(rows,section,key):
    return [v for s,k,v in rows if (s,k)==(section,key)]


def composed(rows,key,initial):
    value=list(initial)
    for s,k,v in rows:
        if (s,k)==('Service',key):
            if v:
                value.append(v)
            else:
                value.clear()
    return value


def content(index):
    return (ROOT/DIRECTORY/FILES[index]).read_text()


class ProfileTest(unittest.TestCase):
    mutations=0

    def reject(self,index,text):
        with self.assertRaises(ValueError):
            exact(index,text)
        type(self).mutations+=1

    def test_C02CFG001_backup_complete_profile(self):
        rows=exact(0,content(0))
        self.assertEqual(46,len(rows))

    def test_C02CFG002_backup_identity_ownership_and_limits(self):
        r=exact(0,content(0))
        for key,want in (('User',['schubert-backup']),('Group',['schubert-backup']),
                         ('CapabilityBoundingSet',['']),('AmbientCapabilities',['']),
                         ('TimeoutStartSec',['30min']),('TimeoutStopSec',['60s']),
                         ('SendSIGKILL',['no']),('RuntimeDirectoryPreserve',['yes'])):
            self.assertEqual(want,values(r,'Service',key))
        self.assertEqual(['backup-request:/run/schubert-nk/backup-request/backup-request',
                          'backup-pgpass:/etc/schubert-nk/credentials/backup-pgpass'],values(r,'Service','LoadCredential'))

    def test_C02CFG003_admin_complete_profile(self):
        rows=exact(1,content(1))
        self.assertEqual(41,len(rows))

    def test_C02CFG004_admin_identity_skip_and_disabled(self):
        r=exact(1,content(1))
        for key,want in (('User',['schubert-api']),('Group',['schubert-api']),
                         ('SuccessExitStatus',['20']),('Restart',['no']),
                         ('TimeoutStartSec',['30s']),('TimeoutStopSec',['30s']),
                         ('CapabilityBoundingSet',['']),('AmbientCapabilities',[''])):
            self.assertEqual(want,values(r,'Service',key))
        self.assertEqual(['db-api:/etc/schubert-nk/credentials/db-api',
                          'bootstrap-admin-username:/etc/schubert-nk/credentials/bootstrap-admin-username',
                          'bootstrap-admin-password:/etc/schubert-nk/credentials/bootstrap-admin-password'],values(r,'Service','LoadCredential'))
        self.assertFalse(any(s=='Install' for s,_,_ in r))

    def test_C02CFG005_caddy_startup_complete_profile(self):
        rows=exact(2,content(2))
        self.assertEqual(22,len(rows))

    def test_C02CFG006_caddy_stop_complete_profile(self):
        self.assertEqual([('Service','TimeoutStopSec','30s'),('Service','SendSIGKILL','no')],exact(3,content(3)))

    def test_C02CFG007_reset_append_semantics_synthetic_base_only(self):
        rows=exact(2,content(2))
        self.assertEqual(['','/usr/bin/caddy validate --config /etc/caddy/Caddyfile'],values(rows,'Service','ExecStartPre'))
        self.assertEqual(['','/usr/bin/caddy run --config /etc/caddy/Caddyfile'],values(rows,'Service','ExecStart'))
        self.assertEqual([''],values(rows,'Service','ExecReload'))
        self.assertEqual(['/usr/bin/caddy validate --config /etc/caddy/Caddyfile'],composed(rows,'ExecStartPre',['old pre']))
        self.assertEqual(['/usr/bin/caddy run --config /etc/caddy/Caddyfile'],composed(rows,'ExecStart',['old start']))
        self.assertEqual([],composed(rows,'ExecReload',['old reload']))

    def test_C02CFG008_each_directive_omission_and_change(self):
        for index in range(4):
            original=lines(content(index))
            for position,line in enumerate(original):
                if '=' not in line:
                    continue
                self.reject(index,'\n'.join(original[:position]+original[position+1:]))
                changed=list(original)
                changed[position]=line+'-invalid'
                self.reject(index,'\n'.join(changed))
            exact(index,content(index))

    def test_C02CFG009_parser_subset_and_unknown_faults(self):
        for wrong in (None,'','[]','[Socket]\nListenStream=80','User=wrong',
                      '[Service]\n=empty','[Service]\nBad Key=value',
                      '[Service]\nUser=one\nUser=two','[Service]\nUser=one\\'):
            with self.assertRaises(ValueError):
                parse(wrong)
            type(self).mutations+=1
        for index in range(4):
            self.reject(index,content(index)+'\n[Service]\nUnknownKey=value')
            self.reject(index,'[Install]\nWantedBy=multi-user.target\n'+content(index))
        self.assertEqual([('Service','LoadCredential','one'),('Service','LoadCredential','two')],
                         parse('[Service]\nLoadCredential=one\nLoadCredential=two'))

    def test_C02CFG010_sensitive_declaration_relaxations(self):
        for index in range(4):
            raw=content(index)
            for before,after in (('SendSIGKILL=no','SendSIGKILL=yes'),
                                 ('NoNewPrivileges=true','NoNewPrivileges=false'),
                                 ('NoNewPrivileges=yes','NoNewPrivileges=no'),
                                 ('CapabilityBoundingSet=\n','CapabilityBoundingSet=CAP_SYS_ADMIN\n'),
                                 ('Restart=no','Restart=always'),('TimeoutStopSec=30s','TimeoutStopSec=infinity'),
                                 ('ExecStart=/usr/bin/java','ExecStart=+/usr/bin/java'),
                                 ('ExecStart=/usr/bin/caddy','ExecStart=/bin/sh -c /usr/bin/caddy')):
                if before in raw:
                    self.reject(index,raw.replace(before,after))

    def test_C02CFG011_additive_and_reset_not_flattened(self):
        for index in (0,1):
            raw=content(index)
            keep=[v for v in lines(raw) if not v.startswith('LoadCredential=')]
            keep.append([v for v in lines(raw) if v.startswith('LoadCredential=')][-1])
            self.reject(index,'\n'.join(keep))
            self.reject(index,raw+'\nLoadCredential=unexpected:/not-read')
        raw=content(2)
        for value in ('ExecStart=\n','ExecStartPre=\n'):
            self.reject(2,raw.replace(value,''))
        self.reject(2,raw+'\nExecReload=/not-run')
        self.assertEqual(['/new-a','/new-b'],composed(
            [('Service','ExecStart',''),('Service','ExecStart','/new-a'),
             ('Service','ExecStart','/new-b')],'ExecStart',['/old']))

    def test_C02CFG012_exact_git_bytes_no_effective_claim(self):
        self.assertEqual('',subprocess.check_output(
            ['git','diff','--name-only',BASELINE,'HEAD','--','src'],cwd=ROOT,text=True))
        self.assertEqual('',subprocess.check_output(
            ['git','status','--porcelain','--untracked-files=normal','--','src'],cwd=ROOT,text=True))
        for index,name in enumerate(FILES):
            file=ROOT/DIRECTORY/name
            self.assertTrue(file.is_file() and not file.is_symlink())
            old=subprocess.check_output(['git','show',BASELINE+':'+DIRECTORY+name],cwd=ROOT)
            self.assertEqual(hashlib.sha256(old).hexdigest(),sha(file))
            self.assertFalse(os.access(file,os.X_OK))
            if index>=2:
                self.assertEqual([],values(exact(index,content(index)),'Unit','Requires'))
                self.assertEqual([],values(exact(index,content(index)),'Unit','After'))


def main():
    invocation=capture(Path(__file__))
    if OUT.exists():
        raise ValueError('new-only declared profile evidence')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    inputs={DIRECTORY+p:sha(ROOT/DIRECTORY/p) for p in FILES}
    inputs[SPEC]=sha(ROOT/SPEC)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    log=io.StringIO()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProfileTest))
    static=subprocess.run([sys.executable,'-B','-m','pyflakes',str(Path(__file__))],
                          cwd=ROOT,text=True,capture_output=True,check=False)
    actual=0 if result.wasSuccessful() and result.testsRun==12 and not result.skipped and static.returncode==0 else 1
    if inputs!={p:sha(ROOT/p) for p in inputs}:
        raise ValueError('fixed profile source changed during own PT')
    verify(invocation)
    value=dict(actualExit=actual,source=source,baselineDeclarationSource=BASELINE,invocation=invocation,
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        startUTC=started,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        environment=dict(os=platform.platform(),python=sys.version,executable=sys.executable),
        inputHashes=inputs,testsRun=result.testsRun,failed=len(result.failures),errors=len(result.errors),
        skipped=len(result.skipped),mutationChecks=ProfileTest.mutations,
        cases=[dict(testId=f'C02CFG{n:03d}',result='PASS' if result.wasSuccessful() else 'NOT_QUALIFIED',
                    oracle='1732 fixed SS declarative profile/explicit reset-append and mutation expectations',
                    actual='all assertions passed' if result.wasSuccessful() else 'see own public log') for n in range(1,13)],
        log=log.getvalue(),static=dict(command=static.args,actualExit=static.returncode,
                                    stdout=static.stdout,stderr=static.stderr),
        perFileDeclaredDirectiveCounts={p:len(parse(content(n))) for n,p in enumerate(FILES)},
        caddyAfterRequiresWebEffective='UNKNOWN_BASE_PACKAGE_NOT_READ_NO_RUNTIME_QUALIFICATION',
        caddyOwnDropinDependencyDeclarations=[],
        statementCoverage=None,methodCoverage=None,classCoverage=None,branchCoverage=None,
        coverageApplicability='DECLARATIVE_DATA_NO_EXECUTABLE_COUNTERS_NOT_JAVA_EXCLUSION',
        original22CasesReplayed=False,javaProductTestsExecuted=0,
        systemdSyntaxToolExecuted=False,effectiveUnitQualified=False,
        actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualCredentialReads=0,
        actualUnitActions=0,targetInitialization=False,wholeC02Accepted=False,
        whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,bugs=[])
    os.umask(0o077)
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as handle:
        json.dump(value,handle,ensure_ascii=False,sort_keys=True,indent=2)
        handle.write('\n')
    print(json.dumps(dict(actualExit=actual,source=source,tests=result.testsRun,failed=len(result.failures),
                         errors=len(result.errors),mutations=ProfileTest.mutations,
                         manifestSha256=sha(OUT/'manifest.json'))))
    raise SystemExit(actual)

if __name__=='__main__':
    main()
