from prep_wepp_inputs.CMIP5_to_CLI.download_ftp import extract_netcdf

BE1_ftp_lst = ['202112011135Nr5d_n_VIqkwo', '202112011141Nr5l_n_PB_INf']
DO1_ftp_lst = ['202112011149Nr5d_n_DLYep4', '202112011154Nr5l_n_EMRSgN']
RO1_ftp_lst = ['202112011146Nr5d_n_PDkd1q', '202112011146Nr5l_n_SLtbnG']
ST1_ftp_lst = ['202112011100Nr5d_n_DtgiWu', '202112011054Nr5l_n_FMUb4i']

def netCDF_to_calcli(HUC12_path, ftp_lst, HUC12_name):
    '''
    Combines functions from scripts in CMIP5_to_CLI folder to produce fully calibrated 
    .cli files from the raw netCDF inputs.

    HUC12_path = path to main HUC12 directory (watershed name/ID)

    ftp_lst = list of ftp IDs. The first ID in the list is always for 
    the BCCA downscaling method and the second is for the LOCA method.
    '''
    #Download netCDF files from ftp link for given HUC12_path and pair of ftp IDs
    #The first ID in the list is always for the BCCA downscaling method and the second
    #is for the LOCA method.
    
    extract_netcdf(ftp_lst[0], str(HUC12_path + '/netCDF/BCCA/'), HUC12_name)
    extract_netcdf(ftp_lst[1], str(HUC12_path + '/netCDF/LOCA/'), HUC12_name)

netCDF_to_calcli('C:/Users/Garner/Soil_Erosion_Project/WEPP_PRWs/DO1/', DO1_ftp_lst, 'DO1')
