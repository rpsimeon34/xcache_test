# xcache_test

Credit: The sample analysis code is heavily based on the
[Analysis Grand Challenge](https://github.com/iris-hep/analysis-grand-challenge).

This repository exists to facilitate testing the speed and reliability of XRootD servers at analysis
facilities - in particular, XCache servers.

## Where Can I Run This?

In short: the user must have CMS file access, there must be an XRootD server available, and you must
have the ability to run containers based on a Dockerfile.

To better represent the performance for realistic file access patterns, filesets were generated using
`coffea`'s Dataset Discovery tools within the CMS context. Therefore, the user must have CMS file
access permissions (ie: VOMS proxy for CMS). Since this tests an XRootD server, there must be an
XRootD server available to use. Finally, to ensure that the environment is properly configured, it
is strongly encouraged to run within a container either based on the provided Dockerfile, or otherwise
properly constructed.

Parts of this code are written specifically for the Wisconsin Analysis Facility. In particular, references
to the [cowtools](https://github.com/rpsimeon34/cowtools) package will work only at Wisconsin, and must be
changed to reflect the cluster-building process at each site.

## How to Run

First, make sure that you have generated a valid VOMS proxy. Then, to run the test, do
```
python3 xcache_test.py
```
This will save a file at `reports/\<xcache choice\>/\<A\>_\<B\>_\<C\>_\<D\>.pkl`, and another with the same
name but an `.html` suffix. `\<xcache choice\>` is the choice of XRootD server, and the other 4 variables
in the file name are (in order) the choice of running locally or distributed, max # workers, max # files per
sample, and max # chunks per file. These are all configurable through `utils/config.py` and
`utils/benchmarking.py`.

To parse the reports, do
```
python3 parse_reports.py --report path_to_report.pkl
```
There are also optional flags `--messages` and `--sites` that can generate figures showing the error messages
that caused certain chunks to fail, and also the distribution of sites that files were read from. Note that the
latter is less informative when testing an XCache, since it will show the XCache as the source for all files.

## What Configurations Should I Set?

Many configurations inherited from the AGC are available, but the ML task is not currently available here. The
file `utils/config.py` is the most important for the XRootD test. One can configure whether to run locally or
on a cluster, how many workers to request at maximum, and which Analysis Facility one is running at. To add a
new AF as an option, the `get_client` function of `xcache_test.py` should be modified appropriately. It is also
probably necessary to modify the `main` function of that file, where the variable `xrd_base` is set.