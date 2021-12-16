def select_subset_hs(model_labels, source_dir, Run_dir, hillslopes):
    '''
    Moves a subset of hillslopes from the main scenario directory and copies them
    to a new directory. The files being moved are generally those used in the 
    runoff and soil erosion calibration process.

    model_labels = list of labels for each climate/time period scenario combo
    source_dir = directory where selected files are sourced from
    target_dir = directory where selected files are copied to
    hillslopes = list of hillslope IDs that are being copied over
    '''

    import shutil, os

    #loop through all model labels
    for mod_lab in model_labels:

        #Set path to target directory (subset of larger WEPP hillslopes)
        DEP_DF_dir = str(Run_dir + 'DF_Comp/' + mod_lab + '_19' + '/wepp/' + 'runs/')

        #Set path for output files 
        DEP_DF_out_dir = str(Run_dir + 'DF_Comp/' + mod_lab + '_19' + '/wepp/' + 'output/')
        
        #create DEP_DF_dir and out_dir
        os.makedirs(DEP_DF_dir)
        os.makedirs(DEP_DF_out_dir)

        #loop through all files in input_dir
        for file in os.listdir(source_dir):
            #Only select hillslope input files that are in subset list
            if file[:-4] in hillslopes:
                #define source files and where they are being copied to
                source_file = str(source_dir + file)
                subset_file = str(DEP_DF_dir + file)
                
                #copy selected file to new subset directory
                shutil.copy(source_file,subset_file)

            #repeat for frost and snow files
            if file == 'frost.txt' or file == 'snow.txt':
                source_file = str(source_dir + file)
                subset_file = str(DEP_DF_dir + file)
                shutil.copy(source_file,subset_file)


