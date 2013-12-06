'''Functions for manipulating trajectory files.  Currently
relies on VMD calls through the shell, and as such is dependent on
VMD CML access and living on a UNIX-like system.'''

import NAMDConf
import os

#This function doesn't return anything.
#This is starting to cause me mental anguish to program like this.
#Oh Functional Programming, how I have sacrificed thee at the alter of getting this done on time!

def extract_data(Config, output_name, target = "protein noh", time_cut = 0):
    #NAMDConf will need variable substitution in the parameters 
    step_cut = int(time_cut / Config.stepsize)
    vmd_command_string = " ".join(["vmd"
                                   , "-dispdev"
                                   , "text"
                                   , "-eofexit"
                                   , str(Config.psf_file)
                                   , str(Config.dcd_file)
                                   , "<"
                                   , ".tmp_MSMControl_script.tcl"
                                   , ">"
                                   , "vmdlog.log"])
    try:
        with open(".tmp_MSMControl_script.tcl", "w") as ftmp:
            #Now we make a temporary TCL script for VMD to consume
            ftmp.write("\n".join([
                  "MSMControl generated script for extracting data sets of interest"
                , "set DataSet [atomselect top \""+ target +"\"]"
                , "set start " + str(step_cut)
                , "set nframes [molinfo top get numframes]"
                , #line to write out data
                ]))

    except:
        print("Failed to open .tmp_MSMControl_script.tcl for VMD script generation")
        #Crap, this should probably never happen (that's why it's an exception I suppose)
        #But I'm not sure how this should be handled
        #Returning None seems completely asinine for a completely side-effecting function
        #And then what the fuck do I return on a success?  This isn't fucking C. Argh.
    
