"""Independent pidfd reservation/identity/order/all fault vectors, no actual signal."""
import ast
import unittest
from pg782_owned_handoff import terminate,payload


class Test(unittest.TestCase):
    def test_normal_and_every_fault_and_generation_change(self):
        def run(fault=None,foreign=False):
            events=[];reads=0
            def event(v):
                events.append(v)
                if len(events)==fault:raise OSError('literal fault')
            def verify(pid,ticks):
                nonlocal reads
                event('verify');reads+=1;self.assertEqual((7,11),(pid,ticks));return 'foreign'if foreign and reads==2 else'fixed'
            def opener(pid):event('open');return 29
            def reserve(pid,v):event('reserve');self.assertEqual((7,'fixed'),(pid,v))
            def sender(fd):event('TERM');self.assertEqual(29,fd)
            def wait(fd):event('wait');return True
            def close(fd):event('close')
            try:terminate(7,11,verify,reserve,opener,sender,wait,close);return events,None
            except (OSError,ValueError)as e:return events,e
        events,error=run();self.assertIsNone(error);self.assertEqual(['verify','open','verify','reserve','TERM','wait','close'],events)
        for at in range(1,8):
            seen,error=run(at);self.assertIsInstance(error,OSError)
            if at<=4:self.assertNotIn('TERM',seen)
        events,error=run(foreign=True);self.assertIsInstance(error,ValueError);self.assertNotIn('TERM',events);self.assertEqual('close',events[-1])
        ast.parse(payload());self.assertNotIn('SIGKILL',payload());self.assertIn('signal.SIGTERM',payload())


if __name__=='__main__':unittest.main()
