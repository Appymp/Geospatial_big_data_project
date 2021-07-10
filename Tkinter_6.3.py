# -*- coding: utf-8 -*-
"""
Created on Wed May 7 10:00 2021

@author: Appanna
"""
#Version 6 Notes.Integrate training and export with Version_2.

"""
May 28th:
    - Running prediction for scale 10 to verify scale of Yassine's export. 
    Maybe 10 instead of 20.

May 27th:
   - Attempting to aggregate the pixels in the shape file with a classification
   based on the number of irr Vs non irr. Zonal_statistics.
   


"""

"""
lAST Week highlights
    - Done.Zone_pred geom geojson.Downloaded directly from : https://france-geojson.gregoiredavid.fr/
    - Optimize global variables to only the relevant ones.
    - Wrong Obs."Reference" can be same as 'Full scope geom'. Since it is used only for bounding the instantiation of Sentinel series.
        But this has to cover prediction zone too. Maybe can define full scope and anyway this will be clipped to tr and pr zones.
    - Wrong Obs. Spain map does not work. Edit previously stated comment.
    - Prediction zone upload.
    - Include entry box to paste Earth engine authentication. Else will not export.
    - Done. Error message for Training Export Fail.
    
    Optimizations:
    - Timer for prog bars
    - If prog bar closed, connect back to status of current job.
    - Multiple file exports. Display number of current jobs with status of each.                                                    
"""


""" Wishlist
Wish list:
    - Clear varibles before start of program. Issues encountered. Mainly Training module variables should be cleared.
    - default text for training zone.Done.
    - algorithm training buttons
    - scale and points entry.
    - export scale.default 30. Affects resolution of export image.
    - Folium takes Geojson i/p and displays in web page.
    - Folium to choose prediction zone.
Optimization phase:
    - Styles of buttons, colors
    - Maybe add buttons
"""



from tkinter import * #From tkinter import everything
from tkinter import filedialog
from tkinter import ttk
import time
import threading

import geemap
import ee
import folium

#Reference: https://www.youtube.com/watch?v=D8-snVfekto
import tkinter as tk




##Initialise earth engine
#ee.Authenticate() # Trigger the authentication flow.
ee.Initialize() # Initialize the library. 




#Define the size of the interface window
HEIGHT = 700
WIDTH= 800

window = tk.Tk() #create Window Object
window.title("Interface for Irrigation prediction")


canvas= tk.Canvas(window, height=HEIGHT, width=WIDTH) #Define the size of the window
canvas.pack()

frame = tk.Frame(window, bg='black')
#frame.place(relx=0.1,rely=0.1,relwidth=0.8,relheight=0.8) #To adjust frame within the window
frame.place(relwidth=1,relheight=1)


#####################################TRAINING THE MODEL##########################################



label_tr=Label(frame,text="TRAINING THE MODEL",bg='white')
label_tr.place(relx=0,rely=0.05,relwidth=1,relheight=0.075, )


#######################Labelled data upload########################
v = StringVar(frame, value='users/mpappanna/Urgell_2020_0_1')
e=Entry(frame, textvariable=v)
e.place(relx=0.275,rely=0.15,relwidth=0.225,relheight=0.1, )#place the box 0.025+0.25=0.275 away from button 
e.configure(font=( "Courier", 8, "italic"))

def sigpac_upload(event=None):
    properties= ['SR_2']
    table_id = e.get()
    sc = ee.FeatureCollection(table_id).reduceToImage(properties, ee.Reducer.first())
    sc1 = ee.FeatureCollection(table_id).select(properties)
   
    global sigpac,sigpac1 #variables which are called in other functions have be declared as global variables
    sigpac=sc
    sigpac1=sc1
    print("Labelled dataset uploaded: ",table_id)
    
button_1 =tk.Button(frame,text="Labelled data upload", command=sigpac_upload)
button_1.place(relx=0.05,rely=0.15,relwidth=0.2,relheight=0.1) #relx ends at 0.25


#######################Full scope geometry d########################
#Upload full scope geometry of the labelled dataset
#set filename_fsg with default parcel
def fsg(event=None):
    filename_fsg = filedialog.askopenfilename(title="Select a file", filetypes=[("GeoJSON files","*.geojson")])
    only_file=filename_fsg.split('/')[-1]
    print("Full scope file: ", only_file)    
    label_1v2=Label(frame,text=only_file,bg='white')
    label_1v2.place(relx=0.8,rely=0.15,relwidth=0.175,relheight=0.1 )#prev box ends at 0.75 relx.
    
    if filename_fsg: # If file upload is cancelled, 'parcel' will not be defined.
        #with open(filename_fsg) as f:
        parcel_geom = geemap.geojson_to_ee(filename_fsg) #feature collection
        parcel_geom1= parcel_geom.geometry() # geometry
        global parcel
        parcel=parcel_geom1
    else:
        if 'parcel' in globals():
            del globals()['parcel']
            print("Full scope geometry file upload cancelled")


filename_fsg=""
label_1v2=Label(frame,text=filename_fsg,bg='white')
label_1v2.place(relx=0.8,rely=0.15,relwidth=0.175,relheight=0.1 )

button_1v2 =tk.Button(frame,text="Full scope geometry", command=fsg)
button_1v2.place(relx=0.55,rely=0.15,relwidth=0.2,relheight=0.1) #prev box ends at 0.5 relx.



#########################Training Zone Upload#######################
def train_zone(event=None):
    
    if not('sigpac1' in globals()):
        tk.messagebox.showinfo(title="Error", message="Upload labelled data first")
        print("Execution halted. Labelled data has not been uploaded.")
        
    elif not('parcel' in globals()):
        tk.messagebox.showinfo(title="Error", message="Upload full scope geometry")
        print("Execution halted. Full scope geometry has not been uploaded.")
    
    
    else:
        filename = filedialog.askopenfilename(title="Select a file", filetypes=[("GeoJSON files","*.geojson")])
        #print('Selected:', filename)
        label_2=Label(frame,text=filename,bg='white')
        label_2.place(relx=0.35,rely=0.31,relwidth=0.55,relheight=0.1, )
       
        if filename != "":
           ###GEE_block_start_1###
            ee_object_in = geemap.geojson_to_ee(filename)
            #Limit the sigpac data geometry to the train_zone
            roi=ee_object_in #feature collection
            sigpac_trz=sigpac1.filterBounds(roi) #define boundary for sigpac image
            
            ft0 =ee.FeatureCollection(sigpac_trz).filter("SR_2 == 0")
            ft100 =ee.FeatureCollection(sigpac_trz).filter("SR_2 == 1")
            global sigpac_trzone,filtered0,filtered100
            sigpac_trzone=sigpac_trz
            filtered0=ft0
            filtered100=ft100
            ###GEE_block_end_1###
            #filename=""
            
        ##If training zone upload is cancelled, remove global var which triggers training model flow for fixed scope.
        elif not filename: #cancel button makes the filename False, and not "null"
            if 'sigpac_trzone' in globals():
                del globals()['sigpac_trzone']
                print("Training zone geometry file upload cancelled.")
  
    
label_2=Label(frame,text=" ",bg='white')
label_2.place(relx=0.35,rely=0.31,relwidth=0.55,relheight=0.1, )

button_2 =tk.Button(frame,text="Training zone upload", command=train_zone)
button_2.place(relx=0.05,rely=0.31,relwidth=0.2,relheight=0.1)




######################Train the model##############################
import ast
with open('reference.geojson') as f:
    reference_geom = ast.literal_eval(f.read()) #Use literal eval so that list is read correctly from text file
    ref_coords = reference_geom['features'][0]['geometry']['coordinates']
reference =ee.Geometry.Polygon(ref_coords)
    


def train_model(event=None):
    #If labelled dataset not upload, throw error message
    if not('sigpac1' in globals()):
        tk.messagebox.showinfo(title="Error", message="Upload labelled data first")
        print("Execution halted. Labelled data has not been uploaded.")
    
    #If full scope geometry not uploaded, throw error message    
    elif not('parcel' in globals()):
        tk.messagebox.showinfo(title="Error", message="Upload full scope geometry")
        print("Execution halted. Full scope geometry has not been uploaded.")
    
    #If Training zone not uploaded, initialise default full scope of labelled dataset
    elif not('sigpac_trzone' in globals()):    
        sigpac_trz=sigpac1 #initialise zone to full scope of uploaded dataset.
        ft0 =ee.FeatureCollection(sigpac_trz).filter("SR_2 == 0")
        ft100 =ee.FeatureCollection(sigpac_trz).filter("SR_2 == 1")
        
        #Complete zone of dataset considered
        label_2=Label(frame,text="Full scope of labelled dataset considered",bg='white')
        label_2.place(relx=0.35,rely=0.31,relwidth=0.55,relheight=0.1, )
        
        global sigpac_trzone,filtered0,filtered100
        sigpac_trzone=sigpac_trz
        filtered0=ft0
        filtered100=ft100
       
        window.update_idletasks() #display "full scope.." comment in interface before training func completes.
        print("Training zone geometry not uploaded. Full scope considered.")
   
    ##Execute training block only if all variables are initialised 
    try:
        gvars = ['sigpac1','sigpac_trzone','parcel']
        if set(gvars).issubset(globals()):
            
            ##Progress bar start. Ref: https://stackoverflow.com/questions/16400533/why-ttk-progressbar-appears-after-process-in-tkinter
            start_progbar_thread() # function which is defined in main. 
    
            #GEE_block_start_2##
            #Train the model

            global image_series #use later for prediction also
            image_series = ee.ImageCollection('COPERNICUS/S1_GRD').filterBounds(reference).filterDate('2017-03-01', '2019-03-01')\
                    .filter(ee.Filter.eq('instrumentMode', 'IW'))\
                    .select('VH','VV') #filtered by 'reference' in backend. Replaced with parcel
                    
            vis_params = {
                'min': -50,
                'max': 1,
                'bands': ['VH','VV']
            }
            image_mean= ee.Image(image_series.reduce(ee.Reducer.mean())).clipToCollection(sigpac_trzone)
            image_variance = ee.Image(image_series.reduce(ee.Reducer.variance())).clipToCollection(sigpac_trzone)
            #image_corr=ee.Image(image_series.reduce(ee.Reducer.pearsonsCorrelation())).clipToCollection(sigpac_trzone)
            vis_params_m = {
                'bands': ['VH_mean','VV_mean']
            }
            vis_params_v = {
                'bands': ['VH_variance','VV_variance']
            }
            
        
            All_sent=image_mean.addBands(image_variance,['VH_variance','VV_variance'])
            #All_sent1= All_sent.addBands(image_corr,['correlation','p-value'])
            All_sent1=All_sent  #do not consider the correlation and p value
            
            global All_sentinel, All_sentinel1, bands, pts_k
            All_sentinel=All_sent
            All_sentinel1=All_sent1
            ##GEE_block_end_2##
            
            ##GEE_block_start_3##
            #Train SVm and get accuracy
            # Use these bands for prediction.
            
            sigpac_cp=sigpac.clipToCollection(sigpac_trzone) #in place of sigpac(image) in the 'points'. Clip to geometry of sigpac_trzone.
            
            # # Make the training dataset.
            pts = 20000 #Set number of pixels in variable. Ref for pred export image name
            pts_k = str(pts)[:-3]+'k' #To get 'k' value. Example 20k points
            #print(pts_k)
            
            points = sigpac_cp.sample(**{
                'region':parcel,
                'scale': 30,
                'numPixels': pts, #pts change to 20k from 9k
                'seed': 0,
                'geometries': True,  # Set this to False to ignore geometries      
            })
                    
            
            bands = ['VV_mean','VH_variance','VH_mean','VV_variance']
            # bands = ['VV_mean','VH_variance','VH_mean','correlation']
            
            # This property of the table stores the SR labels.
            label ='first'
            
            # Overlay the points on the imagery to get training.
            
            training = All_sentinel1.select(bands).sampleRegions(**{
              'collection': points,
              'properties': [label],
              'scale':30 #brought down from 100
            })
            
            # Train a SVM classifier .
            # classifier = ee.Classifier.libsvm(**{
            #   'kernelType': 'RBF',
            #   'gamma': 0.5,
            #   'cost': 10
            # });
            
            #Train a random forest classifier
            trained = ee.Classifier.smileRandomForest(10).train(training,label,bands);
            ##GEE_block_end_3##
            
            
            
            ##GEE_block_start_4##
            # Classify the image with the same bands used for training.
            resul = All_sentinel1.select(bands).classify(trained)
            resul1=ee.Image(resul.reduce(ee.Reducer.mean()))
            
            ##accuracy
            sample = training.randomColumn()
            split = 0.7
            training1 = sample.filter(ee.Filter.lt('random', split))
            validation = sample.filter(ee.Filter.gte('random', split))
            ##
            
            train_accuracy = trained.confusionMatrix()
            validated = validation.classify(trained)
            test_accuracy = validated.errorMatrix('first', 'classification')
            acc=test_accuracy.accuracy().getInfo()
            acc=acc*100
            acc=round(acc,2)
            acc=str(acc)
            
            global accur, result,result1, trained_g
            accur=acc
            accmess= "Model accuracy: "+accur+"%"
            result=resul
            result1=resul1
            trained_g=trained
            
            label_3=Label(frame, text=accmess, bg='white')
            label_3.place(relx=0.25,rely=0.47,relwidth=0.20,relheight=0.1)
            ##GEE_block_end_4##
            
            #Stop the progress bar
            stop_progbar_thread()
            
            #Console comments
            print("Model trained with an acuuracy of : ",accur,"%")
        
    except Exception as e:
        mess_zone_error= str(e) + "\nCheck uploaded full scope geometry."
        tk.messagebox.showinfo(title="Error", message=mess_zone_error) #print error in message box
        print("Error occurred in training: ",e)
        popup.destroy() #destroy the progressbar popup 
            
##Functions for progress bar should be defined in main        
def start_progbar_thread():
    global progressbar, popup, timelabel, tasktime,x
    popup=tk.Toplevel() 
    popup.wm_title("Training in progress")
    popup.geometry('500x100')
    progressbar = ttk.Progressbar(popup, orient=HORIZONTAL, length=400, mode='indeterminate')
    
    progressbar.pack()
    progressbar.start(10)
    
#     tasktime= StringVar()
#     timelabel = Label(popup,textvariable=tasktime).pack()
#     popup.update_idletasks()
 
    
# def update_time():  
#     x+=1
#     tasktime.set(x)
#     popup.update_idletasks()
    

def stop_progbar_thread():
    progressbar.stop()
    popup.destroy()



#Create a new thread for the training function so that progress bar can run in main. Use lambda so that waits for button press before starting thread.
button_3 =tk.Button(frame,text="Train the model", command=lambda: threading.Thread(target=train_model).start())
button_3.place(relx=0.05,rely=0.47,relwidth=0.175,relheight=0.1)

label_3=Label(frame,text="Accuracy",bg='white')
label_3.place(relx=0.25,rely=0.47,relwidth=0.20,relheight=0.1)
label_3.configure(font=( "Courier", 8, "italic"))








###################Export training#################
# label_4=Label(frame,text=" ",bg='white')
# label_4.place(relx=0.35,rely=0.53,relwidth=0.55,relheight=0.1, )

##Slider for scale display and selection
w1 = Scale(frame, from_=5, to=30, tickinterval=5, orient=HORIZONTAL)
w1.set(30)
w1.place(relx=0.775,rely=0.47,relwidth=0.175,relheight=0.1) # relx at 0.025 away from button

button_4 =tk.Button(frame,text="Set Scale and Export training", command=lambda: threading.Thread(target=trexport).start())
button_4.place(relx=0.55,rely=0.47,relwidth=0.2,relheight=0.1)




def trexport():
    #If labelled dataset not upload, throw error message
    if not('sigpac1' in globals()):
        tk.messagebox.showinfo(title="Error", message="Upload labelled data first")
        print("Execution halted. Labelled data has not been uploaded.")
    
    #If full scope geometry not uploaded, throw error message    
    elif not('parcel' in globals()):
        tk.messagebox.showinfo(title="Error", message="Upload full scope geometry")
        print("Execution halted. Full scope geometry has not been uploaded.")
    
    #If training not done, throw error message    
    elif not('result1' in globals()):
        tk.messagebox.showinfo(title="Error", message="Train the model first")
        print("Execution halted. Model has to be trained first.")
    
    else:   
        global ef, popup_filename, sc, landcover
        class_values=[0,1]
        class_palette=['000000','111BEE']
        landcover = result.set('classification_class_values', class_values)
        landcover = landcover.set('classification_class_palette', class_palette) 
        
        ##Filename entry box popup
        sc=w1.get() #get scale value
        popup_filename=tk.Toplevel()
        popup_filename.geometry('200x100')
        popup_filename.wm_title("Filename")
        
        label_fn=Label(popup_filename,text="Enter the filename:")
        label_fn.pack()
        ef=tk.Entry(popup_filename)
        ef.pack(ipady=10)
        
        button_ok =tk.Button(popup_filename,text="OK", command=cont_exp)
        button_ok.pack()
        
   
    
def cont_exp():
    fn=ef.get()
    print("Filename entered : ", fn)
    popup_filename.destroy() #Destroy the popup box
    

    exp_filename = fn+'_train_px_'+pts_k+'_sc_'+str(sc) 
    print("Resulting export filename: ", exp_filename)
    
    global task
    task= ee.batch.Export.image.toDrive(image=landcover,  # an ee.Image object.
                                     region=parcel,  # an ee.Geometry object.
                                     description='OKP4_Project_ul',
                                     fileFormat='GeoTIFF',
                                     folder='OKP4_Irrigation_tool',
                                     fileNamePrefix=exp_filename, # Set name of the file
                                     scale=sc, #pass the scale value 
                                     maxPixels=10000000000, #For spain_act,10 zeroes
                                     crs='EPSG:4326')
    task.start()
    start_progbar_export()
    
    
text_mess=StringVar()
text_mess.set("Start")
def start_progbar_export():
    global progressbar1, popup1
    popup1=tk.Toplevel() 
    popup1.wm_title("Export in progress")
    popup1.geometry('500x100')
    progressbar1 = ttk.Progressbar(popup1, orient=HORIZONTAL, length=400, mode='indeterminate')
    
    progressbar1.pack()
    progressbar1.start(10) #progress bar indeterminately increases 10 steps
    Disp = Label(popup1,textvariable=text_mess).pack()
    popup1.update_idletasks()
    
    #time.sleep(10)
    check_status_export()
    
    
def check_status_export():
    print(task.status())
   # while task.status()['state']!='COMPLETED':
       
    if task.status()['state']=='READY':
        text_mess.set("READY")
        popup1.update_idletasks()
        popup1.after(10000, check_status_export)
        
    elif task.status()['state']=='RUNNING':
        text_mess.set("RUNNING")
        popup1.update_idletasks()
        popup1.after(10000, check_status_export)
    
    elif task.status()['state']=='FAILED':
        fail_err_mess=task.status()['error_message']
        tk.messagebox.showinfo(title="Error", message=fail_err_mess)
        print("Execution halted. Check error message: ", fail_err_mess )
        
        progressbar1.stop()
        popup1.destroy()
        
    elif task.status()['state']=='COMPLETED':        
        text_mess.set("COMPLETED")
        popup1.update_idletasks()
        progressbar1.stop()
        time.sleep(5)
        popup1.destroy()
        
        #import sys
        #sys.exit() #exit program
        

# Radiobutton(frame,text="points",variable=g)


################################PREDICTION##################################
label_pr=Label(frame,text="PREDICTION",bg='white')
label_pr.place(relx=0,rely=0.59,relwidth=1,relheight=0.075, )


######################Prediction Zone Upload####################

def psg(event=None): #prediction zone geometry

    #If training not done, throw error message    
    if not('result1' in globals()):
        tk.messagebox.showinfo(title="Error", message="Train the model first")
        print("Execution halted. Model has to be trained first.")
        
    else:
        try:
            filename_psg = filedialog.askopenfilename(title="Select a file", filetypes=[("GeoJSON files","*.geojson")])
            only_file_psg=filename_psg.split('/')[-1]
                
            label_5=Label(frame,text=only_file_psg,bg='white')
            label_5.place(relx=0.35,rely=0.69,relwidth=0.55,relheight=0.1)#prev box ends at 0.75 relx.
            
            if filename_psg: # If file upload is cancelled, 'landcover_pred' will not be defined.
                #with open(filename_psg) as f:
                print("Prediction zone upload: ", only_file_psg)
                pred_zone = geemap.geojson_to_ee(filename_psg) #feature collection
                pred_zone_geom= pred_zone.geometry() # geometry
                
                global zone_pred, zone_pred_geom, zone_pred_img, result_pred, landcover_pred
                zone_pred = pred_zone
                zone_pred_geom = pred_zone_geom
                
                
                image_mean1= ee.Image(image_series.reduce(ee.Reducer.mean()))
                image_variance1 = ee.Image(image_series.reduce(ee.Reducer.variance()))
                All_sentinel_pred=image_mean1.addBands(image_variance1,['VH_variance','VV_variance'])
                #All_sentinel1_pred= All_sentinel_pred.addBands(image_corr1,['correlation','p-value'])
                All_sentinel1_pred= All_sentinel_pred
                
                zone_pred_img=All_sentinel1_pred.clipToCollection(zone_pred)
                result_pred=zone_pred_img.select(bands).classify(trained_g)
                
                class_values=[0,1] #Explicitly defined vars here to allow for standalone predicition based on preloaded weight, w/o executing "training export" 
                class_palette=['000000','111BEE'] #Explicitly defined again
                landcover_pred = result_pred.set('classification_class_values', class_values)
                landcover_pred = landcover_pred.set('classification_class_palette', class_palette)
                print("Prediction zone classification complete.")
                
            else:
                if 'landcover_pred' in globals():
                    del globals()['landcover_pred']
                    print("Prediction zone geometry file upload cancelled")
        except Exception as e:
            mess_zone_error2= str(e) 
            tk.messagebox.showinfo(title="Error", message=mess_zone_error2) #print error in message box
            print("Error occurred in prediction: ",e)


label_5=Label(frame,text=" ",bg='white')
label_5.place(relx=0.35,rely=0.69,relwidth=0.55,relheight=0.1, )

button_5 =tk.Button(frame,text="Prediction zone upload", command=psg)
button_5.place(relx=0.05,rely=0.69,relwidth=0.2,relheight=0.1)




######################Export Prediction####################


##Slider for scale display and selection
w2 = Scale(frame, from_=5, to=30, tickinterval=5, orient=HORIZONTAL)
w2.set(30)
w2.place(relx=0.3,rely=0.85,relwidth=0.175,relheight=0.1) #prevrelx 0.25

def prexport():
    #If labelled dataset not upload, throw error message
    if not('landcover_pred' in globals()):
        tk.messagebox.showinfo(title="Error", message="Upload prediction zone first")
        print("Execution halted. Prediction zone has not been uploaded.")
    
    
    else:   
        global ef2, popup2_filename,sc2
        ##Filename entry box popup
        sc2=w2.get() #get scale value
        popup2_filename=tk.Toplevel()
        popup2_filename.geometry('200x100')
        popup2_filename.wm_title("Filename")
        
        label_fn2=Label(popup2_filename,text="Enter the filename for prediction:")
        label_fn2.pack()
        ef2=tk.Entry(popup2_filename)
        ef2.pack(ipady=10)
        
        button_ok2 =tk.Button(popup2_filename,text="OK", command=cont_exp2)
        button_ok2.pack()
        
   
    
def cont_exp2():
    fn2=ef2.get()
    print("Filename entered : ", fn2)
    popup2_filename.destroy() #Destroy the popup box

    exp_filename2 = fn2+'_pred_px_'+pts_k+'_sc_'+str(sc2) 
    print("Resulting prediction image export filename: ", exp_filename2)
    
    global task2
    task2= ee.batch.Export.image.toDrive(image=landcover_pred,  # an ee.Image object.
                                     region=zone_pred_geom,  # an ee.Geometry object.
                                     description='OKP4_Project_pred',
                                     fileFormat='GeoTIFF',
                                     folder='OKP4_Irrigation_tool',
                                     fileNamePrefix=exp_filename2, # Set name of the file
                                     scale=sc2, #pass the scale value 
                                     maxPixels=10000000000, #For spain_act,10 zeroes
                                     crs='EPSG:4326')
    task2.start()
    start_progbar_export2()
    
    
text_mess2=StringVar()
text_mess2.set("Start")
def start_progbar_export2():
    global progressbar2, popup2
    popup2=tk.Toplevel() 
    popup2.wm_title("Export in progress")
    popup2.geometry('500x100')
    progressbar2 = ttk.Progressbar(popup2, orient=HORIZONTAL, length=400, mode='indeterminate')
    
    progressbar2.pack()
    progressbar2.start(10) #progress bar indeterminately increases 10 steps
    Disp2 = Label(popup2,textvariable=text_mess2).pack()
    popup2.update_idletasks()
    
    #time.sleep(10)
    check_status_export2()
    
    
def check_status_export2():
    print(task2.status())
   # while task.status()['state']!='COMPLETED':
       
    if task2.status()['state']=='READY':
        text_mess2.set("READY")
        popup2.update_idletasks()
        popup2.after(10000, check_status_export2) #check again after 10,000 milli secs
        
    elif task2.status()['state']=='RUNNING':
        text_mess2.set("RUNNING")
        popup2.update_idletasks()
        popup2.after(10000, check_status_export2)
    
    elif task2.status()['state']=='FAILED':
        fail_err_mess2=task2.status()['error_message']
        tk.messagebox.showinfo(title="Error", message=fail_err_mess2)
        print("Execution halted: ", fail_err_mess2 )
        
        progressbar2.stop()
        popup2.destroy()
        
    elif task2.status()['state']=='COMPLETED':        
        text_mess2.set("COMPLETED")
        popup2.update_idletasks()
        progressbar2.stop()
        time.sleep(5)
        popup2.destroy()
        
        #import sys
        #sys.exit() #exit program


button_6 =tk.Button(frame,text="Export prediction", command=lambda: threading.Thread(target=prexport).start())
button_6.place(relx=0.05,rely=0.85,relwidth=0.2,relheight=0.1)




window.mainloop()