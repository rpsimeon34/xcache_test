import awkward as ak
from coffea import processor
from coffea.analysis_tools import PackedSelection
from coffea.dataset_tools import apply_to_fileset, max_files, max_chunks
import dask
from dask.distributed import Client, performance_report
import datetime
import gzip
import hist
import hist.dask as hda
import json
from pathlib import Path
import pickle
import time

from test_processor import TtbarAnalysis
import utils # contains code for bookkeeping and cosmetics, as well as some boilerplate

FILESET_LOC = "xcache_test_fileset_available.json.gz"
N_FILES_MAX_PER_SAMPLE = utils.config["benchmarking"]["N_FILES_MAX_PER_SAMPLE"]
N_CHUNKS_MAX_PER_FILE = utils.config["benchmarking"]["N_CHUNKS_MAX_PER_FILE"]
MAX_WORKERS = utils.config["benchmarking"]["MAX_WORKERS"]
XRD_CHOICE = utils.config["benchmarking"]["XROOTD_CHOICE"]

# Imports specific to Wisconsin Analysis Facility
if utils.config["global"]["AF"] == "Wisconsin":
    import cowtools.jobqueue

def get_client():
    if not utils.config["benchmarking"]["USE_HTC"]:
        return Client()
    if utils.config["global"]["AF"] == "Wisconsin":
        client = cowtools.jobqueue.GetCondorClient(
            max_workers=utils.config["benchmarking"]["MAX_WORKERS"],
            memory="4 GB",
            disk="2 GB"
        )
        return client
    else:
        raise ValueError(f"""
        No known way to create a distributed client for AF {utils.config['global']['AF']}.
        Please configure the client yourself, and include it in xcache_test.py.""")

def main():
    #Store reports here
    Path(f"reports/{XRD_CHOICE.replace('.','_')}").mkdir(parents=True, exist_ok=True)
    if utils.config["benchmarking"]["USE_HTC"]:
        htc_label = "HTC"
    else:
        htc_label = "local"
        
    ###################### Modify this if adding a new AF/set of XRootD options ######################
    if utils.config["global"]["AF"] == "Wisconsin":
        if XRD_CHOICE == "cmsxrootd.fnal.gov":
            xrd_base = f"root://cmsxrootd.fnal.gov/"
        else:
            xrd_base = f"root://cms{XRD_CHOICE}.hep.wisc.edu/"
    ##################################################################################################
    
    #Prepare fileset
    print(f"Applying to signal fileset {FILESET_LOC}")
    with gzip.open(FILESET_LOC, "rt") as file:
        fileset_full = json.load(file)
    #Only do at most first # files
    if N_FILES_MAX_PER_SAMPLE:
        fileset_maxfiles = max_files(fileset_full,N_FILES_MAX_PER_SAMPLE)
    else:
        fileset_maxfiles = fileset_full
    #Only do at most first # chunks of each file
    if N_CHUNKS_MAX_PER_FILE:
        fileset_maxchunks = max_chunks(fileset_maxfiles,N_CHUNKS_MAX_PER_FILE)
    else:
        fileset_maxchunks = fileset_maxfiles
    #Change filepaths to use chosen XRootD server
    fileset_ready = {}
    for dset in fileset_maxchunks:
        dataset_ready = {}
        for key, val in fileset_maxchunks[dset].items():
            if key != 'files':
                dataset_ready[key] = val
            else:
                files_info = {}
                for fkey, fval in val.items():
                    fparts = fkey.split('/store')
                    if len(fparts) != 2:
                        raise ValueError(f"Filepath {fkey} in dataset {dset} does not fit pattern (splittable on '/store'")
                    xfname = '/store'.join([xrd_base,fparts[-1]])
                    files_info[xfname] = fval
                dataset_ready[key] = files_info
        fileset_ready[dset] = dataset_ready
    
    client = get_client()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rep_fname = f"reports/{XRD_CHOICE.replace('.','_')}/{htc_label}_{MAX_WORKERS}_{N_FILES_MAX_PER_SAMPLE}_{N_CHUNKS_MAX_PER_FILE}"
    with client, performance_report(filename=f"{rep_fname}.html"):
        print("Starting clock")
        t0 = time.monotonic()
        #Run across the fileset (if set up correctly, a lazy dask operation)
        outputs, reports = apply_to_fileset(TtbarAnalysis(),fileset_ready,uproot_options={"allow_read_errors_with_report": True, "skipbadfiles": True, "timeout": utils.config["benchmarking"]["TIMEOUT"]})
        #Actually compute the outputs
        print('About to compute signal outputs')
        coutputs, creports = dask.compute(outputs,reports)
        print('Finished computing signal outputs')

    exec_time = time.monotonic() - t0

    if utils.config["benchmarking"]["USE_HTC"]:
        client.shutdown()
    
    print(f"\nexecution took {exec_time:.2f} seconds")
    creports["TotalTime"] = exec_time

    with open(f"{rep_fname}.pkl", "wb") as f:
        pickle.dump(creports,f)

    print(f"Wrote HTML and pkl reports to {rep_fname} (.html and .pkl, respectively)")

if __name__ == "__main__":
    main()