"""Pure prerequisite validation and exact retained Git-tool provenance, never invokes Maven or a target."""
import hashlib
import json
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7730_media_stream_six_compile as compilation
from pg7000_monitoring_mode_host import MODULES

META=host.BASE/'PG7740-web-classpath-metadata-v1/manifest.json'
META_SHA='a273b9d1560a096382c07571ba33a3ee10649bc2dc6a0c5ed06a491a5e231aca'
SOURCE_COMMIT='f852bbc3ad2b1e075436688eb48f669a742f75cb'
META_ENTRY='tools/quality/pg7740_web_classpath_metadata.py'
COMMAND=[str(host.TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','--no-transfer-progress',
 '-Dmaven.repo.local='+str(host.TC/'m2/repository'),'-pl',MODULES,'-am',
 'org.apache.maven.plugins:maven-dependency-plugin:3.9.0:build-classpath','-DincludeScope=test','-Dmdep.outputFile=target/pgpt-test-classpath.txt']

def require(value,message):
    if not value:raise ValueError(message)

def validate_receipt(value,source,compile_sha,classpath_sha):
    require(value['actualExit']==value['terminal']['actualExit']==0 and value['source']==source
      and value['originalCompileSha256']==compile_sha,'exact genuine metadata source/compile/terminal')
    require(value['metadataOnly'] is True and value['compileRepeated'] is False and value['productionPtExecuted']==0
      and value['originalClassBytesAndMtimesUnchanged'] is True and value['sourceInputsUnchanged'] is True,
      'metadata only, no repeated build/PT or class/source changes')
    require(value['classpath']['sha256']==classpath_sha and value['command']==COMMAND,'exact real output and one approved offline metadata command')

def verify_metadata():
    require(host.sha(META)==META_SHA,'original completed metadata receipt unchanged')
    value=json.loads(META.read_bytes());normal_file=compilation.SLOT/'manifest.safe.json';normal=json.loads(normal_file.read_bytes())
    cp=compilation.SLOT/'snapshot/src/schubert-nk-web/target/pgpt-test-classpath.txt'
    require(cp.is_file() and not cp.is_symlink() and value['classpath']['path']==str(cp),'exact original current-snapshot classpath path')
    validate_receipt(value,compilation.SOURCE,host.sha(normal_file),host.sha(cp))
    require(normal['source']==compilation.SOURCE and normal['actualExit']==normal['terminal']['actualExit']==0
      and normal['testsExecuted']==0,'original compile remains genuinely zero, not PT pass')
    jars={r['path']:r['sha256'] for r in normal['jars'].values()}
    require(jars==value['originalJarHashes'] and all(host.sha(Path(p))==h for p,h in jars.items()),'all original six normal Jar bytes retained')
    require(all(Path(p).is_file() and host.sha(Path(p))==h for p,h in value['resolvedMetadataJarHashes'].items()),'every generated metadata dependency still has actual original bytes')
    invocation=value['invocation']
    bindings={**invocation['loadedProjectPythonSources'],invocation['entrypointPath']:invocation['entrypointSha256'],invocation['libraryPath']:invocation['librarySha256']}
    for name,digest in bindings.items():
        before=subprocess.check_output(['git','show',SOURCE_COMMIT+':'+name],cwd=host.ROOT)
        require(hashlib.sha256(before).hexdigest()==digest,'every actually executed metadata tool/library byte preserved in exact Git version')
        current=(host.ROOT/name).read_bytes()
        if name==META_ENTRY:
            require(before.count(b'import hashlib\n')==1 and current==before.replace(b'import hashlib\n',b'',1),
              'only unused stdlib import removed after terminal; no goal replay or behavior change')
        else:require(current==before,'all other executed helper sources unchanged')
    return dict(path=str(META),sha256=META_SHA,source=compilation.SOURCE,executedToolSourceCommit=SOURCE_COMMIT,
      exactExecutedSourcesVerified=True,postRunOnlyUnusedImportRemoved=True,metadataGoalReplayed=False)
