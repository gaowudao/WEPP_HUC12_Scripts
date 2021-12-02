#!/usr/bin/env python
# coding: utf-8

# In[6]:


def run_ftp_download(ID, output_path):
    """
    Function for downloading subset request results submitted through the 
    Green Data Oasis: Downscaled Climate and Hydrology Projections website 
    (https://gdo-dcp.ucllnl.org/downscaled_cmip_projections/).
    Uses native Python 3 libraries. No external dependencies are required.

    Please provide bug notifications via this form:
    https://gdo-dcp.ucllnl.org/downscaled_cmip_projections/dcpInterface.html#Feedback

    Parameters
    ----------
    s_job_id: string
        Job identifier provided in DCP notification email (sent from no-reply@gdo4.llnl.gov).
        This is the directory on the FTP the data are located within.
    s_local_destination: string
        Destination location for the files to be downloaded to on the local machine.
        Default is the current working directory (i.e. os.getcwd()).

    Returns
    -------
    Path on the local machine where the downloaded files are located.

    Examples
    --------
    Bash terminal example:
        python ./ftp_download.py <s_job_id> [s_local_destination]
        python ./ftp_download.py 202102031234Nl3m_a_J8R3kl DCP_SubsetResults

    PowerShell terminal example:
        python .\ftp_download.py <s_job_id> [s_local_destination]
        python .\ftp_download.py 202102031234Nl3m_a_J8R3kl DCP_SubsetResults

    Python script example:
        from ftp_download import download_dcp_subset_results
        pth_out = download_dcp_subset_results('202102031234Nl3m_a_J8R3kl', 
                                              'DCP_SubsetResults')
    """

    import ftplib
    import os
    import time
    import sys
    import getopt
    import re

    def download_dcp_subset_results(s_job_id, s_local_destination=None):
        """
        Download subset request results submitted through the Green Data Oasis:
        Downscaled Climate and Hydrology Projections website 
        (https://gdo-dcp.ucllnl.org/downscaled_cmip_projections/). Requires 
        the job identifier from the email notification that the request was completed. 
        Wraps _download_files.

        Parameters
        ----------
        s_job_id: str
            Job identifier provided in DCP notification email.
            This is the directory on the FTP the data are located within.
        s_local_destination: str
            Destination location for the files to be downloaded to on the local machine
            Default is the current working directory (i.e. os.getcwd())

        Returns
        -------
        Path on the local machine where files are located

        Examples
        --------
        from ftp_download import download_dcp_subset_results
        pth = download_dcp_subset_results('202102031234Nl3m_a_J8R3kl', 
                                          'DCP_SubsetResults')
        """

        ### Pre-Processing ###
        # Convert local path to abs path
        # Perform a few checks
        s_local_destination = _build_dest_path(s_local_destination)

        # Remove ".job" if passed in job identifier
        s_job_id = s_job_id.rstrip('.job')

        # Check that user-supplied job identifier is reasonable
        if not _check_job_id(s_job_id):
            raise ValueError('Job identifier %s is invalid.' % s_job_id)

        # Create full file path to ftp
        s_input_path = _build_ftp_path(s_job_id)

        # Login to the FTP site
        s_server_address = "gdo-dcp.ucllnl.org"
        ftp = ftplib.FTP(s_server_address)
        ftp.login()
        print('Connected to %s...' % s_server_address)

        # Start download
        print('Downloading files from %s...' % s_input_path)
        _ = _download_files(ftp, s_input_path, s_local_destination)

        # Close connection
        ftp.quit()

        # Notify of completion
        print('Download complete.')

        # Get full file path to where data was downloaded to
        pth = os.path.join(s_local_destination, *s_input_path.split('/')[1:])
        pth = os.path.normpath(pth)

        return(pth)


    def _download_files(ftp, s_input_path, s_destination_path, b_change_dir=False):
        """
        Worker function to download the DCP directory recursively

        Parameters
        ----------
        ftp: ftplib.FTP
            An ftp connection to the server
        s_input_path: str
            Location of the folder on the server without the server name
        s_destination_path: str
            Destination location for the files to be downloaded to on the local machine
        b_change_dir: bool
            Indicates if the worker should move up a directory at the end of the process.
            Default is False.

        Returns
        -------
        None. All files are downloaded to the local machine.

        """

        ### Create the path on the local machine ###
        # Separate out the remote path
        sl_split = s_input_path.split('/')[1:]

        # Make the paths recursively on the local host
        s_path = s_destination_path
        for s_directory in sl_split:
            # Join the current path with the next proposed step
            s_path = os.path.join(s_path, s_directory)

            # Test if the file already exists or is a file
            if not os.path.isdir(s_path) and '.' not in s_path:
                os.mkdir(s_path)

        ### Begin the download from the remote site ###
        # Change to the destination on local machine
        os.chdir(s_destination_path)

        # Navigate to subset results directory
        ftp.cwd(s_input_path)

        # Get the contents of the results directory
        sl_filelist = ftp.nlst()

        # Loop over each entry at the results directory
        for s_file in sl_filelist:
            # Pause momentarily to allow communication
            time.sleep(0.05)

            # Parse the directory entry
            try:
                # Attempt to download the file
                o_file = open(os.path.join(s_path, s_file), "wb")
                ftp.retrbinary("RETR " + s_file, o_file.write)
                print('%s' % s_file)
                o_file.close()

            except:
                # Download attempt failed. It must be a directory.
                # Delete the initial file attempt
                o_file.close()
                os.remove(os.path.join(s_path, s_file))

                # Recursive call into the directory
                _ = _download_files(ftp, s_input_path + '/' + s_file,
                                    s_destination_path, True)

        # Move up one directory to keep the workers in sync
        if b_change_dir:
            ftp.cwd("..")

        return(None)


    def _check_job_id(s_job_id):
        '''
        Cursory verification of user-supplied job identifier
        '''
        pat = re.compile('20[0-9]{10}.+_[a-zA-Z0-9_]{6}$')
        return(pat.match(s_job_id))


    def _build_dest_path(pth):
        '''
        Build destination path on local machine and a few checks
        '''
        if pth:
            # Convert to abs path if not already
            pth = os.path.abspath(pth)

            # Check that destination path exists
            if not os.path.exists(pth):
                raise IOError('%s path does not exist.' % pth)

            # Check that destination path is a directory
            if not os.path.isdir(pth):
                raise IOError('%s exists but is not a directory.' % pth)

        else:
            # Set to current working directory
            pth = os.getcwd()

        return(pth)


    def _build_ftp_path(s_job_id, s_base_path="/pub/dcp/subset"):
        '''
        Build ftp file path
        '''
        # Combine job identifier with ftp path
        pth = os.path.join(s_base_path, s_job_id)

        # Clean path
        pth = os.path.normpath(pth)

        # Change to forward slash for ftp
        pth = pth.replace(os.sep, '/')

        return(pth)


    if __name__ == "__main__":

        # Parse inputs
        args = sys.argv[1:]
        if len(args) == 1:
            s_job_id = args[0]
            s_local_destination = None
        elif len(args) == 2:
            s_job_id = args[0]
            s_local_destination = args[1]
        else:
            sys.stderr.write('Expected 1 or 2 arguments, received %i' % len(args))
            sys.exit(1)

        #############################################################################
        # Call the download processor
        download_dcp_subset_results(ID, output_path)
        
run_ftp_download('202108231014Nl5l_n_Qc3tYr', 'C:\\Users\\Garner\\Soil_Erosion_Project\\GO1_field_test\\climate_files\\LOCA_obs')

