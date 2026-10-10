import unittest
import pg1238_fresh_day_ordinary_before as p

class FreshBeforeTest(unittest.TestCase):
    def test_actual_noargs_day_skip_admission_source_and_capacity(self):
        s=p.payload();compile(s,'<actual current new day admission>','exec')
        for part in ["'run':'PG1238-fresh-day-ordinary-before-v1'",'require(not same_day)',"r['step']=='CLEAN_INBOX_OUTBOX'",'ordinary_argv(base_bytes,native_bytes)','requiredGuestWriteAndCloseBytes',"'--resume'not in argv"]:
            self.assertTrue(part in s,part)
        self.assertFalse("'run':'PG1236-completed-runtime-retired-post-v1'"in s)
        # Independent fixed default+agent declaration normal and malformed.
        base=b'[Service]\nExecStart=/usr/bin/java -cp literal dev.codex.schubert.nk.batch.file.MorningProcessMain\n'
        argv=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false -cp literal dev.codex.schubert.nk.batch.file.MorningProcessMain'
        native=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+argv+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
        self.assertEqual(p.ordinary_argv(base,native),argv.decode())
        for a,b in [(None,native),(base,None),(base,native+b'x'),(base.replace(b'-cp',b'--resume x -cp'),native),(base+base,native)]:
            with self.assertRaises(ValueError):p.ordinary_argv(a,b)

if __name__=='__main__':unittest.main()
