def unpreprocess(fs):
    '''
    Undo preprocessing, converting a preprocessed fileset made for coffea 202X < 2025.5 into a fileset
    suitable for coffea >= 2025.5
    '''
    fs_out = {}
    for dset in fs:
        fnames = []
        for fname in fs[dset]['files']:
            fnames.append(fname)
        fs_out[dset] = fnames
    return fs_out