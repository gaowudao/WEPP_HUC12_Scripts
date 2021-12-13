model_labels = ['L1','L2','L3','L4','L5','L6',\
                'B1','B2','B3','B4','B5','B6']
target_dir = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/GO1_DEP/Runs/wepp/runs/'
source_dir = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/GO1_DEP/Runs/wepp/runs/'

DEP_DF_lst = ['p14', 'p26', 'p66', 'p70', 'p374']


def select_subset_hs(model_labels, source_dir, target_dir, hillslopes):
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
        DEP_DF_dir = str(target_dir + mod_lab + '_19' + '/wepp/' + 'runs/')
        
        #loop through all files in input_dir
        for file in os.listdir(source_dir):
            #Only select hillslope input files that are in subset list
            if file[:-4] in hillslopes:
                #define source files and where they are being copied to
                source_file = str(source_dir + file)
                sub_file = str(DEP_DF_dir + file)
                
                #copy selected file to new subset directory
                shutil.copy(source_file,sub_file)

