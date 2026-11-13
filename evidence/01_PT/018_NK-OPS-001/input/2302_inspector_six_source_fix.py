"""Minimal public-source repairs only. No compilation, class loading, file provider or authority call."""
from pathlib import Path
import json,hashlib,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';c=json.loads((b/'input/2301_inspector_six_source_start.json').read_text());out=b/'evidence/PG29400-inspector-six-main-source-repair-v1';assert not out.exists();out.mkdir();patches=[]
def patch(name,pairs):
 p=r/name;old=p.read_text();new=old
 for a,z in pairs:assert new.count(a)==1,(name,a);new=new.replace(a,z)
 assert old!=new;(out/(p.stem+'.before.java.txt')).write_text(old);p.write_text(new);patches.append(dict(path=name,beforeSha256=hashlib.sha256(old.encode()).hexdigest(),pairs=pairs))
api='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/'
imp=('import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;\n','')
def add_import(anchor):return (anchor,imp[0]+anchor)
patch(api+'maintenance/InboxResponseInspector.java',[add_import('import dev.codex.schubert.nk.api.idempotency.InboxCompletion;'),('        | IllegalStateException failure) {\n      return false;','        | IllegalStateException failure) {\n      // BUG2825: owned plaintext/wire wipes have finished before graph classification.\n      TemporaryInfrastructureException.preserveFatal(failure);\n      return false;')])
for f,anchor,old in [('file/InspectorApplication.java','import dev.codex.schubert.nk.api.maintenance.InspectionExecution;','        } catch (IOException unavailable) {\n          throw new InspectorCredentialException();'),('maintenance/InspectorProcess.java','import dev.codex.schubert.nk.api.file.AesCredentialFile;','      } catch (IOException unavailable) {\n        throw new InspectorCredentialException();'),('maintenance/InspectionRunExecutor.java','import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;','      } catch (IOException unavailable) {\n        return Optional.of(InspectionExecution.Status.TIME_LIMIT);')]:
 lines=old.splitlines();indent=lines[-1][:len(lines[-1])-len(lines[-1].lstrip())];new='\n'.join(lines[:-1]+[indent+'// BUG2826: preserve fatal graph identity before the ordinary fixed outcome.',indent+'TemporaryInfrastructureException.preserveFatal(unavailable);',lines[-1]])
 patch(api+f,[add_import(anchor),(old,new)])
patch(api+'maintenance/InspectorLauncher.java',[add_import('import dev.codex.schubert.nk.api.file.InspectorApplication;'),('    } catch (InspectorLaunchConfiguration.Invalid\n        | InspectorCredentialException\n        | NoSuchAlgorithmException failure) {\n      return 70;\n    } catch (IOException failure) {\n      return 50;','    } catch (InspectorLaunchConfiguration.Invalid invalid) {\n      return 70;\n    } catch (InspectorCredentialException | NoSuchAlgorithmException failure) {\n      // BUG2827: callback/provider fatal graphs are not configuration catalog outcomes.\n      TemporaryInfrastructureException.preserveFatal(failure);\n      return 70;\n    } catch (IOException failure) {\n      TemporaryInfrastructureException.preserveFatal(failure);\n      return 50;')])
name='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/InspectorEnvironmentReader.java'
old='''          require(channel.size() == expected);
          while (buffer.hasRemaining()) {
            int position = buffer.position();
            int remaining = buffer.remaining();
            int count = channel.read(buffer);
            if (count == -1) break;
            require(count > 0 && count <= remaining && buffer.position() == position + count);
          }
          require(buffer.position() == expected);
          require(channel.size() == expected);'''
new='''          // BUG2829: all byte progress must agree with both seek and buffer positions.
          require(channel.size() == expected && channel.position() == 0);
          while (buffer.hasRemaining()) {
            int position = buffer.position();
            long channelPosition = channel.position();
            int remaining = buffer.remaining();
            int count = channel.read(buffer);
            if (count == -1) {
              require(buffer.position() == position && channel.position() == channelPosition);
              break;
            }
            require(
                count > 0
                    && count <= remaining
                    && buffer.position() == position + count
                    && channel.position() == channelPosition + count);
          }
          require(buffer.position() == expected && channel.position() == expected);
          require(channel.size() == expected);'''
patch(name,[(old,new)])
(out/'patches.json').write_text(json.dumps(patches,ensure_ascii=False,indent=2)+'\n');assert len(patches)==6
fmt=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace'];p=subprocess.run(fmt+[str(r/v['path']) for v in patches],capture_output=True);(out/'format.stdout').write_bytes(p.stdout);(out/'format.stderr').write_bytes(p.stderr);assert p.returncode==0
(out/'manifest.json').write_text(json.dumps(dict(actualExit=0,sourceAtStart=c['source'],mainSourcesChanged=6,productTestsExecuted=0,compileExecuted=False,bugs=['BUG-2825','BUG-2826','BUG-2827','BUG-2829'],runtimeQualified=False,patchesSha256=hashlib.sha256((out/'patches.json').read_bytes()).hexdigest(),inputs=[dict(path=v['path'],sha256=hashlib.sha256((r/v['path']).read_bytes()).hexdigest()) for v in patches]),ensure_ascii=False,indent=2)+'\n');print('six source repairs formatted; no compile/PT/actual4/backend/native/Root')
