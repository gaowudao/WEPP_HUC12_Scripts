# WEPP_HUC12_Scripts
Repository of python scripts that setup and run the WEPP model for future climates. Fully calibrated climate input files (.cli) are created using functions in the CMIP5_to_CLI subfolder while the input files for soil (.sol), topography (.slp), and management (.man) are prepared and edited with scripts/functions in the prep_wepp_inputs subfolder. Once the input files are prepared and any potential manual edits have been completed, the inputs are sent to the WEPP model via functions in the "RUN_WEPP_Hillslopes" script. The outputs of each run are analyzed and compared to observed data using scripts in the "WEPP_output_analysis" subfolder.

All functions associated with file and directory preparation/editing are called in the 'run_all_prep.py' script. This script should be run first and followed by the RUN_WEPP_Hillslopes.py script. The output data from each run can then be analyzed with scripts in the WEPP_output_analysis sub-folder. 
