# xcache_test

This repository exists to facilitate testing the speed and reliability of XRootD servers at analysis
facilities - in particular, XCache servers.

## Where Can I Run This?

In short: the user must have CMS file access, there must be an XRootD server available, and you must
have the ability to run containers based on a Dockerfile.

To better represent the performance for realistic file access patterns, filesets are generated using
`coffea`'s Dataset Discovery tools within the CMS context. Therefore, the user must have CMS file
access permissions (ie: VOMS proxy for CMS). Since this tests an XRootD server, there must be an
XRootD server available to use. Finally, to ensure that the environment is properly configured, it
is strongly encouraged to run within a container either based on the provided Dockerfile, or otherwise
properly constructed.