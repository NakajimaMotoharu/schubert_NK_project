"""Independent corrected23 actual-source qualification; failed/partial history unchanged."""
import pg7134_http_terminal_post as post


if __name__=='__main__':
    post.original.COMPILE=post.host.W/'pg7136-http-terminal-six-compile-v3'
    post.original.SLOT=post.host.W/'pg7138-http-terminal-host-v2'
    post.SLOT=post.host.W/'pg7140-http-terminal-post-v2'
    post.OUT=post.host.BASE/'PG7140-http-terminal-post-v2'
    post.RAW_SHA='1a37984df4bd113a811b48e106222dd6a046724ee8b6129612ae3107ce23094b'
    post.COMPILE_SHA='a6643c4eb6df5bedaa99a40ca8a790d0c4af86c3611b6bca60dc0990e1dbf30d'
    post.main()
