"""Parent18 for the necessary post-CHR sealed image, same genuine parent termination."""
import inspect
import pg2888_network_parent_projection as prior

SLOT='pg2904-network-after-chr-parent-projection-v1'
SEAL='pg2902-network-after-chr-full-seal-v1'


def payload(sha,bom=None):return prior.payload(sha,bom).replace(prior.SEAL,SEAL)


def main():
    ns={**prior.__dict__,'SLOT':SLOT,'SEAL':SEAL,'payload':payload}
    exec(compile(inspect.getsource(prior.main),'<fresh sealed same parent18>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
