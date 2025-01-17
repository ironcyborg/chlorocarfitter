def resourcePath(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)



from pickle import FALSE, TRUE
from libplot import ObjPlot
from libcoord import ObjCoord
from libfuncs import parseMD, loadCSV, loadXLSX, saveCSV, saveXLSX, fitterChl, fitterCar, compsAdder, calculatePorraEq, calculateCaffarriEq, calculateFttingError
import tkinter, tkinter.font, tkinter.ttk, tkinter.filedialog
import platform, copy, sys, os, datetime



class MainFrame(tkinter.ttk.Frame):
    
    
    
    def __init__(self, root,  *args, **kwargs):
        
        # inherit from ttk.Frame:
        tkinter.ttk.Frame.__init__(self, root,  *args, **kwargs)
        
        # first create the GUI:
        self.__createGUI()
        
        # load standards:
        self.standards = {
            "chla70": loadCSV(resourcePath("standards/ChA-70-std3.csv"))[0],      
            "chla90": loadCSV(resourcePath("standards/ChA-90-std3.csv"))[0],      
            "chlb70": loadCSV(resourcePath("standards/ChB-70-std3.csv"))[0],       
            "chlb90": loadCSV(resourcePath("standards/ChB-90-std3.csv"))[0],
            "asta80": loadCSV(resourcePath("standards/Asta-80-std3.csv"))[0],      
            "beta80": loadCSV(resourcePath("standards/Beta-80-std3.csv"))[0],     
            "lute80": loadCSV(resourcePath("standards/Lute-80-std3.csv"))[0],    
            "neo80": loadCSV(resourcePath("standards/Neo-80-std3.csv"))[0],     
            "viola80": loadCSV(resourcePath("standards/Viola-80-std3.csv"))[0],  
            "zea80": loadCSV(resourcePath("standards/Zea-80-std3.csv"))[0],     
            "null": loadCSV(resourcePath("standards/Null.csv"))[0],
        }
        # make standards coherent with other datasets:
        for i in self.standards: 
            self.standards[i] = self.standards[i].generateSynthetic(350, 750, 0.1)
        
        # create datasets memory variables:
        self.datasets = []
        self.datasets_backup = []
        self.datasets_filename = "None"
        
        # create plots variable (only p1 at launch):
        self.p1 = ObjPlot(self.frame_canvas, bg= "#ffffff", labelX = "nm", labelY = "au", pixelWidth = 800, pixelHeight = 400)
        self.p1.grid(row=1, column = 1, columnspan=2, sticky="WENS")
        self.p2, self.p3 = None, None
        tkinter.Grid.rowconfigure(self.frame_canvas, 1, weight=1)
        tkinter.Grid.columnconfigure(self.frame_canvas, 1, weight=1)



    def __createGUI(self):
        
        # STYLE (same on all platforms!)
        self.ttk_style = tkinter.ttk.Style()
        self.ttk_style.theme_use("clam")

        # FONT
        if platform.system() == "Windows": 
            tkinter.font.nametofont("TkDefaultFont").config(family= "Verdana", size = 10)
            tkinter.font.nametofont("TkTextFont").config(family= "Verdana", size = 10) # For Comboboxes ecc.
        elif platform.system() == "Linux": 
            tkinter.font.nametofont("TkDefaultFont").config(family= "Helvetica", size = 10)
            tkinter.font.nametofont("TkTextFont").config(family= "Helvetica", size = 10)
        elif platform.system() == "Darwin": # "Darwin" for MacOS
            tkinter.font.nametofont("TkDefaultFont").config(family= "Verdana", size = 12)
            tkinter.font.nametofont("TkTextFont").config(family= "Verdana", size = 12)

        # MAIN DIVISION
        self.frame_controls = tkinter.ttk.Frame(self)
        self.frame_canvas = tkinter.ttk.Frame(self)
        self.frame_controls.pack(side = "left")
        self.frame_canvas.pack(fill = "both", expand = True)

        # "Show manual" button
        self.button_info = tkinter.ttk.Button(self.frame_controls, text ="Show manual",  width = 10, command= self.onInfo)
        self.button_info.grid(row=1, column = 1, columnspan=2, pady=(5,2))

        # "Clear all" button
        self.button_clear = tkinter.ttk.Button(self.frame_controls, text ="Clear all", width = 10, command = self.onClear)
        self.button_clear.grid(row=2, column = 2, padx=(5,10), pady=2)

        # "Load dataset" button
        self.button_load = tkinter.ttk.Button(self.frame_controls, text ="Load dataset", width = 10, command= self.onLoad)
        self.button_load.grid(row=2, column = 1, padx=(10,5), pady=2)

        # First separator 
        self.sep1 = tkinter.ttk.Separator(self.frame_controls, orient="horizontal")
        self.sep1.grid(row=3, column = 1,  columnspan=2, padx=(50,50), pady=5, sticky= "WE")

        # Listbox
        self.frame_file = tkinter.ttk.Frame(self.frame_controls)
        self.scroll_file = tkinter.ttk.Scrollbar(self.frame_file, orient="vertical")
        self.list_file = tkinter.Listbox(self.frame_file, height = 5, selectmode = "multiple", exportselection=False, yscrollcommand= self.scroll_file.set, borderwidth=0)
        self.scroll_file.config(command= self.list_file.yview)
        self.scroll_file.pack(side="right", fill="y")
        self.list_file.pack(side="left", fill="both", expand=1)
        self.frame_file.grid(row=4, column=1, columnspan=2, padx=(10, 10), pady=2, sticky = "WE") 

        # Radios
        self.frame_radio = tkinter.ttk.Frame(self.frame_controls)
        self.manipulation_var = tkinter.StringVar()
        self.manipulation_var.set("nothing")
        self.radio_nothing = tkinter.ttk.Radiobutton(self.frame_radio , text="None", variable= self.manipulation_var, value="nothing", width=9)
        self.radio_nothing.grid(sticky = "W")
        self.radio_720 = tkinter.ttk.Radiobutton(self.frame_radio , text="720zeroing", variable= self.manipulation_var, value="720", width=9)
        self.radio_720.grid(sticky = "W")
        self.radio_720_red = tkinter.ttk.Radiobutton(self.frame_radio, text="720z.+ red", variable= self.manipulation_var, value="720red", width=9)
        self.radio_720_red.grid(sticky = "W")
        self.radio_720.invoke()
        self.frame_radio.grid(row=5, column =1, pady =5, padx=(5,2))
        
        # "Plot selected" button
        self.button_plot = tkinter.ttk.Button(self.frame_controls, text ="Plot selected", width = 10, command= self.onPlot)
        self.button_plot.grid(row=5, column = 2,  padx=(5,10), pady=2)

        # Second separator 
        self.sep2 = tkinter.ttk.Separator(self.frame_controls, orient="horizontal")
        self.sep2.grid(row=6, column = 1,  columnspan=2, padx=(50,50), pady=5, sticky= "WE")

        # Fitting sample Combobox
        self.var_fitter = tkinter.IntVar() 
        self.combo_fitter = tkinter.ttk.Combobox(self.frame_controls, width=5, textvariable= self.var_fitter, state= "readonly")
        self.combo_fitter["values"] = [""]
        self.combo_fitter.current(0) # Fills the combobox with nothing. Otherwise default value on creation is "0".
        self.combo_fitter.grid(row=7, column=1, columnspan=2, padx=(10, 10), pady=2, sticky = "WE")
        
        # Normalization factor
        self.norm_var = tkinter.StringVar()
        self.norm_var.set('1')
        self.norm_label = tkinter.ttk.Label(self.frame_controls, width=5, text="Norm. factor:", anchor="e") # anchor="e" is right-aligned
        self.norm_label.grid(row=8, column=1, padx=(10, 5), pady=2, sticky="WE")
        # validatecommand is a function and returns True if the change is accepted
        # validatecommand is called every time the Entry is modified
        # '%S' means: inserted or deleted char is passed as argument to only_numbers function
        def only_numbers(char):
            return char.isdigit() # Exponents, like ², are also considered to be a digit.
        validation = self.register(only_numbers)
        self.norm_entry = tkinter.ttk.Entry(self.frame_controls, width=5, textvariable=self.norm_var, validate="key", validatecommand=(validation, '%S'))
        self.norm_entry.grid(row=8, column=2, padx=(5, 10), pady=2, sticky="WE")
        
        # Algorithm Combobox
        self.combo_algo = tkinter.ttk.Combobox(self.frame_controls, width=5, state= "readonly")
        self.combo_algo["values"] = ["Caffarri fit", "Porra eq", "Caffarri eq"]
        self.combo_algo.current(0) # Fills the combobox with nothing. Otherwise default value on creation is "0".
        self.combo_algo.bind("<<ComboboxSelected>>", self.__onAlgoChange)
        self.combo_algo.grid(row=9, column=1, padx=(10, 5), pady=2, sticky = "WE")

        # "Fit selected" button
        self.button_fitter = tkinter.ttk.Button(self.frame_controls, text= "Fit selected", width= 10, command= self.onFitting)
        self.button_fitter.grid(row=9, column=2, padx=(5,10), pady=2)

        # Fitting results
        self.frame_results = tkinter.ttk.Frame(self.frame_controls)
        self.scroll_results = tkinter.ttk.Scrollbar(self.frame_results, orient="vertical")
        self.text_results = tkinter.Text(self.frame_results, height=13, width=10, yscrollcommand= self.scroll_results.set, state="disabled")
        self.text_results.configure(font="TkTextFont")
        self.scroll_results.config(command= self.text_results.yview)
        self.scroll_results.pack(side="right", fill="y")
        self.text_results.pack(side="left", fill="both", expand=1)
        self.frame_results.grid(row=10, column = 1, columnspan=2, padx=(10, 10), pady=2, sticky = "WE")
        
        # "Fit all & Save" button
        self.button_save = tkinter.ttk.Button(self.frame_controls, text ="Fit all & Save", width = 10, command = self.onSave)
        self.button_save.grid(row=11, column = 2,  padx=(5,10), pady=(2))
        
        # "Hide details" button
        self.button_hide = tkinter.ttk.Button(self.frame_controls, text ="Hide details", width = 10, command= self.onHide)
        self.button_hide.grid(row=11, column = 1,  padx=(10,5), pady=(2))
        self.button_hide["state"] = "disabled"
        
        # STATUS BAR / PROGRESS BAR
        self.string_status = tkinter.StringVar()
        self.label_status = tkinter.ttk.Label(self.frame_controls,  width=10, textvariable= self.string_status)
        self.label_status.grid(row=12, column=1, columnspan=2, padx=(10,10), pady=(2, 5), sticky= "WE")
        self.string_status.set("Starting up... Ready!")
        self.progress = tkinter.ttk.Progressbar(self.frame_controls, orient = "horizontal", mode = 'determinate')
        self.progress.grid(row=12, column=1, columnspan=2, padx=(10,10), pady=(2, 5), sticky= "WE")
        self.progress["value"] = 70
        self.progress.grid_remove()

        # Checkboxes
        self.checkChla = tkinter.BooleanVar(self.frame_controls, True)
        self.checkChlb = tkinter.BooleanVar(self.frame_controls, True)
        self.checkBeta = tkinter.BooleanVar(self.frame_controls, True)
        self.checkLute = tkinter.BooleanVar(self.frame_controls, True)
        self.checkNeo = tkinter.BooleanVar(self.frame_controls, True)
        self.checkViola = tkinter.BooleanVar(self.frame_controls, True)
        self.checkZea = tkinter.BooleanVar(self.frame_controls, True)
        self.checkAsta = tkinter.BooleanVar(self.frame_controls, False)
        self.checkCantha = tkinter.BooleanVar(self.frame_controls, False)
        self.checkChl_label = tkinter.ttk.Label(self.frame_controls, text="Chlorophylls:", width = 10)
        self.checkChl_label.grid(row=13, column=1, columnspan=2, padx=(10,10), pady=(2, 2), sticky= "WE")
        self.checkbox_Chla = tkinter.Checkbutton(self.frame_controls, text="Chl a", variable=self.checkChla, onvalue = True, offvalue = False, state = tkinter.DISABLED)
        self.checkbox_Chla.grid(row=14, column=1, columnspan=1, padx=(10,10), pady=(2, 2), sticky= "WE")
        self.checkbox_Chlb = tkinter.Checkbutton(self.frame_controls, text="Chl b", variable=self.checkChlb, onvalue = True, offvalue = False)
        self.checkbox_Chlb.grid(row=14, column=2, columnspan=1, padx=(10,10), pady=(2, 2), sticky= "WE")
        self.checkCar_label = tkinter.ttk.Label(self.frame_controls, text="Carotenoids:", width = 10)
        self.checkCar_label.grid(row=15, column=1, columnspan=2, padx=(10,10), pady=(2, 2), sticky= "WE")
        self.checkbox_Beta = tkinter.Checkbutton(self.frame_controls, text="Beta", variable=self.checkBeta, onvalue = True, offvalue = False)
        self.checkbox_Beta.grid(row=16, column=1, columnspan=1, padx=(10,10), pady=(2, 2), sticky= "WE")
        self.checkbox_Lute = tkinter.Checkbutton(self.frame_controls, text="Lute", variable=self.checkLute, onvalue = True, offvalue = False)
        self.checkbox_Lute.grid(row=16, column=2, columnspan=1, padx=(10,10), pady=(2, 2), sticky= "WE")
        self.checkbox_Neo = tkinter.Checkbutton(self.frame_controls, text="Neo", variable=self.checkNeo, onvalue = True, offvalue = False)
        self.checkbox_Neo.grid(row=17, column=1, columnspan=1, padx=(10,10), pady=(2, 2), sticky= "WE")
        self.checkbox_Viola = tkinter.Checkbutton(self.frame_controls, text="Viola", variable=self.checkViola, onvalue = True, offvalue = False)
        self.checkbox_Viola.grid(row=17, column=2, columnspan=1, padx=(10,10), pady=(2, 2), sticky= "WE")
        self.checkbox_Zea = tkinter.Checkbutton(self.frame_controls, text="Zea", variable=self.checkZea, onvalue = True, offvalue = False)
        self.checkbox_Zea.grid(row=18, column=1, columnspan=1, padx=(10,10), pady=(2, 2), sticky= "WE")
        self.checkbox_Asta = tkinter.Checkbutton(self.frame_controls, text="Asta", variable=self.checkAsta, onvalue = True, offvalue = False)
        self.checkbox_Asta.grid(row=18, column=2, columnspan=1, padx=(10,10), pady=(2, 2), sticky= "WE")
        self.checkbox_Cantha = tkinter.Checkbutton(self.frame_controls, text="Cantha", variable=self.checkCantha, onvalue = True, offvalue = False, state = tkinter.DISABLED)
        self.checkbox_Cantha.grid(row=19, column=1, columnspan=2, padx=(10,10), pady=(2, 2), sticky= "WE")

    def onInfo(self):
        
        # Toplevel is for secondary windows
        top = tkinter.Toplevel()
        top.title("About this software...")
        info_top = tkinter.ttk.Frame(top)
        info_top.pack(fill="both", expand=1)
        
        frame_info = tkinter.ttk.Frame(info_top)
        scroll_info = tkinter.ttk.Scrollbar(frame_info, orient="vertical")
        text_info = tkinter.Text(frame_info, height=20, width=70, yscrollcommand=scroll_info.set)
        scroll_info.config(command= text_info.yview)
        scroll_info.pack(side="right", fill="y")
        text_info.pack(side="left", fill="both", expand=1)
        frame_info.pack(fill="both", expand=1, pady=(10,5), padx=(10,10))
        
        text_info.configure(wrap="word")
        
        text_info.configure(state="normal") # Enables the Text widget to be programmatically filled.
        parseMD(text_info, resourcePath("README.md"), top)
        text_info.configure(state="disabled") # Prevent the user to edit the text.

        button = tkinter.ttk.Button(info_top, text="OK", command=top.destroy, width=7)
        button.pack(pady=(5,10))
        
        # lock window dimensions:
        top.update()
        #top.maxsize(top.winfo_width(), top.winfo_height())
        top.minsize(top.winfo_width(), top.winfo_height())
    
    
    
    def onLoad(self):
        
        # my_input will be like "C:/Users/.../folder/file.csv"
        my_input =  tkinter.filedialog.askopenfilename(title = "Load file...")
        if my_input == "": # If the user clicked on "Cancel".
            tkinter.messagebox.showwarning(title="Warning", message="No dataset file selected!")
            return 
        
        if my_input.endswith(".csv") == False and my_input.endswith(".xlsx") == False:
            tkinter.messagebox.showerror(title="Error", message='Dataset file must have ".csv" OR ".xlsx" extension!')
            return
        
        self.onClear()
        
        # get dataset filename
        self.datasets_filename = os.path.splitext(os.path.basename(my_input))[0]
        
        if my_input.endswith(".csv"):
            self.datasets = loadCSV(my_input)
        else:
            self.datasets = loadXLSX(my_input)

        # Interpolation step to make sure all the data is the same beforehand! -> essential for zeroing and normalizing
        for i in range(len(self.datasets)):
            self.datasets[i] = self.datasets[i].generateSynthetic(350, 750, 0.1)
            
            self.progress.grid()
            self.progress['value'] = (i+1)/len(self.datasets)*100
            self.progress.update_idletasks()
        
        # backup datasets
        self.datasets_backup = copy.deepcopy(self.datasets)
        
        # fill the listbox:
        samples_names = []
        for i in self.datasets:
            self.list_file.insert("end", i.label) # "end" means: append the item to the end of the list.
            samples_names.append(i.label)
        
        # fill the combobox:
        self.combo_fitter["values"] = samples_names
        self.combo_fitter.current(0) 
        
        self.progress.grid_remove()
        self.string_status.set("All loaded!")
        
        
        
    def onClear(self):
        
        self.datasets = []
        self.datasets_backup = []
        self.datasets_filename = "None"
        self.list_file.delete(0, "end") # empty the listbox (from 0 to end)
        self.combo_fitter["values"] = [""] # empty the combobox
        self.combo_fitter.current(0) # Fills the combobox with nothing. Otherwise default value on creation is "0".
        self.p1.cleanPlot()
        self.text_results.configure(state="normal") # Enables the Text widget to be programmatically filled.
        self.text_results.delete("1.0", "end")
        self.text_results.configure(state="disabled")
        if (self.p2 != None and self.p3 != None):
            self.p2.cleanPlot()
            self.p3.cleanPlot()
        self.string_status.set("Memory cleared!")
        
    
    
    def doComboManipulations(self, isFitting = False):
        
        if self.manipulation_var.get() == "nothing":
            print("Nothing to do here")
        elif self.manipulation_var.get() == "720":
            self.on720zeroing()
        elif self.manipulation_var.get() == "720red":
            self.on720zeroing()
            if (isFitting == False):
                self.onRedNormalization()
            


    def on720zeroing(self):
        
        for i in range(len(self.datasets)):
            index_to_subtract = self.datasets[i].x.index(720.0) # It will be always 925 since everything is interpolated at 0.1 intervals
            value_to_subtract = self.datasets[i].y[index_to_subtract]
            for k in range(len(self.datasets[i].y)):
                self.datasets[i].y[k] -= value_to_subtract
        
        
    def onRedNormalization(self):
        
        for i in range(len(self.datasets)):
            left_border = self.datasets[i].x.index(600.0)
            right_border = self.datasets[i].x.index(749.9)
            subset_au = self.datasets[i].y[left_border : right_border]
            current_max = max(subset_au)
            for k in range(len(self.datasets[i].y)):
                self.datasets[i].y[k] /= current_max



    def onPlot(self):

        self.onHide()

        if self.datasets_backup == []:
            self.string_status.set("First load samples!")
            return
        
        self.string_status.set("Plotting..."); self.label_status.update_idletasks()
        
        self.datasets = copy.deepcopy(self.datasets_backup)
        self.doComboManipulations()
        
        self.p1.title = ""
        self.p1.subtitle = ""
        self.p1.cleanPlot()
        my_selection = self.list_file.curselection() 
        for i in my_selection:
            self.p1.loadLine(self.datasets[i])
        self.p1.updatePlot()
        self.string_status.set("Plot finished!")
        
        
        
    def __onAlgoChange(self, event):
        
        if self.combo_algo.get() == "Porra eq" or self.combo_algo.get() == "Caffarri eq":
            self.button_fitter["text"] = "Calculate"
        else:
            self.button_fitter["text"] = "Fit selected"
            
            
       
    def onFitting(self):
        
        # if the user didn't any sample yet
        if (self.datasets_backup == []):
            self.string_status.set("First load samples!")
            return
        
        # if Porra eq is selected, exit from onFitting()
        if self.combo_algo.get() == "Porra eq":
            self.onPorraEq()
            return

        # if Caffarri eq is selected, exit from onFitting()
        if self.combo_algo.get() == "Caffarri eq":
            self.onCaffarriEq()
            return
        
        # create p2 and p3 if needed, and activate button_hide
        if (self.p2 == None and self.p3 == None):
            self.p2 = ObjPlot(self.frame_canvas, beginX=350, endX=600, title="Carotenoids fit", bg ="#ffffff", labelX = "nm", labelY = "au", pixelHeight = 300, xTicks = 6, yTicks = 3);
            self.p2.grid(row=2, column = 1, sticky="WENS")
            self.p3 = ObjPlot(self.frame_canvas, beginX=590, endX=700, title="Chlorophylls fit", bg ="#ffffff", labelX = "nm", labelY = "au", pixelHeight = 300, xTicks = 6, yTicks = 3);
            self.p3.grid(row=2, column = 2, sticky="WENS")
                
            tkinter.Grid.rowconfigure(self.frame_canvas, 2, weight=1)
            tkinter.Grid.columnconfigure(self.frame_canvas, 2, weight=1)
            
            self.button_hide["state"] = "active"
        

        self.string_status.set("Fitting..."); self.label_status.update_idletasks()
        

        # take fresh datapoints, but avoid red peak normalization
        self.datasets = copy.deepcopy(self.datasets_backup)
        self.doComboManipulations(isFitting= True) # isFitting=False only when plotting
        
        
        # take the choosen sample
        choosen = self.datasets[self.combo_fitter.current()]
        choosen.changeColor("gray60")
        
        
        # get the normalization factor
        norm = self.norm_var.get()
        if norm == '': self.norm_var.set('1')
        norm = int(self.norm_var.get())

        # get checkboxes value


        # calculate contributions 
        chl_concents, chl_comps = fitterChl(choosen, self.standards, self.combo_algo.get(), self.checkChla.get(), self.checkChlb.get())
        chl_a_conc, chl_a_comp = compsAdder(chl_concents[0:2], chl_comps[0:2], "Chl a fit", color = "SteelBlue4")
        chl_b_conc, chl_b_comp = compsAdder(chl_concents[2:4], chl_comps[2:4], "Chl b fit", color = "green4")
        chl_conc, chl_fit = compsAdder(chl_concents[0:4], chl_comps[0:4], "Chl fit", color = "DarkOliveGreen3")
        car_concents, car_comps = fitterCar(choosen, self.standards, chl_fit, self.combo_algo.get(), self.checkBeta.get(), self.checkLute.get(), self.checkNeo.get(), self.checkViola.get(), self.checkZea.get(), self.checkAsta.get())
        car_conc, car_fit = compsAdder(car_concents[0:6], car_comps[0:6], "Car fit", color = "tomato")
        choosen_subtracted = choosen.subtract(chl_fit, choosen.label + " sub", color = "gray60")
        tot_conc, tot_fit = compsAdder([chl_conc, car_conc], [chl_fit, car_fit], "Total fit", color = "brown")
        

        # calculate the goodness of the fit:
        goodness = calculateFttingError(choosen, tot_fit, self.checkAsta.get())
        goodness_red = goodness[0]
        goodness_blue = goodness[1]


        # clean and fill p1
        self.p1.title = "Total fit"
        self.p1.subtitle = "Fit quality: blue " + str(goodness_blue) +" ; red "+ str(goodness_red)
        self.p1.cleanPlot()
        self.p1.loadLine(choosen)
        self.p1.loadLine(chl_a_comp)
        self.p1.loadLine(chl_b_comp)
        self.p1.loadLine(car_fit)
        self.p1.loadLine(tot_fit)
        self.p1.updatePlot()
        # clean and fill p3
        self.p3.cleanPlot()
        self.p3.loadLine(choosen)
        self.p3.loadLine(chl_a_comp)
        self.p3.loadLine(chl_b_comp)
        self.p3.loadLine(chl_fit)
        for i in range(len(chl_comps)): self.p3.loadLine(chl_comps[i])
        self.p3.updatePlot()
        # clean and fill p2
        self.p2.cleanPlot()
        self.p2.loadLine(choosen_subtracted)
        self.p2.loadLine(car_fit)
        for i in range(len(car_comps)): self.p2.loadLine(car_comps[i])
        self.p2.updatePlot()


        # clean and fill text_results
        self.text_results.configure(state="normal") # Enables the Text widget to be programmatically filled.
        self.text_results.delete("1.0", "end")
        self.text_results.insert("end", choosen.label + " report: \n\n", "norm")
        if self.checkChlb.get():
            self.text_results.insert("end", "Chl", "norm", " a", "chla", "/", "norm", "b: ", "chlb", str(round(chl_a_conc/chl_b_conc, 3)) + "\n", "norm")
        self.text_results.insert("end", "Chl", "chl", "/", "norm", "Car: ", "car", str(round(chl_conc/car_conc, 3)) + "\n", "norm")
        # Raw concentrations
        # self.text_results.insert("end", "Raw concentrations: \n", "raw")
        self.text_results.insert("end", "Chl a [uM]: ", "chla", str(round(chl_a_conc, 3)) + "\n", "norm")
        self.text_results.insert("end", "Chl b [uM]: ", "chlb", str(round(chl_b_conc, 3)) + "\n", "norm")
        self.text_results.insert("end", "Chl [uM]: ", "chl", str(round(chl_conc, 3)) + "\n", "norm")
        self.text_results.insert("end", "Car [uM]: ", "car", str(round(car_conc, 3)) + "\n", "norm")
        for i in range(len(car_comps)): self.text_results.insert("end", car_comps[i].label + " [uM]: ", car_comps[i].color, str(round(car_concents[i], 3)) + "\n", "norm")
        for i in range(len(chl_comps)): self.text_results.insert("end", chl_comps[i].label + " [uM]: ", chl_comps[i].color, str(round(chl_concents[i], 3)) + "\n", "norm")
        # Normalized values
        self.text_results.insert("end", "\nNormalized values: \n\n", "norm")
        self.text_results.insert("end", "Chl a: ", "chla", str(round(norm * chl_a_conc /(chl_a_conc + chl_b_conc), 3)) + "\n", "norm")
        self.text_results.insert("end", "Chl b: ", "chlb", str(round(norm * chl_b_conc /(chl_a_conc + chl_b_conc), 3)) + "\n", "norm")
        self.text_results.insert("end", "Car: ", "car", str(round(norm * car_conc /(chl_a_conc + chl_b_conc), 3)) + "\n", "norm")
        for i in range(len(car_comps)): self.text_results.insert("end", car_comps[i].label + ": ", car_comps[i].color, str(round(norm * car_concents[i] /(chl_a_conc + chl_b_conc), 3)) + "\n")
        
        self.text_results.configure(state= "disabled") # Prevent the user to edit the text.
        # Define style for every tag:
        self.text_results.tag_config('norm', foreground='black')
        self.text_results.tag_config('chla', foreground='SteelBlue4')
        self.text_results.tag_config('chlb', foreground='green4')
        self.text_results.tag_config('chl', foreground='DarkOliveGreen3')
        self.text_results.tag_config('car', foreground='tomato')
        for i in range(len(car_comps)): self.text_results.tag_config(car_comps[i].color, foreground=car_comps[i].color)
        for i in range(len(chl_comps)): self.text_results.tag_config(chl_comps[i].color, foreground=chl_comps[i].color)

        self.string_status.set("Fit finished!")
        
        
        
    def onPorraEq(self):
        
        self.onPlot()
        
        self.datasets = copy.deepcopy(self.datasets_backup)
        self.doComboManipulations(isFitting= True) # isFitting=False only when plotting
        
        self.text_results.configure(state="normal") # Enables the Text widget to be programmatically filled.
        self.text_results.delete("1.0", "end")
        
        choosen = self.datasets[self.combo_fitter.current()]
        self.text_results.insert("end", choosen.label + " report: \n") 
        
        Cchla_ug, Cchlb_ug, Cchla_nmol, Cchlb_nmol = calculatePorraEq(choosen)
        self.text_results.insert("end", "\nWith ug/uL concents:\n\n")
        self.text_results.insert("end", "Chl a/b: " + str(round(Cchla_ug/Cchlb_ug, 3)) + "\n")
        self.text_results.insert("end", "Chl a: " + str(Cchla_ug) + "\n")
        self.text_results.insert("end", "Chl b: " + str(Cchlb_ug) + "\n")
        self.text_results.insert("end", "\nWith nmol/uL concents:\n\n")
        self.text_results.insert("end", "Chl a/b: " + str(round(Cchla_nmol/Cchlb_nmol, 3)) + "\n")
        self.text_results.insert("end", "Chl a: " + str(Cchla_nmol) + "\n")
        self.text_results.insert("end", "Chl b: " + str(Cchlb_nmol) + "\n")
                
        self.text_results.configure(state= "disabled") # Prevent the user to edit the text.
        self.string_status.set("Calcs finished!")
        


    def onCaffarriEq(self):
        
        self.onPlot()
        
        self.datasets = copy.deepcopy(self.datasets_backup)
        self.doComboManipulations(isFitting= True) # isFitting=False only when plotting
        
        self.text_results.configure(state="normal") # Enables the Text widget to be programmatically filled.
        self.text_results.delete("1.0", "end")
        
        choosen = self.datasets[self.combo_fitter.current()]
        self.text_results.insert("end", choosen.label + " report: \n")
        
        Cchla_ug, Cchlb_ug, Cchla_nmol, Cchlb_nmol = calculateCaffarriEq(choosen)
        self.text_results.insert("end", "\nWith ug/uL concents:\n\n")
        self.text_results.insert("end", "Chl a/b: " + str(round(Cchla_ug/Cchlb_ug, 3)) + "\n")
        self.text_results.insert("end", "Chl a: " + str(Cchla_ug) + "\n")
        self.text_results.insert("end", "Chl b: " + str(Cchlb_ug) + "\n")
        self.text_results.insert("end", "\nWith nmol/uL concents:\n\n")
        self.text_results.insert("end", "Chl a/b: " + str(round(Cchla_nmol/Cchlb_nmol, 3)) + "\n")
        self.text_results.insert("end", "Chl a: " + str(Cchla_nmol) + "\n")
        self.text_results.insert("end", "Chl b: " + str(Cchlb_nmol) + "\n")
                
        self.text_results.configure(state= "disabled") # Prevent the user to edit the text.
        self.string_status.set("Calcs finished!")
    
    

    def onSave(self):
        
        if self.datasets_backup == []:
            self.string_status.set("First load samples!")
            return

        # get the normalization factor
        norm = self.norm_var.get()
        if norm == '': self.norm_var.set('1')
        norm = int(self.norm_var.get())
        
        self.string_status.set("Fitting and saving all..."); self.label_status.update_idletasks()
        
        self.datasets = copy.deepcopy(self.datasets_backup)
        self.doComboManipulations()
        
        # get current date and time -> to avoid filename conflicts
        now = datetime.datetime.now() # get system's date and time
        nowString = now.strftime("%Y%m%d%H%M%S")
            
        file_path = tkinter.filedialog.asksaveasfilename(title = "Save results...", initialfile = self.datasets_filename + "_" + nowString, defaultextension = ".xlsx")
        if file_path == "":  # If dialog closed with "cancel"
            self.string_status.set("Operation canceled!")
            return
        
        if os.path.isfile(file_path): # for file replacement
            os.remove(file_path)
        
        if(self.combo_algo.get() == "Porra eq"):
            tkinter.messagebox.showwarning(title="Warning", message="Save with Porra eq is not implemented. Caffarri fit will be used instead.")
        
        if(self.combo_algo.get() == "Caffarri eq"):
            tkinter.messagebox.showwarning(title="Warning", message="Save with Caffarri eq is not implemented. Caffarri fit will be used instead.")

        self.progress.grid() # show progress bar
        # saveCSV(self.datasets, self.standards, self.combo_algo.get(), file_path, self.progress)
        saveXLSX(self.datasets, self.standards, self.combo_algo.get(), file_path, self.progress, norm, self.checkChla.get(), self.checkChlb.get(), self.checkBeta.get(), self.checkLute.get(), self.checkNeo.get(), self.checkViola.get(), self.checkZea.get(), self.checkAsta.get())
        self.progress.grid_remove() # hide progress bar
    
        self.string_status.set("All saved!")
                                                 
                                                 
    
    def onHide(self):
        
        if(self.p2 != None and self.p3 != None):
            self.p2.destroy()
            self.p3.destroy()
            self.p2 = None
            self.p3 = None
                
            tkinter.Grid.rowconfigure(self.frame_canvas, 2, weight=0)
            tkinter.Grid.columnconfigure(self.frame_canvas, 2, weight=0)
            
            self.button_hide["state"] = "disabled"
            



def resize_handler():
    return


#if __name__ == "__main__":
root = tkinter.Tk()
root.title("chlorocarfitter v1.4.1")
icon = tkinter.Image(imgtype = "photo", file= resourcePath("icons/icon_chlorocarfitter.gif"))
root.iconphoto(True, icon) # default = True
main = MainFrame(root)
main.pack(fill = "both", expand = True)
root.update()
root.minsize(root.winfo_width(), root.winfo_height()) 
#root.maxsize(root.winfo_width(), root.winfo_height())   
root.mainloop()
    
    