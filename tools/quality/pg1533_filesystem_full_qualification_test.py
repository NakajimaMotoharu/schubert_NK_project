"""Independent fabricated artifact graph tests; these are tooling, not Production PT."""
import contextlib
import datetime
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as E
import zipfile
from pg1533_filesystem_full_qualification import CODE


class QualificationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='pg1533-qualification-')
        self.addCleanup(self.tmp.cleanup)
        self.b = Path(self.tmp.name)
        self.s = self.b / 'source-full-PG1532'
        self.o = self.b / 'runs/PG1532-six-v1'
        self.o.mkdir(parents=True)
        self.begin = {'productionSource': '4d6bcbddb417b76d27e52d5d9640752c300edccf', 'sourceSnapshotHead': 'a'*40, 'inputs': {}, 'startUTC': (datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(minutes=1)).isoformat()}
        self.v = {'productionSource': self.begin['productionSource'], 'sourceSnapshotHead': 'a'*40, 'actualExit': 0, 'mavenExit': 0, 'issues': [], 'sourceInputsUnchanged': True, 'tests': 3583, 'elapsedSeconds': 60, 'startUTC': self.begin['startUTC'], 'modules': {}}
        archive=self.b/'transfer/PG1532-source.tar';archive.parent.mkdir();archive.write_bytes(b'independent archive fixture');self.begin['sourceArchiveSha256']=self.sha(archive)
        self.old={'modules': {}}
        expected={'protocol':(81,17,174),'storage':(163,23,74),'bootstrap':(298,40,105),'api':(963,157,401),'web':(886,129,315),'batch':(1192,158,568)}
        changed=['dev/codex/schubert/nk/batch/file/'+n+'.class' for n in ['InspectorEnvironmentReader$NioIo','EnvironmentInodePolicy']]
        added=['dev/codex/schubert/nk/storage/LinuxFilesystemClassifier'+n+'.class' for n in ['', '$StatfsCall']]
        for m,(nt,ns,nc) in expected.items():
            t=self.s/f'src/schubert-nk-{m}/target';reports=t/'surefire-reports';reports.mkdir(parents=True);xmls={}
            for i in range(ns):
                n=nt-ns+1 if i==0 else 1
                x=E.Element('testsuite',tests=str(n),failures='0',errors='0',skipped='0')
                for j in range(n):E.SubElement(x,'testcase',classname=m+'.Suite'+str(i),name='test'+str(j))
                p=reports/f'TEST-{i}.xml';E.ElementTree(x).write(p);xmls[p.name]=self.sha(p)
            E.ElementTree(E.Element('BugCollection')).write(t/'spotbugsXml.xml')
            cov=E.Element('report');session=E.SubElement(cov,'sessioninfo',id='independent-test-session',start='1',dump='2');counters={}
            for k in ['LINE','METHOD','CLASS','BRANCH']:
                E.SubElement(cov,'counter',type=k,covered='1',missed='0');counters[k]={'covered':1,'missed':0}
            if m=='storage':
                c=E.SubElement(cov,'class',name='dev/codex/schubert/nk/storage/LinuxFilesystemClassifier')
                for k in counters:E.SubElement(c,'counter',type=k,covered='1',missed='0')
            p=t/'site/jacoco/jacoco.xml';p.parent.mkdir(parents=True);E.ElementTree(cov).write(p);(t/'jacoco.exec').write_bytes(b'fixture-not-native')
            names=(changed if m=='batch' else added if m=='storage' else [])
            names=names+[m+'/Fixture'+str(i)+'.class'for i in range(nc-len(names))]
            hashes={}
            with zipfile.ZipFile(t/f'schubert-nk-{m}-0.1.0-SNAPSHOT.jar','w')as z:
                for name in names:
                    payload=('independent:'+name).encode();z.writestr(name,payload);p=t/'classes'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(payload);hashes[name]=self.sha(p)
            prev={p:h for p,h in hashes.items()if p not in added}
            for p in changed:
                if p in prev:prev[p]='0'*64
            self.old['modules'][m]={'mainClassHashes':prev}
            self.v['modules'][m]={'tests':nt,'suites':ns,'mainClasses':nc,'failures':0,'errors':0,'skipped':0,'flaky':0,'staticIssues':0,'xmlHashes':xmls,'mainClassHashes':hashes,'coverage':counters,'sessions':[dict(session.attrib)]}
        p=self.b/'runs/PG1476-six-v1/manifest.safe.json';p.parent.mkdir(parents=True);p.write_text(json.dumps(self.old))
        self.v['endUTC']=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(minutes=1)).isoformat()

    @staticmethod
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

    def execute(self):
        (self.o/'begin.safe.json').write_text(json.dumps(self.begin));(self.o/'manifest.safe.json').write_text(json.dumps(self.v))
        raw=CODE.replace("B=Path('/home/mini/schubert-nk-pgpt')", 'B=Path('+repr(str(self.b))+')')
        with contextlib.redirect_stdout(io.StringIO())as stream:exec(compile(raw,'<independent qualification fixture>','exec'), {})
        return json.loads(stream.getvalue())

    def test_complete_graph_and_nonformal(self):
        r=self.execute();self.assertEqual((r['tests'],r['suites'],r['mainClasses']),(3583,524,1637));self.assertFalse(r['formalAccepted']);self.assertFalse(r['global100']);self.assertTrue(r['sameSourceNativePending'])

    def test_foreign_source_refused(self):
        self.v['productionSource']='f'*40
        with self.assertRaises(ValueError):self.execute()

    def test_skip_flaky_missing_module_refused(self):
        for k in ['skipped','flaky','staticIssues']:
            with self.subTest(k=k):
                self.v['modules']['batch'][k]=1
                with self.assertRaises(ValueError):self.execute()
                self.v['modules']['batch'][k]=0
        del self.v['modules']['api']
        with self.assertRaises(ValueError):self.execute()

    def test_mutated_byte_refused(self):
        p=next((self.s/'src/schubert-nk-protocol/target/classes').rglob('*.class'));p.write_bytes(b'changed after package')
        with self.assertRaises(ValueError):self.execute()

    def test_duplicate_testcase_refused(self):
        p=self.s/'src/schubert-nk-storage/target/surefire-reports/TEST-0.xml';x=E.parse(p);cs=x.getroot().findall('testcase');cs[1].attrib=dict(cs[0].attrib);x.write(p)
        self.v['modules']['storage']['xmlHashes'][p.name]=self.sha(p)
        with self.assertRaises(ValueError):self.execute()

    def test_missing_classifier_branch_refused(self):
        p=self.s/'src/schubert-nk-storage/target/site/jacoco/jacoco.xml';x=E.parse(p)
        for c in x.getroot().find('.//class').findall('counter'):
            if c.attrib['type']=='BRANCH':c.attrib['missed']='1'
        x.write(p)
        with self.assertRaises(ValueError):self.execute()

if __name__=='__main__':unittest.main()
