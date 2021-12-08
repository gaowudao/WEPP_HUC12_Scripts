from prep_wepp_inputs.CMIP5_to_CLI.download_ftp import extract_netcdf
from prep_wepp_inputs.CMIP5_to_CLI.netcdf_to_GDS import netcdf_to_GDS


def netCDF_to_calcli(HUC12_path, ftp_ID, HUC12_name, dwnsc_type, num_locs, proj_num,):
    '''
    Combines functions from scripts in CMIP5_to_CLI folder to produce fully calibrated 
    .cli files from the raw netCDF inputs.

    HUC12_path = path to main HUC12 directory (watershed name/ID)

    ftp_ID = ID of ftp download from  The first ID in the list is always for 
    the BCCA downscaling method and the second is for the LOCA method.

    var_cols = column names of variables (bcca and loca have different names)

    proj_names = path to text file with climate projection names

    num_locs = number of modeled areas in netcdf - only need to specify if equal to 1 
    or greater than 1. If greater than 1, input = 2 or any other integer greater than 1. 

    proj_num = number of projections/models in netcdf (same numbering system as num_locs)
    '''

    #Set paths to netcdf and GDS directories and define column labels, model IDs,  
    netcdf_path = str(HUC12_path + '/netCDF/{}/'.format(dwnsc_type))
    GDS_path = str(HUC12_path + '/GDS/{}/'.format(dwnsc_type))
    var_cols = '{}_cols.format(dwnsc_type)'
    model_IDs = str(HUC12_path + 'netcdf/{}_projections_Short.txt'.format(dwnsc_type))
 
    #Run functions to extract netcdf, convert to GDS format, and then generate fully
    #calibrated climate files
    extract_netcdf(ftp_ID, netcdf_path, HUC12_name)
    netcdf_to_GDS(netcdf_path, var_cols, model_IDs, num_locs, proj_num, dwnsc_type, GDS_path)


#Define ftp IDs. First ID in each list is BCCA and second is LOCA
BE1_ftp_lst = ['202112011135Nr5d_n_VIqkwo', '202112011141Nr5l_n_PB_INf']
DO1_ftp_lst = ['202112011149Nr5d_n_DLYep4', '202112011154Nr5l_n_EMRSgN']
RO1_ftp_lst = ['202112011146Nr5d_n_PDkd1q', '202112011146Nr5l_n_SLtbnG']
ST1_ftp_lst = ['202112011100Nr5d_n_DtgiWu', '202112011054Nr5l_n_FMUb4i']

#netCDF extractions come with different column labels for LOCA and BCCA,
#so they must be defined beforehand
LOCA_cols = ['lat', 'lon', 'projection', 'time']
BCCA_cols = ['latitude', 'longitude', 'projection', 'time']

#Define path to HUC12 watershed directory
HUC12_path = 'C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/DO1/'

netCDF_to_calcli(HUC12_path, DO1_ftp_lst[0], 'DO1', 'BCCA')

