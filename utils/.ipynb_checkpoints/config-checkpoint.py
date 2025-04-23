config = {
    "global": {
        # ServiceX: ignore cache with repeated queries
        "SERVICEX_IGNORE_CACHE": False,
        # analysis facility: currently only set up for "Wisconsin"
        "AF": "Wisconsin",
        # number of bins for standard histograms in processor
        "NUM_BINS": 25,
        # lower end of standard histograms in processor
        "BIN_LOW": 50,
        # upper end of standard histograms in processor
        "BIN_HIGH": 550
    },
    "benchmarking": {
        #Which XRootD server to use
        #For Wisconsin, options are "xcache" for the full server, or
        #"xcache01" - "xcache05" for the individual disks
        "XROOTD_CHOICE": "xcache",
        #If None, there is no max
        "N_FILES_MAX_PER_SAMPLE": 2,
        "N_CHUNKS_MAX_PER_FILE": None,
        #Number of seconds before giving up on file reading
        "TIMEOUT": 300,
        #Number of distributed workers to request
        "MAX_WORKERS": 250,
        # Enable distributed computing
        "USE_HTC": True,
        "AF_NAME": "Wisconsin",
        # currently has no effect
        "SYSTEMATICS": "all",
        # does not do anything, only used for metric gathering (set to 1 for distributed coffea-casa)
        "CORES_PER_WORKER": 1,
        # scaling for local setups with FuturesExecutor
        "NUM_CORES": 4,
        # only I/O, all other processing disabled
        "DISABLE_PROCESSING": False,
        ### read additional branches (only with DISABLE_PROCESSING = True) ###
        # acceptable values are 4.1, 15, 25, 50 (corresponding to % of file read), 4.1% corresponds to the standard branches used in the notebook
        "IO_FILE_PERCENT": "4.1",
        # nanoAOD branches that correspond to different values of IO_FILE_PERCENT
        "IO_BRANCHES": {
            "4.1": [
                "Jet_pt",
                "Jet_eta",
                "Jet_phi",
                "Jet_btagCSVV2",
                "Jet_mass",
                "Muon_pt",
                "Electron_pt",
            ],
            "15": ["LHEPdfWeight", "GenPart_pdgId", "CorrT1METJet_phi"],
            "25": [
                "LHEPdfWeight",
                "GenPart_pt",
                "GenPart_eta",
                "GenPart_pdgId",
                "LHEScaleWeight",
            ],
            "50": [
                "LHEPdfWeight",
                "GenPart_pt",
                "GenPart_eta",
                "GenPart_phi",
                "GenPart_pdgId",
                "GenPart_genPartIdxMother",
                "GenPart_statusFlags",
                "GenPart_mass",
                "LHEScaleWeight",
                "GenJet_pt",
                "GenPart_status",
                "LHEPart_eta",
                "LHEPart_phi",
                "LHEPart_pt",
                "GenJet_eta",
                "GenJet_phi",
                "Jet_eta",
                "Jet_phi",
                "SoftActivityJet_pt",
                "SoftActivityJet_phi",
                "SoftActivityJet_eta",
                "GenJet_mass",
                "Jet_pt",
                "Jet_mass",
                "LHEPart_mass",
                "Jet_qgl",
                "Jet_muonSubtrFactor",
                "Jet_puIdDisc",
            ],
        },
    },
    "preservation": {
        "HEPData": False
    }
}