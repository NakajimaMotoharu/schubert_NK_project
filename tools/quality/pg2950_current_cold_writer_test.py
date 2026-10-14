"""Existing finite cold writer's full independent fixtures bound to current exact run/name."""
import types
import unittest
from unittest.mock import patch
import pg1160_runtime_writer_test as fixture
from pg2950_current_cold_resume_sources import sources


class CurrentColdWriter(fixture.WriterTest):
    @classmethod
    def setUpClass(cls):
        cls.writer_source=sources()['pg2950_runtime_writer.py']

    def exercise(self,*args,**kwargs):
        module=types.ModuleType('currentcoldwriter');exec(self.writer_source,module.__dict__)
        with patch.object(fixture,'writer',module):return super().exercise(*args,**kwargs)

    def test_base_native_literal_and_negative(self):
        module=types.ModuleType('currentcoldwriter');exec(self.writer_source,module.__dict__)
        base=b'[Service]\nExecStart=/usr/bin/java -cp literal dev.codex.schubert.nk.batch.file.MorningProcessMain\n'
        agent=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false -cp literal dev.codex.schubert.nk.batch.file.MorningProcessMain'
        native=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+agent+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
        golden=b'# SS343 6.13: explicit same-run fresh activation; retire after genuine terminal.\n[Service]\nExecStart=\nExecStart='+agent+b' --resume 0dc63b79-3f9a-450c-b2a6-56f86272d272\n'
        self.assertEqual('zz-pg2950-once-resume.conf',module.NAME)
        self.assertEqual(golden,module.fixed_dropin(base,native))
        for b,n in [(None,native),(base,None),(base,b'foreign'),(base+base,native),(base.replace(b'-cp',b'--resume x -cp'),native),(base.replace(b'-cp',b'-javaagent:foreign -cp'),native)]:
            with self.assertRaises(ValueError):module.fixed_dropin(b,n)


if __name__=='__main__':unittest.main()
