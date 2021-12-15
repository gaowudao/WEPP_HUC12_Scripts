from prep_DF_comp.clip_GDS_files import clip_GDS
from prep_wepp_inputs.CMIP5_to_CLI.Generate_calibrated_cli_files import gen_cli_file
from prep_DF_comp.hillslope_subset_sel import select_subset_hs
from prep_wepp_inputs.Assign_Cli_Files import assign_cli_files
from Run_WEPP_Hillslopes import run_wepp

def run_comp_prep(HUC12_path, subset_ID, years, obs_cli_xlsx, HUC12_name, LOCA_labs, BCCA_labs, hillslopes, hill_nums):
    '''
    Sets up input data for subset of WEPP hillslopes, runs the model for them,
    and then compares the runoff and erosion outputs to observed data from the 
    Discovery Farms Project (Minnesota Dept. of Agriculture)

    HUC12_path = path to main watershed directory

    subset_ID = ID to find folders in GDS, uncal, and par paths. Folders should have labels
    of 'dwnsc_type + subset_ID'

    years = subset of years that are being modeled in cligen and WEPP

    obs_cli_xlsx = observed climate data from MnDNR that only contains data for the subset of years

    HUC12_name = ID for watershed

    man,LOCA,BCCA + _labs = list of management and climate scenario labels as strings

    periods = list of time periods as integers 
    '''

    def create_subset_cli(dwnsc_type):
        '''
        Creates fully generated .cli files for subset of years

        dwnsc_type = downscaling method for CMIP5 data (BCCA or LOCA)
        '''
        #Define paths to GDS, PAR, uncalibrated, and observed directories, and
        #climate model IDs 
        GDS_path_source = str(HUC12_path + '/GDS/{}/'.format(dwnsc_type))
        GDS_path_subset = str(HUC12_path + '/GDS/{}/'.format(str(dwnsc_type + subset_ID)))
        uncal_path = str(HUC12_path + '/Uncalibrated/{}/'.format(dwnsc_type + subset_ID))
        obs_path = str(HUC12_path + '/obs_data/{}'.format(obs_cli_xlsx))
        par_path = str(HUC12_path + '/PAR/{}/'.format(dwnsc_type + subset_ID))

        #Use cli_GDS to create new GDS files that only include years that match the obs data
        clip_GDS(GDS_path_source, GDS_path_subset, '19', years)

        #generate fully calibrated .cli files with the clipped GDS files. No future .cli files are 
        #present so set 'future' variable to False
        gen_cli_file(GDS_path_subset, HUC12_name, uncal_path, obs_path, '19', '59', par_path, False)

    #Run create_subset_cli
    create_subset_cli('BCCA')
    create_subset_cli('LOCA')


    #Set up paths to the base runs directory (includes soil, slope, and management 
    #files as well as the parent directory for all model runs (Run_dir)
    base_runs_dir = str(HUC12_path + 'Runs/wepp/runs/')
    Run_dir = str(HUC12_path + 'Runs/')

    #Combine LOCA and BCCA model labs into one list for prep_input_files
    model_labs = []
    for mod in LOCA_labs:
        model_labs.append(mod)

    for mod in BCCA_labs:
        model_labs.append(mod)

    #move subset of hillslopes
    select_subset_hs(model_labs, base_runs_dir, Run_dir, hillslopes)


    #Set path to LOCA and BCCA .cli files
    LOCA_cli_path = str(HUC12_path + '/PAR/LOCA{}/'.format(subset_ID))
    BCCA_cli_path = str(HUC12_path + '/PAR/BCCA{}/'.format(subset_ID))

    #set path to the excel file that contains the coordinate points for each hillslope
    hill_coords = str(HUC12_path + 'hillslope_coords.xlsx')

    #Run assign_cli_files for each downscaling method
    assign_cli_files(hill_coords, LOCA_cli_path, Run_dir, LOCA_labs, 'DF_Comp/', [], '19', HUC12_name, hill_nums)
    assign_cli_files(hill_coords, BCCA_cli_path, Run_dir, BCCA_labs, 'DF_Comp/', [], '19', HUC12_name, hill_nums)


#Define path to HUC12 watershed directory and subset of years 
HUC12_path = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/BE1/'
years = ['12','13','14','15','16']
LOCA_labs = ['L1','L2','L3','L4','L5','L6']
BCCA_labs = ['B1','B2','B3','B4','B5','B6']
hillslopes = ['p157', 'p221']
hill_nums = [157, 221]

run_comp_prep(HUC12_path, '_sub', years, 'BE1_MnDNR_Obs_1216.xlsx', 'BE1', LOCA_labs, BCCA_labs, hillslopes, hill_nums)

#Define path to wepppy windows bootstrap scripts directory
wepppy_win_dir = 'C:/Users/Garner/Soil_Erosion_Project/wepppy-win-bootstrap-master/scripts'

model_labs = ['L1','L2','L3','L4','L5','L6',\
              'B1','B2','B3','B4','B5','B6']

scen_dir = str(HUC12_path + 'Runs/DF_comp/')
run_wepp(wepppy_win_dir, scen_dir, model_labs)
