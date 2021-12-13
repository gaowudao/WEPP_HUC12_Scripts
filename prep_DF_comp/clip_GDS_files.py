def clip_GDS(source_GDS_dir, new_GDS_dir, period_ID, years):
    '''
    copies specific years from all GDS files in a directory
    and pastes them into a new file. The ID line of the original 
    file is copied to the new file as well. 

    source_GDS_dir = directory with exisiting GDS files

    new_GDS_dir = directory where new GDS files with only 
    a subset of all years will be copied to

    years = list of years (last two digits) that new GDS files
    will contain

    period_ID = ID of time period (19, 59, or 99) included at the 
    end of each files name
    '''
    import os

    #loop through all files in source directory
    for file in os.listdir(source_GDS_dir):
        print(file)
        #select files from wanted time period
        if file.endswith(str(period_ID+'.txt')):
            print(file)

            # open both files
            with open(str(source_GDS_dir + file),'r') as GDS_source, \
                 open(str(new_GDS_dir + file),'w+') as GDS_new:

                # read content from GDS source file
                lines = GDS_source.readlines()

                #write ID line to first line of new GDS file
                GDS_new.write(lines[0])

                # loop through lines
                for line in lines:
                    #copy line to new file if it begins with last two digits
                    #of a selected year
                    if line.startswith(tuple(years)):
                        # append content to second file
                        GDS_new.write(line)