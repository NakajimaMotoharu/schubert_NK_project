import types
import unittest
from unittest.mock import patch
import pg1160_runtime_writer_test as fixture
from pg2316_current_cold_resume_sources import sources,RUN


class CurrentWriter(fixture.WriterTest):
    def exercise(self,*args,**kwargs):
        module=types.ModuleType('currentcoldwriter')
        exec(sources()['pg2316_runtime_writer.py'],module.__dict__)
        with patch.object(fixture,'writer',module):return super().exercise(*args,**kwargs)

    def test_base_native_literal_and_negative(self):
        module=types.ModuleType('currentcoldwriter')
        exec(sources()['pg2316_runtime_writer.py'],module.__dict__)
        base=b'[Service]\nExecStart=/usr/bin/java -cp literal dev.codex.schubert.nk.batch.file.MorningProcessMain\n'
        agent=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false -cp literal dev.codex.schubert.nk.batch.file.MorningProcessMain'
        native=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+agent+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
        golden=b'# SS343 6.13: explicit same-run fresh activation; retire after genuine terminal.\n[Service]\nExecStart=\nExecStart='+agent+b' --resume 91f5484b-9702-4c7c-97f3-dd5110a853f9\n'
        self.assertEqual('zz-pg2316-once-resume.conf',module.NAME)
        self.assertEqual(RUN,module.RUN_ID)
        self.assertEqual(golden,module.fixed_dropin(base,native))
        for b,n in [(None,native),(base,None),(base,b'foreign'),(base+base,native),(base.replace(b'-cp',b'--resume x -cp'),native),(base.replace(b'-cp',b'-javaagent:foreign -cp'),native)]:
            with self.assertRaises(ValueError):module.fixed_dropin(b,n)


if __name__=='__main__':unittest.main()
