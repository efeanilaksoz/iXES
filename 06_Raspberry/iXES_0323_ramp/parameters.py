from datetime import datetime
import pandas as pd

from gui_functions import *

def get_variables(folder, name):   
    df = pd.read_csv(folder + name)
    amp = str(df['amp']).split(':')
    return df

def update_variable(df, folder, varname, value):
    df[varname] = value
    df.to_csv(folder + '/parameters.csv')

def update_timedate(df, folder):
    ## Test Time Varibles
    time        = 10*60 #secs
    mins, secs  = divmod(time, 60)
    time_show   = '{:02d}:{:02d}'.format(mins, secs)
    date        = datetime.today().strftime('%Y%m%d%H%M%S') 
    date_show   = datetime.today().strftime("%m/%d/%Y, %H:%M:%S")
    df['date'] = date_show
    df.to_csv(folder + '/parameters.csv')





"""
## Stimulation Parameters
Amp          = [50 , 50 , 50 , 50 , 50 , 50 , 50 , 50 ] #mA
Plsw         = [200, 200, 200, 200, 200, 200, 200, 200] #muS
Start_Angle  = [310, 300, 300, 300, 300, 300, 300, 300] #degrees
Range_Angle  = [100 , 80 , 80 , 80 , 80 , 80 , 80 , 80 ] #degrees
Stop_Angle   = [(Start_Angle[0]+Range_Angle[0])%360 , (Start_Angle[1]+Range_Angle[1])%360,
                (Start_Angle[2]+Range_Angle[2])%360 , (Start_Angle[3]+Range_Angle[3])%360,
                (Start_Angle[4]+Range_Angle[4])%360 , (Start_Angle[5]+Range_Angle[5])%360,
                (Start_Angle[6]+Range_Angle[6])%360 , (Start_Angle[7]+Range_Angle[7])%360]
"""

