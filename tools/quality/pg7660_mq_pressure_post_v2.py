"""BUG1670 same-source114/14 independent actual CRC/coverage/static, never old result transfer."""
import pg7646_mq_pressure_post as previous
import pg7658_mq_pressure_host_v2 as host

def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7658-mq-pressure-host-v2'
    post.OUT=post.host.BASE/'PG7660-mq-pressure-post-v2'
    post.PRIVATE=post.host.W/'pg7660-mq-pressure-post-v2'
    return post

if __name__=='__main__':
    host.previous.previous.verify_inputs()
    configure().main()
