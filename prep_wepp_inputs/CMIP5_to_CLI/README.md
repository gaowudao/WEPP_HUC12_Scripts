# CMIP5_to_CLI
Repository of python scripts that use downscaled CMIP5 daily climate data to generate calibrated and validated Cligen climates. These scripts work with data from a baseline time period (1965-2019) and two future time periods (2020-2059 and 2060-2099). The calibrated Cligen output files are used as inputs for the Water Erosion Prediction Project Model (WEPP).

CMIP5 data is downloaded from the CMIP5 multi-model ensemble archive in netCDF format from the following website: (https://gdo-dcp.ucllnl.org/downscaled_cmip_projections/dcpInterface.html#Welcome). After the files are requested from the archive, an ftp link and ID can be used to download the selected data (netCDF format) by using the "download_ftp" script which is provided by the archive.

The netCDF files can then be extracted and converted to a GDS format by using the "netCDF_to_GDS" script. A GDS file is a space delimited text file that arranges daily climate data into a specific format that can be read by the GenStPar program. GenStPar generates 12 lines of averaged meteorological/statistical parameters based on the climate data in the GDS file. The corresponding output file type is ".TOP". In order to run GenStPar, it must be in the same directory as the GDS files and the WEPP_CountryCodes file. 

The newly created .TOP files are calibrated and validated using MnDNR observed daily climate datasets in the "Generate_calibrated_cli_files" script. The meteorological and statistical parameters created in the .TOP file are calculated using the observed data, and the newly calculated parameters are substituted into the existing baseline .TOP files. These calibrations are scaled to future time periods by adding the difference between the uncalibrated future and baseline parameters to the calibrated baseline parameters. 

The calibrated .TOP files are identical in format to the top 12 lines of .PAR files which contain more in depth climate and meteorological data. A .TOP file is used to locate existing climate station files that have similar GPS coordinates and climate regimes (existing station files from WEPP GUI databases). Once an existing station is selected, the first 12 lines of that file are overwritten by the .TOP file. After the .Par files are created, they can be sent to the Cligen climate generator program which generates hypothetical climates based on the calibrated CMIP5 data.

These scripts are meant for data generated by the LOCA and BCCAv2 downscaling methods. 