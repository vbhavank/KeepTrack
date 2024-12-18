import pandas as pd
import numpy as np
import sys 
from tkinter import * 
from pandastable import Table, TableModel
import pdb
import tkinter.font as font
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import font as tkFont  # for convenience
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import webbrowser
import os
import io
from AllTax import AllTMonth
from AllTax import AllTYear
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


SOFTWARE_NAME = "KeepTrackv8.5"
REQUIRED_FIELDS = ['DATE','Invoice No.', \
                   'Order ID ','Shipping', 'SKU',
                  'Quantity','Platform ','Incl_Tax','SGST@6%','CGST@6%','IGST@12%','Price', 'Name','Time','Return Status','Url','otherSKU']

csv_file_path = 'InventorySheet.csv'
prime_file_path = 'Prime-KA.csv'
import tempfile


class InteractiveChart():
    def __init__(self, root_tk):
        # Create a container
        self.root_tk = root_tk
        #frame = Tkinter.Frame(master)
        # Create 2 buttons
        self.button_right = tk.Button(self.root_tk,text="< Back",
                                        command=self.decrease)
        self.button_right.pack(side="left")
        self.button_left = tk.Button(self.root_tk,text="Front >",
                                        command=self.increase)
        self.button_left.pack(side="left")

        self.org_df = pd.read_csv(csv_file_path)
        self.curr_df = self.org_df
        self.step = 1000
        self.start = 0
        self.update_step()
        self.make_figurefromdf()
        self.plot_figu()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        self.root_tk.mainloop()

    def update_step(self):
        self.finish = self.start + self.step
        self.curr_df = self.org_df.truncate(before=self.start, after=self.finish)    

    def make_figurefromdf(self):
        df = self.curr_df
        num_order = {}
        amz_or_cnt = {}

        #time_tup = tuple((df['DATE'].unique()[0], df['DATE'].unique()[-1])
        def get_distr(df):
            r_dict = {}
            
            for date_t in df['DATE'].unique():
                df_sub = df[df['DATE'] == date_t]
                val_fk = 0
                val_amz = 0
                val_pur = 0
                val_ets = 0
                val_mees = 0
                val_amz_us = 0
                for kl in range(len(df_sub)):
                    qu = df_sub['Quantity'].iloc[kl]
                    pr = df_sub['Incl_Tax'].iloc[kl]

                    if qu < 0:
                        if df_sub['Platform '].iloc[kl] == 'Flipkart':
                            val_fk += pr#(qu* -1)
                        if df_sub['Platform '].iloc[kl] == 'Amazon':
                            val_amz += pr#(qu* -1)

                        if df_sub['Platform '].iloc[kl] == 'Etsy':
                            val_ets += pr
                        if df_sub['Platform '].iloc[kl] == 'Website':
                            val_pur += pr
                        if df_sub['Platform '].iloc[kl] == 'Meesho':
                            val_mees += pr
                        if df_sub['Platform '].iloc[kl] == 'Amazon-USA':
                            val_amz_us += pr
                    #else:
                    #    if df_sub['Platform '].iloc[kl] == 'Purchase':
                    #        val_pur += pr/#(qu* -1)
                try:
                    r_dict[str(date_t[0:2] + date_t[3:6])] = [val_fk, val_amz, val_pur, val_ets, val_mees, val_amz_us]
                except:
                    pass
            return r_dict
        r_Cnt = get_distr(df)
        self.xs, self.y_1s, self.y_2s, self.y_3s, self.y_4s,  self.y_5s, self.y_6s = self.aggregate(r_Cnt)

    def plot_figu(self):
        #amz_cnt = get_distr(df_amz)
        fig = Figure()
        ax = fig.add_subplot(111)
        #import pdb
        #pdb.set_trace()
        #ax.xticks(len(r_Cnt.keys()), r_Cnt.values())
        #ax.set_xticklabels(rotation = (0), fontsize = 10, va='bottom', ha='left')

        self.final_fk = ax.plot(self.xs, self.y_1s, "-b", label="Flipkart")
        self.final_amaz = ax.plot(self.xs, self.y_2s, "-g", label = "Amazon")
        self.final_pur = ax.plot(self.xs, self.y_3s, "-r", label = "Website")
        self.final_ets = ax.plot(self.xs, self.y_4s, "-y", label = "Etsy")
        self.final_ets = ax.plot(self.xs, self.y_5s, "-o", label = "Meesho")
        self.final_ets = ax.plot(self.xs, self.y_6s, "-o", label = "Amazon-USA")

        ax.legend((self.final_fk, self.final_amaz, self.final_pur, self.final_ets), ('Flipkart', 'Amazon', 'Website', 'Etsy', 'Meesho', 'Amazon-USA'), fancybox=True, loc='center', shadow=True)
        ax.legend()
        ax.set_xlabel("Date")
        ax.set_ylabel("Sales(Inc Tax) in ₹")
        self.canvas = FigureCanvasTkAgg(fig,master=self.root_tk)
        self.canvas.draw()
        return fig

    def increase(self):
        self.start += self.step
        self.finish += self.step
        self.curr_df = self.org_df.truncate(before=self.start, after=self.finish)

        self.make_figurefromdf()
        #self.final_fk.set_ydata(self.y_1s)
        #self.final_fk.set_xdata(self.xs)
        #self.final_amaz.set_ydata(self.y_2s)
        #self.final_amaz.set_xdata(self.xs)
        self.plot_figu()
    def aggregate(self, som_dict):
        f_v_dict = []
        a_v_dict = []
        p_v_dict = []
        e_v_dict = []
        meesho_dict = []
        amz_usa_dict = []
   
        k_dict = []
        for k in som_dict.keys():
            f_v_dict.append(som_dict[k][0])
            a_v_dict.append(som_dict[k][1])
            p_v_dict.append(som_dict[k][2])
            e_v_dict.append(som_dict[k][3])
            meesho_dict.append(som_dict[k][4])
            amz_usa_dict.append(som_dict[k][5])
            k_dict.append(k)
        return k_dict, f_v_dict, a_v_dict, p_v_dict, e_v_dict, meesho_dict, amz_usa_dict

    def decrease(self):
        self.start -= self.step

        self.finish -= self.step
        if self.start < 0:
            self.start += self.step
            self.finish += self.step
        self.curr_df = self.org_df.truncate(before=self.start, after=self.finish)    
        self.make_figurefromdf()
        #self.final_fk.set_ydata(self.y_1s)
        #self.final_fk.set_xdata(self.xs)
        #self.final_amaz.set_ydata(self.y_2s)
        #self.final_amaz.set_xdata(self.xs)
        self.plot_figu()


class GeneralScreen():
    def calendarfnc(self):
        from tkcalendar import Calendar
      
        calend = Tk()
      
        # Set geometry
        calend.geometry("400x400")
        calend.title('{}: Calendar'.format(SOFTWARE_NAME))

        # Add Calender
        cal = Calendar(calend, selectmode = 'day',
                       year = 2023, month = 1,
                       day = 22)
          
        cal.pack(pady = 20)
          
        def grad_date():
            self.date = cal.get_date()
            self.date = datetime.strptime(self.date, '%m/%d/%y').strftime('%d/%b/%Y')
            self.display_date.config(text = "" + self.date)
            calend.destroy()
        # Add Button and Label
        butt = tk.Button(calend, text = "Set Date",
               command =grad_date).pack(pady = 30)

        calend.mainloop()
        self.CurrentActiveWindow = calend
    def popup(self, msg):
        #msg =
        popup = tk.Tk()
        popup.wm_title("Warning!")
        label = tk.Label(popup, text=msg, font=('Helvetica',20,'normal'))
        label.pack(side="top", fill="x", pady=20)
        B1 = tk.Button(popup, text="Okay", command = popup.destroy)
        B1.pack()
        popup.mainloop()
    def Main_screen(self):
        self.root_tk.destroy()
        self.root_tk=tk.Tk()
        self.root_tk.wm_title("Welcome to {}!".format(SOFTWARE_NAME))

        self.root_tk.geometry("700x400")
        def update_sheet_drive():
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()

            drive = GoogleDrive(gauth)
            file1 = drive.CreateFile({"mimeType": "text/csv"})
            file1.SetContentFile(csv_file_path)
            file2 = drive.CreateFile({"mimeType": "text/csv"})
            file2.SetContentFile(prime_file_path)
            file1.Upload()
            file2.Upload()

        def redict_explore_prim():
            self.root_tk.destroy()
            #self.root_tk =tk.Tk()
            viewinev = ViewInventory()
            inv_df = viewinev.wrap_grop_inve('Prime-KA')
            
        def redict_explore():
            self.root_tk.destroy()
            #self.root_tk =tk.Tk()
            viewinev = ViewInventory()
            inv_df = viewinev.wrap_grop_inve('InventorySheet')
            #app2 = TestApp(root_tk=self.root_tk,df=inv_df)
            #app2.show_table()
        def sale():
            self.root_tk.destroy()
            self.root_tk=tk.Tk()
            UpdateInApp  = SaleClass(self.root_tk, self.AUTH_NAME)
            UpdateInApp.AddNewOrder()
            #update_sheet_drive()
        def purchase():
            self.root_tk.destroy()
            self.root_tk=tk.Tk()
            UpdateInApp  = PurchaseClass(self.root_tk, self.AUTH_NAME)
            UpdateInApp.AddNewOrder()
            #update_sheet_drive()
        def add_old_order():
            self.root_tk.destroy()
            self.root_tk=tk.Tk()
            UpdateInApp  = UpdateReturnOrder(self.root_tk, self.AUTH_NAME)
            UpdateInApp.UpdateOldOrder()
            #update_sheet_drive()
        def update_url_image():
            self.root_tk.destroy()
            self.root_tk=tk.Tk()
            UpdateInApp  = UpdateImage(self.root_tk, self.AUTH_NAME)
            UpdateInApp.updateurls()
            #update_sheet_drive()

        SALE_ORDER = tk.Button(self.root_tk,text = 'Sale', command = sale,height = 5, width = 20, bg='blue', fg='white')
        purchase_order = tk.Button(self.root_tk,text = 'Purchase', command = purchase,height = 5, width = 20, bg='white', fg='black')
        add_return_order = tk.Button(self.root_tk,text = 'Enter Return Order', command = add_old_order, height = 5, width = 20, bg='red', fg='white')
        view_inve = tk.Button(self.root_tk,text = 'View Inventory', command = redict_explore, height = 5, width = 20, bg='green', fg='white')
        view_prime_inve = tk.Button(self.root_tk,text = 'View Prime Inventory', command = redict_explore_prim, height = 5, width = 20, bg='blue', fg='white')
        update_img = tk.Button(self.root_tk,text = 'Update Images', command = update_url_image, height = 5, width = 20, bg='yellow', fg='black')
        backup = tk.Button(self.root_tk,text = 'Create Backup', command = update_sheet_drive, height = 5, width = 20, bg='yellow', fg='black')

        purchase_order['font'] = helv36
        SALE_ORDER['font'] = helv36
        add_return_order['font'] = helv36
        view_inve['font'] = helv36
        update_img['font'] = helv36
        backup['font'] = helv36
        view_prime_inve['font'] = helv36

        image = Image.open('logo.png')
        image = image.resize((156, 64))
        photo = ImageTk.PhotoImage(image)

        label = Label(self.root_tk, image = photo)
        label.image = photo
        #launch the app

        #view_inventory_reup.grid(row=0,column=0)
        SALE_ORDER.grid(row=0,column=1)
        add_return_order.grid(row=1,column=1)
        view_inve.grid(row=2,column=1)
        view_prime_inve.grid(row=1,column=2)
        update_img.grid(row=3,column=1)
        purchase_order.grid(row=0,column=2)
        backup.grid(row=2,column=2)
        label.grid(row=0)

        # performing an infinite loop
        # for the window to display
        self.root_tk.mainloop()

class TestApp():
        """Basic test frame for the table"""
        def __init__(self, root_tk, parent=None, df=None):
            self.parent = parent
            self.df = df
            self.root_tk = root_tk

        def show_table(self):
            #Frame.__init__(self)
            #self.main = self.master
                
            self.root_tk.geometry('600x400')
            self.root_tk.title(SOFTWARE_NAME)
            f = Frame(self.root_tk )
            f.pack(fill=BOTH,expand=1)
            self.table = pt = Table(f, dataframe=self.df,
                                    showtoolbar=True, showstatusbar=True)
            pt.show()
            return

class UpdateImage(GeneralScreen):
    def __init__(self, root_tk, AUTH_NAME):
        self.df = pd.read_csv(csv_file_path)
        self.sku = None
        self.url = None
        self.root_tk = root_tk
        self.AUTH_NAME = AUTH_NAME

    def popup(self, msg):
        #msg =
        popup = tk.Tk()
        popup.wm_title("!")
        label = tk.Label(popup, text=msg, font=('Helvetica',20,'normal'))
        label.pack(side="top", fill="x", pady=20)
        B1 = tk.Button(popup, text="Okay", command = popup.destroy)
        B1.pack()
        popup.mainloop()
    def updateurls(self):
        self.root_tk.geometry("600x400")
        self.root_tk.title('{}: Add Return Order to Database'.format(SOFTWARE_NAME))
        sku=tk.StringVar()
        url=tk.StringVar()

        sku_lab = tk.Label(self.root_tk, text = 'SKU', font=('Helvetica',20, 'bold'))
        sku_val = tk.Entry(self.root_tk,textvariable = self.sku, font=('Helvetica',20,'normal'))
        Url_la = tk.Label(self.root_tk, text = 'Url', font=('Helvetica',20, 'bold'))
        url_val = tk.Entry(self.root_tk,textvariable = self.url, font=('Helvetica',20,'normal'))
        def _submit_url():
           self.sku = str(sku_val.get())
           self.url = str(url_val.get()) 
           sku_val.delete(0, 'end')
           url_val.delete(0, 'end')
           if len(self.df.index[self.df['SKU'] == self.sku].tolist()) > 0:
               for_all_ind = self.df.index[self.df['SKU'] == self.sku].tolist()
               for indi in for_all_ind:
                   self.df.loc[indi, 'Url'] = self.url
               self.df.to_csv(csv_file_path)
               self.popup( "Successfully Updated all Image Urls")
           else:
               self.popup( "SKU not found in Database")
        def exitroot():
            self.root_tk.destroy()
        def Backbutton():
            self.root_tk.destroy()
            self.root_tk =tk.Tk()
            self.root_tk.title('Update Images')
            app = TestApp(root_tk=self.root_tk, df=pd.read_csv(csv_file_path))
            app.show_table()
        submitButton = tk.Button(self.root_tk, command=_submit_url, text="Update Imgae Link", bg='blue', fg='white')
        ExitButton = tk.Button(self.root_tk, command=exitroot, text="Exit", bg='red', fg='white')
        BackButton = tk.Button(self.root_tk, command=Backbutton, text="View all Entries", bg='yellow')
        MainButton = tk.Button(self.root_tk, command=self.Main_screen, text="Main Screen" , bg='blue', fg='white')

        submitButton['font'] = helv362
        ExitButton['font'] = helv362
        BackButton['font'] = helv362
        MainButton['font'] = helv362

        sku_lab.grid(row=1,column=0)
        sku_val.grid(row=1,column=1)
        Url_la.grid(row=2,column=0)
        url_val.grid(row=2,column=1)
        
        
        submitButton.grid(row=3,column=0)
        BackButton.grid(row=3,column=2)
        MainButton.grid(row=4,column=1)
        ExitButton.grid(row=3,column=1)
        self.root_tk.mainloop()

class ViewInventory():
    def __init__(self, open_type=True):
        self.df = None
        self.open_type = open_type

    def wrap_grop_inve(self, platform):
        if platform == "Prime-KA":
#            self.df = pd.read_excel(open(full_file_path, 'rb'),
#                     sheet_name='Prime-KA')
            self.df = pd.read_csv(prime_file_path)

        else:
            self.df = pd.read_csv(csv_file_path)
            #self.df = pd.read_excel(open(full_file_path, 'rb'),
            #         sheet_name='InventorySheet')
        self.group_inventory()
        
    def group_inventory(self):
        from IPython.core.display import display,HTML
        # convert your links to html tags 
        def path_to_image_html(path):
            return '<img src="'+ path + '" width="60" >'
        pd.set_option('display.max_colwidth', None)

        #self.df = pd.read_csv(csv_file_path)
        inv_df = pd.DataFrame(columns=['SKU','Quantity In Store','Product', 'Purchase Price', 'House Price', 'Flipkart Price','Website Price', 'Etsy@69.5'])
        sku_dict = {}
        url_dict= {}
        purchase_price = {}
        #import pdb
        #pdb.set_trace()
        dub_df = self.df[self.df['Platform '] == 'Purchase']
        house_price = {}
        flipkart_price = {}        
        website_price = {}
        etsy_price = {}
        dollar_rate = 69.5
        for eachsku in self.df['SKU'].unique():
            dub_df_2 = dub_df[dub_df['SKU'] == eachsku]
            sku_dict[eachsku] = 0
            try:
                purchase_price[eachsku] = round(dub_df_2['Incl_Tax'].sum()/dub_df_2['Quantity'].sum())
                house_price[eachsku] = round( 1.45*purchase_price[eachsku])
                flipkart_price[eachsku] = round(1.25*house_price[eachsku])
                website_price[eachsku] = round(1.2*house_price[eachsku])
                etsy_price[eachsku] =  "$" + str(round(((1.2*house_price[eachsku])*1.6 + 1500 + 3000)/dollar_rate))
            except:
                purchase_price[eachsku] = 0
                house_price[eachsku] = 0
                flipkart_price[eachsku] = 0
                website_price[eachsku] = 0
                etsy_price[eachsku] = 0

        for eachsku in self.df['SKU'].unique():
            tmp_df_q = self.df[self.df['SKU'] == eachsku]['Quantity'].sum()
            
            try:
                url1 = self.df[self.df['SKU'] == eachsku]['Url'].unique()[0]
                #url1 = url1_byte[url1_byte.keys()[0]]
                assert len(url1)>0

                #url1 = url1[0]
           
            except:
                url1= 'https://drive.google.com/file/d/1jWJ1eZUzPgYUD5HLyvJTfkHMR5TpD02Q/view?usp=sharing'
            url_dict[eachsku]='https://drive.google.com/uc?id=' + url1.split('/')[-2]
            try:
                assert not self.df[self.df['SKU'] == eachsku]['otherSKU'].isnull().iloc[0]
                comboskulist = self.df[self.df['SKU'] == eachsku]['otherSKU']
                #import pdb
                #pdb.set_trace()
                location2 = self.df.index[self.df['SKU'] == eachsku].tolist()
                for cmb_loc in location2:
                    if self.df['Platform '][cmb_loc] != 'Purchase':
                        for c_sku in comboskulist.iloc[0].split('/'):
                        
                        #if len(self.df[self.df['SKU'] == c_sku])>0:
                        #location2 = inv_df.index[inv_df['SKU'] == c_sku].tolist()
                            sku_dict[c_sku] += (1*self.df['Quantity'][cmb_loc])
                        #inv_df.loc[location2[0], 'Quantity In Store'] = inv_df['Quantity In Store'][location2[0]] - 1
                    #else:
                        #sku_dict[c_sku] = -1
                        #inv_df = inv_df.append({'SKU':eachsku,'Quantity In Store': -1, 'Product': url2}, ignore_index=True)
            #import pdb
            #pdb.set_trace()
            except:
                pass
            sku_dict[eachsku] = sku_dict[eachsku] + int(tmp_df_q)
            #if #len(inv_df.index[inv_df['SKU'] == eachsku].tolist())>0:
                #inv_df = inv_df.append({'SKU':eachsku,'Quantity In Store': int(tmp_df_q), 'Product': url2}, ignore_index=True)

                #import pdb
                #pdb.set_trace()
            #    location2 = inv_df.index[inv_df['SKU'] == eachsku].tolist()
            #    inv_df.loc[location2[0], 'Quantity In Store'] = inv_df['Quantity In Store'][location2[0]] + int(tmp_df_q)
            #else:
        #import pdb
        #pdb.set_trace()        
        for c_keys in sku_dict.keys():
            if str(c_keys)!='nan':
                inv_df = inv_df.append({'SKU':str(c_keys),'Quantity In Store': int(sku_dict[c_keys]), 'Product': str(url_dict[c_keys]),'Purchase Price': purchase_price[c_keys],
                                        'House Price': house_price[c_keys], 'Flipkart Price': flipkart_price[c_keys], 'Website Price': website_price[c_keys],
                                        'Etsy@69.5':etsy_price[c_keys]}, ignore_index=True)
        inv_df = inv_df.sort_values('Quantity In Store')
        if self.open_type:
            image_cols = ['Product']  #<- define which columns will be used to convert to html

            # Create the dictionariy to be passed as formatters
            format_dict = {}
            for image_col in image_cols:
                format_dict[image_col] = path_to_image_html
            #inv_df = inv_df.style.set_properties(**{'background-color': 'black',
            #                   'color': 'green'}).render()
            #display(HTML(inv_df.to_html(escape=False ,formatters=format_dict)))
            inv_df.to_html('inventory_html.html', escape=False, formatters=format_dict)

            filename = 'file:///'+os.getcwd()+'/' + 'inventory_html.html'
            webbrowser.open_new_tab(filename)
        return inv_df

# declaring string variable
# for storing name and password
class UpdateReturnOrder(GeneralScreen):
    def __init__(self, root_tk, AUTH_NAME):
        self.date = None
        self.CurrentActiveWindow = None
        self.orderid = None
        self.sku = None
        self.quantity = None
        self.root_tk= root_tk
        self.AUTH_NAME = AUTH_NAME

    def validate_date(self):
        if self.sku is None:
            self.popup( "No SKU")

        if self.quantity is None:
            self.popup( "Imvalid Quantity")
                
        if self.orderid == "":
            self.orderid = "N/A"
            
        if self.date is None:
            self.popup( "No Date")
           
    def UpdateOldOrder(self):
        #return_order_tk.q()
        #return_order_tk=tk.Tk()
        self.root_tk.geometry("600x400")
        self.root_tk.title('{}: Add Return Order to Database'.format(SOFTWARE_NAME))
        orderid=tk.StringVar()
        sku=tk.StringVar()
        return_satt=tk.StringVar()
        return_satt.set('Noticed')
        order_id = tk.Label(self.root_tk, text = 'OrderID', font=('Helvetica',20, 'bold'))
        Oderid = tk.Entry(self.root_tk,textvariable = self.orderid, font=('Helvetica',20,'normal'))
        self.display_date = tk.Label(self.root_tk, text="",  font=('Helvetica',20,'normal'))

        sku_n = tk.Label(self.root_tk, text = 'SKU', font=('Helvetica',20, 'bold'))
        saku = tk.Entry(self.root_tk,textvariable = self.sku, font=('Helvetica',20,'normal'))
        quantity_n = tk.Label(self.root_tk, text = 'Quantity', font=('Helvetica',20, 'bold'))
        Quantit = tk.Entry(self.root_tk,textvariable = self.quantity, font=('Helvetica',20,'normal'))
        return_status = tk.OptionMenu(self.root_tk, return_satt, "Noticed", "Recieved")
        orderdate = tk.Button(self.root_tk,text = 'Select Date', command = self.calendarfnc)
        variable_plt = StringVar(self.root_tk)

        variable_plt.set("Inventory")
        
        platfor = tk.OptionMenu(self.root_tk, variable_plt, "Inventory","Prime-KA")

        def update_return_order():
            self.orderid = str(Oderid.get())
            self.sku = saku.get()
            self.quantity = int(Quantit.get())
            self.validate_date()
            Quantit.delete(0, 'end')
            saku.delete(0, 'end')
            Oderid.delete(0, 'end')
            self.platform = variable_plt.get()
            if self.platform == "Prime-KA":
                dframe = pd.read_csv(prime_file_path)
                #dframe = pd.read_excel(open(full_file_path, 'rb'),
                #    sheet_name='Prime-KA') 
            else:
                dframe = pd.read_csv(csv_file_path)
                #dframe = pd.read_excel(open(full_file_path, 'rb'),
                #    sheet_name='InventorySheet')
            df_display = pd.DataFrame(dframe, columns= REQUIRED_FIELDS)
            df = pd.DataFrame()
            if len(df_display.index[df_display['Order ID '] == self.orderid].tolist()) > 0:
                location = df_display.index[df_display['Order ID '] == self.orderid].tolist()
                #locatio2n = [ind for ind in location if df_display['SKU'][ind] == self.sku]
                for loc in location:
                    if df_display['SKU'][loc] == self.sku:
                        try:
                            this_date = datetime.strptime(df_display['DATE'][loc], '%m-%d-%y').strftime('%d/%b/%Y')
                        except:
                            try:
                                this_date = datetime.strptime(df_display['DATE'][loc], '%m/%d/%y').strftime('%d/%b/%Y')
                            except:
                                try:
                                    this_date = datetime.strptime(df_display['DATE'][loc], '%m-%d-%Y').strftime('%d/%b/%Y')

                                except:
                                    try:
                                        this_date = datetime.strptime(df_display['DATE'][loc], '%d-%b-%y').strftime('%d/%b/%Y')
                                    except:
                       #try:        
                        #    assert len(this_date) !=0
                        #except:
                                        this_date = df_display['DATE'][loc]
                        if this_date == self.date:
                            final_loc = loc
                            location = final_loc
                            convrt_date = this_date
                #try:
                #    convrt_date = datetime.strptime(df_display['DATE'][final_loc], '%m-%d-%Y').strftime('%d/%b/%Y') 
                    #local_ind = convrt_date.index(self.date)
                    #location = location[convrt_date.index(self.date)]
                #except:
                    #self.popup( "Contact Bhavan: Date Time Wrong")
                    #location = [ind for ind in location if df_display['DATE'][ind] == self.date]

                    #location = location[0]
                #    convrt_date = [df_display['DATE'][location]]
                #    pass
                #import pdb
                #pdb.set_trace()
                if df_display['SKU'][location] == self.sku and convrt_date == self.date:
                    df_display.loc[location, 'Return Status'] = return_satt.get()
                    if df_display['Quantity'][location] <= (-1 *self.quantity):
                        if return_satt.get() == 'Recieved':
                            df_display.loc[location, 'Quantity'] = df_display['Quantity'][location] + self.quantity
                        df_save = pd.concat([df, df_display])
                        if self.platform == "Prime-KA":
                            #df_save.to_excel(full_file_path,
                            #  sheet_name='Prime-KA') 
                            df_save.to_csv(prime_file_path)
                        else:
                            df_save.to_csv(csv_file_path)

                            #df_save.to_excel(,
                            #  sheet_name='InventorySheet') 
                        
                        tk.messagebox.showinfo(title="Return Order Updated", message="Return Order Uodated successfully")
                    else:
                        self.popup( "Duplicate Entry, Return Order Already updated")
                else:
                    self.popup( "SKU and Date Combination not found in Database!")
            else:
                self.popup( "Order ID and SKU combination not found in Database!")


        def Backbutton():
            self.root_tk.destroy()
            self.root_tk = tk.Tk()
            if self.platform == "Prime-KA":
                df_in = pd.read_csv(prime_file_path)
            else:
                df_in = pd.read_csv(csv_file_path)
            app = TestApp(root_tk=self.root_tk, df=df_in)
            app.show_table()
            
        def exitroot():
            self.root_tk.destroy()
        submitButton = tk.Button(self.root_tk, command=update_return_order, text="Submit Return Order", bg='blue', fg='white')
        ExitButton = tk.Button(self.root_tk, command=exitroot, text="Exit", bg='red', fg='white')
        BackButton = tk.Button(self.root_tk, command=Backbutton, text="View all Entries", bg='yellow')
        MainButton = tk.Button(self.root_tk, command=self.Main_screen, text="Main Screen" , bg='blue', fg='white')
        submitButton['font'] = helv362
        ExitButton['font'] = helv362
        MainButton['font'] = helv362
        BackButton['font'] = helv362
        # Add to order df after gst
        self.display_date.grid(row=0, column=1)

        orderdate.grid(row=0,column=0)
        order_id.grid(row=2,column=0)
        Oderid.grid(row=2,column=1)
        sku_n.grid(row=3,column=0)
        saku.grid(row=3,column=1)
        quantity_n.grid(row=4,column=0)
        Quantit.grid(row=4,column=1)
        submitButton.grid(row=5,column=0)
        BackButton.grid(row=5,column=2)
        return_status.grid(row=1,column=0)
        platfor.grid(row=1,column=2)
        ExitButton.grid(row=5,column=1)
        MainButton.grid(row=6,column=1)
        self.root_tk.mainloop()
        
class SaleClass(GeneralScreen):
    def __init__(self, root_tk, AUTH_NAME):
        self.date = None
        self.CurrentActiveWindow = None
        self.orderid = None
        self.sku = None
        self.platform = None
        self.quantity = None
        self.transaction_type = None
        self.ship_type = None
        self.incl_tax = None
        self.invoiceno = None
        self.imageurl = None
        self.igst = 0
        self.cgst = 0
        self.sgst = 0
        self.root_tk = root_tk
        self.AUTH_NAME = AUTH_NAME
        self.otherSKU = None

    def type_of_transaction(self):
        master = Tk()

        variable = StringVar(master)
        variable.set("one") # default value

        w = OptionMenu(master, variable, "one", "two", "three")
        w.pack()

        mainloop()

    def validate_date(self):
            
        if self.invoiceno == "":
            self.invoiceno = "N/A"
        if self.sku is None:
            self.popup( "No SKU")
                    
        if self.quantity is None:
            self.popup( "No Quantity")

        if self.incl_tax is None:
            self.popup( "No Incl Tax")

        if self.date is None:
            self.popup( "No Date")
                
        if self.orderid == "":
            self.orderid = "N/A"

    def AddNewOrder(self):
        #new_order_tk=tk.Tk()
        
        #self.root_tk.geometry("800x400")
        self.root_tk.title('{}: Add Sales Transaction to Database'.format(SOFTWARE_NAME))
        orderid=tk.StringVar()
        sku=tk.StringVar()
        platform=tk.StringVar()
        date_set=tk.StringVar()

        invoice_no = tk.Label(self.root_tk, text = 'Invoice No.', font=('Helvetica',20, 'bold'))
        invoiceno = tk.Entry(self.root_tk,textvariable = self.invoiceno, font=('Helvetica',20,'normal'))
        

        order_id = tk.Label(self.root_tk, text = 'OrderID', font=('Helvetica',20, 'bold'))
        Oderid = tk.Entry(self.root_tk,textvariable = self.orderid, font=('Helvetica',20,'normal'))
        
        sku_n = tk.Label(self.root_tk, text = 'SKU', font=('Helvetica',20, 'bold'))
        saku = tk.Entry(self.root_tk,textvariable = self.sku, font=('Helvetica',20,'normal'))
        platform_name = tk.Label(self.root_tk, text = 'Platform', font=('Helvetica',20, 'bold'))
        platfor = tk.Entry(self.root_tk,textvariable = self.platform, font=('Helvetica',20,'normal'))

        price_incl_t = tk.Label(self.root_tk, text = 'Inclusive Tax', font=('Helvetica',20, 'bold'))
        price_inc_text = tk.Entry(self.root_tk,textvariable = self.incl_tax, font=('Helvetica',20,'normal'))
        self.display_date = tk.Label(self.root_tk, text="",  font=('Helvetica',20,'normal'))
        quantity_n = tk.Label(self.root_tk, text = 'Quantity', font=('Helvetica',20, 'bold'))
        Quantit = tk.Entry(self.root_tk,textvariable = self.quantity, font=('Helvetica',20,'normal'))
        imurl = tk.Label(self.root_tk, text = 'Image Url', font=('Helvetica',20, 'bold'))
        imgUrLink = tk.Entry(self.root_tk,textvariable = self.imageurl, font=('Helvetica',20,'normal'))
        variable_trans = StringVar(self.root_tk)
        variable_trans.set("Sale")
        variable_plt = StringVar(self.root_tk)

        variable_plt.set("Flipkart")
        variable_shipping = StringVar(self.root_tk)
        variable_shipping.set("Not Karnataka")
        platfor = tk.OptionMenu(self.root_tk, variable_plt, "Flipkart","Prime-KA", "Amazon", "Website", "Etsy", "House", "Meesho", "Amazon-USA")
        #trans_type = tk.OptionMenu(self.root_tk, variable_trans, "Sale")
        ship_type = tk.OptionMenu(self.root_tk, variable_shipping, "Not Karnataka", "Karnataka")

        orderdate = tk.Button(self.root_tk,text = 'Select Date', command = self.calendarfnc)

                
        def get_order_data():
            self.orderid = str(Oderid.get())
            self.sku = saku.get()
            self.platform = variable_plt.get()
            #self.transaction_type = variable_trans.get()
            self.quantity = int(Quantit.get())
            self.ship_type = variable_shipping.get()
            self.incl_tax = float(price_inc_text.get())
            self.invoiceno = invoiceno.get()
            self.validate_date()
            self.imageurl = str(imgUrLink.get())
            Quantit.delete(0, 'end')
            saku.delete(0, 'end')
            Oderid.delete(0, 'end')
            price_inc_text.delete(0, 'end')
            invoiceno.delete(0, 'end')
            if self.platform == "Prime-KA":
                dframe = pd.read_csv(prime_file_path)
#                dframe = pd.read_excel(open(full_file_path, 'rb'),
#                    sheet_name='Prime-KA') 
            else:
                dframe = pd.read_csv(csv_file_path)

#                dframe = pd.read_excel(open(full_file_path, 'rb'),
#                    sheet_name='InventorySheet')
            df_display = pd.DataFrame(dframe, columns= REQUIRED_FIELDS)

            if self.incl_tax != None:
                if self.ship_type == "Karnataka":# and self.transaction_type != "Inventory":
                    delat = ((1/1.12)*self.incl_tax)
                    self.cgst = (self.incl_tax - delat)/2# + ((-1 * 0.8928571429)*self.incl_tax)
                    self.sgst = (self.incl_tax - delat)/2
                    
                if self.ship_type == "Not Karnataka":# and self.transaction_type != "Inventory":
                    self.igst = self.incl_tax  - (1/1.12)*self.incl_tax
                self.quantity = -1 * self.quantity
                # removed because of unknown error.
                #self.otherSKU = df_display[df_display["SKU"] == self.sku]['otherSKU'].sum()
                if self.otherSKU == 0:
                    self.otherSKU = None
                price_before = self.incl_tax - self.cgst - self.sgst - self.igst
                dict_app = {'DATE': self.date,'Invoice No.': self.invoiceno, 
                           'Order ID ': self.orderid,'Shipping': self.ship_type , 'SKU': self.sku, 
                          'Quantity':self.quantity,'Platform ': self.platform, 
                            'Incl_Tax':self.incl_tax,'SGST@6%':self.sgst,'CGST@6%':self.cgst,'IGST@12%':self.igst, 
                            'Price':round(price_before, 2), 'Name': self.AUTH_NAME,'Time':datetime.now(),'Url': self.imageurl,'otherSKU':self.otherSKU} 

                df = pd.DataFrame()
                if len(df_display.index[df_display['Order ID '] == self.orderid].tolist()) > 0:
                    location = df_display.index[df_display['Order ID '] == self.orderid].tolist()
                    location = [ind for ind in location if df_display['DATE'][ind] == self.date]
                    if len(location)>0:
                        if df_display['SKU'][location[0]] == self.sku and df_display['DATE'][location[0]] == self.date:
#                            if df_display['Quantity'][location] < self.quantity:
#                                df_display.loc[location, 'Quantity'] = df_display['Quantity'][location] + self.quantity 
#                                self.popup( "This is a return Order")
#                            else:
                            self.popup( "Error!!! Use Return Order console, this order is already sent.")
                        else:
                            df = df.append(dict_app, ignore_index=True)
                            tk.messagebox.showinfo(title="Successfully Added", message="Order added successfully")
                    else:
                        df = df.append(dict_app, ignore_index=True)
                        tk.messagebox.showinfo(title="Successfully Added", message="Order added successfully")
                else:
                    df = df.append(dict_app, ignore_index=True)
                    tk.messagebox.showinfo(title="Successfully Added", message="Order added successfully")

                df_save = pd.concat([df, df_display])
                if self.platform == "Prime-KA":
                    df_save.to_csv(prime_file_path)
                else:
                    df_save.to_csv(csv_file_path)
        def exitroot():
            self.root_tk.destroy()
        def Backbutton():
            self.root_tk.destroy()
            self.root_tk =tk.Tk()
#            backwin.title('EnthAv0')

            #CurrentActiveWindow = root
            # setting the windows size
            #backwin.geometry("600x400")
            if self.platform == "Prime-KA":
                df_in = pd.read_csv(prime_file_path)
            else:
                df_in = pd.read_csv(csv_file_path)
                #df_in = pd.read_excel(open(full_file_path, 'rb'),
                #     sheet_name='InventorySheet') 
            app = TestApp(root_tk=self.root_tk, df=df_in)
            app.show_table()
            
        submitButton = tk.Button(self.root_tk, command=get_order_data, text="Submit",height = 2, width = 6, bg='green', fg='white')
        ExitButton = tk.Button(self.root_tk, command=exitroot, text="Exit", height = 2, width = 6, bg='red', fg='white')
        BackButton = tk.Button(self.root_tk, command=Backbutton, text="View all Entries" , bg='yellow')
        MainButton = tk.Button(self.root_tk, command=self.Main_screen, text="Main Screen" , bg='blue', fg='white')
        submitButton['font'] = helv362
        ExitButton['font'] = helv362
        BackButton['font'] = helv362
        MainButton['font'] = helv362

        # Add to order df after gst 
        order_id.grid(row=1,column=0)
        Oderid.grid(row=1,column=1)
        invoice_no.grid(row=2,column=0)
        invoiceno.grid(row=2,column=1)
        ship_type.grid(row=3, column=0)
        sku_n.grid(row=4,column=0)
        saku.grid(row=4,column=1)
        platfor.grid(row=3,column=1)
        quantity_n.grid(row=5,column=0)
        Quantit.grid(row=5,column=1)
        price_incl_t.grid(row=6,column=0)
        price_inc_text.grid(row=6,column=1)
        self.display_date.grid(row=0, column=1)
        orderdate.grid(row=0,column=0)
        #imurl.grid(row=7,column=0)
        #imgUrLink.grid(row=7,column=1)
        
        submitButton.grid(row=8,column=0)
        BackButton.grid(row=8,column=2)
        MainButton.grid(row=9,column=1)
        ExitButton.grid(row=8,column=1)
        self.root_tk.mainloop()
        
class PurchaseClass(GeneralScreen):
    def __init__(self, root_tk, AUTH_NAME):
        self.date = None
        self.CurrentActiveWindow = None
        self.orderid = None
        self.sku = None
        self.platform = None
        self.quantity = None
        self.otherSKU = None
        self.ship_type = None
        self.incl_tax = None
        self.invoiceno = None
        self.imageurl = None
        self.igst = 0
        self.cgst = 0
        self.sgst = 0
        self.root_tk = root_tk
        self.AUTH_NAME = AUTH_NAME

    def type_of_transaction(self):
        master = Tk()

        variable = StringVar(master)
        variable.set("one") # default value

        w = OptionMenu(master, variable, "one", "two", "three")
        w.pack()

        mainloop()

    def validate_date(self):
            
        if self.invoiceno == "":
            self.invoiceno = "N/A"
        if self.sku is None:
            self.popup( "No SKU")
                    
        if self.quantity is None:
            self.popup( "No Quantity")

        if self.incl_tax is None:
            self.popup( "No Incl Tax")

        if self.date is None:
            self.popup( "No Date")
                
        if self.orderid == "":
            self.orderid = "N/A"

    def AddNewOrder(self):
        #new_order_tk=tk.Tk()
        
        self.root_tk.geometry("800x400")
        self.root_tk.title('{}: Add Purchase Transaction to Database'.format(SOFTWARE_NAME))
        orderid=tk.StringVar()
        sku=tk.StringVar()
        platform=tk.StringVar()
        date_set=tk.StringVar()
  
        sku_n = tk.Label(self.root_tk, text = 'SKU', font=('Helvetica',20, 'bold'))
        saku = tk.Entry(self.root_tk,textvariable = self.sku, font=('Helvetica',20,'normal'))

        price_incl_t = tk.Label(self.root_tk, text = 'Inclusive Tax', font=('Helvetica',20, 'bold'))
        price_inc_text = tk.Entry(self.root_tk,textvariable = self.incl_tax, font=('Helvetica',20,'normal'))
        self.display_date = tk.Label(self.root_tk, text="",  font=('Helvetica',20,'normal'))
        quantity_n = tk.Label(self.root_tk, text = 'Quantity', font=('Helvetica',20, 'bold'))
        Quantit = tk.Entry(self.root_tk,textvariable = self.quantity, font=('Helvetica',20,'normal'))
        imurl = tk.Label(self.root_tk, text = 'Image Url', font=('Helvetica',20, 'bold'))
        imgUrLink = tk.Entry(self.root_tk,textvariable = self.imageurl, font=('Helvetica',20,'normal'))
        
        othSku = tk.Label(self.root_tk, text = 'Other SKU(sku1/sku2/sku3)', font=('Helvetica',20, 'bold'))
        otsku = tk.Entry(self.root_tk,textvariable = self.otherSKU, font=('Helvetica',10,'normal'), width=50)
        variable_plt = StringVar(self.root_tk)
        variable_plt.set("Inventory")
        orderdate = tk.Button(self.root_tk,text = 'Select Date', command = self.calendarfnc)
        platfor = tk.OptionMenu(self.root_tk, variable_plt, "Inventory","Prime-KA")

                
        def get_order_data():
            self.sku = saku.get()
            self.quantity = int(Quantit.get())
            self.incl_tax = float(price_inc_text.get())
            self.imageurl = str(imgUrLink.get())
            self.otherSKU = str(otsku.get())
            self.platform = variable_plt.get()
            Quantit.delete(0, 'end')
            saku.delete(0, 'end')
            price_inc_text.delete(0, 'end')
            imgUrLink.delete(0, 'end')
            if self.otherSKU == 0:
                self.otherSKU = None
            if self.incl_tax != None:
                if self.ship_type == "Karnataka":# and self.transaction_type != "Inventory":
                    delat = ((1/1.12)*self.incl_tax)
                    self.cgst = (self.incl_tax - delat)/2# + ((-1 * 0.8928571429)*self.incl_tax)
                    self.sgst = (self.incl_tax - delat)/2
                    self.igst = 0
                if self.ship_type == "Not Karnataka":# and self.transaction_type != "Inventory":
                    self.igst = (1/1.12)*self.incl_tax
                    self.sgst = 0
                    self.cgst = 0
                price_before = self.incl_tax - self.cgst - self.sgst - self.igst                        
                if self.platform == "Prime-KA":
                    dframe = pd.read_csv(prime_file_path)
#                dframe = pd.read_excel(open(full_file_path, 'rb'),
#                    sheet_name='Prime-KA') 
                else:
                    dframe = pd.read_csv(csv_file_path)
                    # sheet_name='InventorySheet') 
                df = pd.DataFrame()
                df_display = pd.DataFrame(dframe, columns= REQUIRED_FIELDS)
                sku_match = df_display.index[df_display['SKU'] == self.sku].tolist()
                if len(sku_match) > 0:
                    for all_ind in sku_match:
                        df_display.loc[all_ind, 'Url'] = self.imageurl
                #if len(self.otherSKU)> 0:
                    #self.sku = (self.otherSKU.split('/')).extend(self.sku)
                dict_app = {'DATE': self.date,'Invoice No.': 'N/A', 
                           'Order ID ': 'N/A','Shipping': 'N/A' , 'SKU': self.sku, 
                          'Quantity':self.quantity,'Platform ': 'Purchase', 
                            'Incl_Tax':self.incl_tax,'SGST@6%':self.sgst,'CGST@6%':self.cgst,'IGST@12%':self.igst, 
                            'Price':round(price_before, 2), 'Name': self.AUTH_NAME,'Time':datetime.now(),'Url': self.imageurl,'otherSKU':self.otherSKU}
                df = df.append(dict_app, ignore_index=True)
                tk.messagebox.showinfo(title="Successfully Added", message="Order added successfully")

                df_save = pd.concat([df, df_display])
                if self.platform == "Prime-KA":
                    #df_save.to_excel(full_file_path,
                     #sheet_name='Prime-KA')
                    df_save.to_csv(prime_file_path)

                else:
                    df_save.to_csv(csv_file_path)
                    #df_save.to_excel(full_file_path,
                    # sheet_name='InventorySheet') 
        def exitroot():
            self.root_tk.destroy()
        def Backbutton():
            self.root_tk.destroy()
            self.root_tk =tk.Tk()
#            backwin.title('EnthAv0')

            #CurrentActiveWindow = root
            # setting the windows size
            #backwin.geometry("600x400")
            if self.platform == "Prime-KA":
                df_in = pd.read_csv(prime_file_path)
                #df_in = pd.read_excel(open(full_file_path, 'rb'),
                #     sheet_name='Prime-KA') 
            else:
                df_in = pd.read_csv(csv_file_path)

                #df_in = pd.read_excel(open(full_file_path, 'rb'),
                #     sheet_name='InventorySheet') 
            app = TestApp(root_tk=self.root_tk, df=df_in)
            app.show_table()
            
        submitButton = tk.Button(self.root_tk, command=get_order_data, text="Submit",height = 2, width = 6, bg='green', fg='white')
        ExitButton = tk.Button(self.root_tk, command=exitroot, text="Exit", height = 2, width = 6, bg='red', fg='white')
        BackButton = tk.Button(self.root_tk, command=Backbutton, text="View all Entries" , bg='yellow')
        MainButton = tk.Button(self.root_tk, command=self.Main_screen, text="Main Screen" , bg='blue', fg='white')
        submitButton['font'] = helv362
        ExitButton['font'] = helv362
        MainButton['font'] = helv362
        BackButton['font'] = helv362
        # Add to order df after gst 
        sku_n.grid(row=3,column=0)
        saku.grid(row=3,column=1)
        quantity_n.grid(row=4,column=0)
        Quantit.grid(row=4,column=1)
        price_incl_t.grid(row=5,column=0)
        price_inc_text.grid(row=5,column=1)
        self.display_date.grid(row=0, column=1)
        orderdate.grid(row=0,column=0)
        imurl.grid(row=6,column=0)
        imgUrLink.grid(row=6,column=1)
        othSku.grid(row=7,column=0)
        otsku.grid(row=7,column=1)
        submitButton.grid(row=8,column=0)
        BackButton.grid(row=8,column=2)
        platfor.grid(row=2,column=1)

        ExitButton.grid(row=8,column=1)
        MainButton.grid(row=9,column=1)
        self.root_tk.mainloop()

        #print(self.orderid, self.sku, self.platform, self.transaction_type, self.quantity, self.date, self.ship_type)
class Autenti(Frame):
    def __init__(self, root_tk):
        self.root_tk = root_tk
    def popup(self, msg):
        popup = tk.Tk()
        popup.wm_title("Warning!")
        label = tk.Label(popup, text=msg, font=('Helvetica',20,'normal'))
        label.pack(side="top", fill="x", pady=20)
        B1 = tk.Button(popup, text="Okay", command = popup.destroy)
        B1.pack()
        popup.mainloop()
    def launch(self): 
        launch=self.root_tk
        launch.geometry("700x200")
        launch.title('{}: Who is this?'.format(SOFTWARE_NAME))
        name=tk.StringVar()
        passwor=tk.StringVar()
        variable_NAME = StringVar(launch)
        variable_NAME.set("CHANDRAKALA")

        password_txt = tk.Label(launch, text = 'Password', font=('Helvetica',20, 'bold'))
        password_v = tk.Entry(launch,textvariable = passwor, font=('Helvetica',20,'normal'))
        name_choice = tk.OptionMenu(launch, variable_NAME,  "CHANDRAKALA", "VASU", "DEEPTHI")
        name_choice.config(width=20)

        def check_keys(passw, name_ks):
            dict_pass_name = {"CHANDRAKALA":"4862",
                              "VASU":"7532",
                              "DEEPTHI":"4523",
                              }
            if dict_pass_name[name_ks] == passw:
                return True
            else:
                return False
        
        def sumbit_aunt():
            passw = str(password_v.get())
            name_aut = str(variable_NAME.get())
            self.AUTH_NAME = name_aut
            if check_keys(passw, name_aut):
                launch.quit()
                self.run_app()
            else:
                self.popup("UGH! Oh Are you sure where and who you are?")

        def exitroot():
            launch.destroy()

        submitButton = tk.Button(launch, command=sumbit_aunt, text="Submit",height = 2, width = 6, bg='green', fg='white')
        ExitButton = tk.Button(launch, command=exitroot, text="Exit", height = 2, width = 6, bg='red', fg='white')

        submitButton['font'] = helv362
        ExitButton['font'] = helv362
        
        # Add to order df after gst 
        name_choice.grid(row=1,column=0)

        password_txt.grid(row=1,column=1)
        password_v.grid(row=1,column=2)
        
        submitButton.grid(row=9,column=0)
        ExitButton.grid(row=9,column=1)
        image = Image.open('logo.png')
        image = image.resize((156, 64))
        photo = ImageTk.PhotoImage(image)

        label = Label(self.root_tk, image = photo)
        label.image = photo
        label.grid(row=0)
        launch.mainloop()
        
    def run_app(self):
        self.root_tk.destroy()
        self.root_tk=tk.Tk()
        self.root_tk.wm_title("Welcome to {}!".format(SOFTWARE_NAME))

        self.root_tk.geometry("800x500")
        def update_sheet_drive():
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()

            drive = GoogleDrive(gauth)
            file1 = drive.CreateFile({"mimeType": "text/csv"})
            file1.SetContentFile(csv_file_path)
            file2 = drive.CreateFile({"mimeType": "text/csv"})
            file2.SetContentFile(prime_file_path)
            file1.Upload()
            file2.Upload()

        def redict_explore_prim():
            self.root_tk.destroy()
            #self.root_tk =tk.Tk()
            viewinev = ViewInventory()
            inv_df = viewinev.wrap_grop_inve('Prime-KA')
            
        def redict_explore():
            self.root_tk.destroy()
            #self.root_tk =tk.Tk()
            viewinev = ViewInventory()
            inv_df = viewinev.wrap_grop_inve('InventorySheet')
            #app2 = TestApp(root_tk=self.root_tk,df=inv_df)
            #app2.show_table()
        def sale():
            self.root_tk.destroy()
            self.root_tk=tk.Tk()
            UpdateInApp  = SaleClass(self.root_tk, self.AUTH_NAME)
            UpdateInApp.AddNewOrder()
            #update_sheet_drive()
        def purchase():
            self.root_tk.destroy()
            self.root_tk=tk.Tk()
            UpdateInApp  = PurchaseClass(self.root_tk, self.AUTH_NAME)
            UpdateInApp.AddNewOrder()
            #update_sheet_drive()
        def add_old_order():
            self.root_tk.destroy()
            self.root_tk=tk.Tk()
            UpdateInApp  = UpdateReturnOrder(self.root_tk, self.AUTH_NAME)
            UpdateInApp.UpdateOldOrder()
            #update_sheet_drive()
        def update_url_image():
            self.root_tk.destroy()
            self.root_tk=tk.Tk()
            UpdateInApp  = UpdateImage(self.root_tk, self.AUTH_NAME)
            UpdateInApp.updateurls()
            #update_sheet_drive()
        def all_tax_month():
            self.root_tk.destroy()  
            UpdateInApp  = AllTMonth()

        def all_tax_quart():
            self.root_tk.destroy()
            UpdateInApp  = AllTYear()

        def interactive_chat():
            self.root_tk.destroy()
            self.root_tk=tk.Tk()
            app = InteractiveChart(self.root_tk)
        SALE_ORDER = tk.Button(self.root_tk,text = 'Sale', command = sale,height = 5, width = 20, bg='blue', fg='white')
        purchase_order = tk.Button(self.root_tk,text = 'Purchase', command = purchase,height = 5, width = 20, bg='white', fg='black')
        add_return_order = tk.Button(self.root_tk,text = 'Enter Return Order', command = add_old_order, height = 5, width = 20, bg='red', fg='white')
        view_inve = tk.Button(self.root_tk,text = 'View Inventory', command = redict_explore, height = 5, width = 20, bg='green', fg='white')
        view_prime_inve = tk.Button(self.root_tk,text = 'View Prime Inventory', command = redict_explore_prim, height = 5, width = 20, bg='blue', fg='white')
        update_img = tk.Button(self.root_tk,text = 'Update Images', command = update_url_image, height = 5, width = 20, bg='yellow', fg='black')
        all_tax_m = tk.Button(self.root_tk,text = 'AllTax-Monthly', command = all_tax_month, height = 5, width = 20, bg='black', fg='white')
        all_tax_q = tk.Button(self.root_tk,text = 'AllTax-Quarterly', command = all_tax_quart, height = 5, width = 20, bg='brown', fg='yellow')
        inter_chat = tk.Button(self.root_tk,text = 'Visualize Sales', command = interactive_chat, height = 5, width = 20, bg='green', fg='white')

        backup = tk.Button(self.root_tk,text = 'Create Backup', command = update_sheet_drive, height = 5, width = 20, bg='yellow', fg='black')
        purchase_order['font'] = helv36
        SALE_ORDER['font'] = helv36
        add_return_order['font'] = helv36
        view_inve['font'] = helv36
        update_img['font'] = helv36
        backup['font'] = helv36
        view_prime_inve['font'] = helv36
        all_tax_m['font'] = helv36
        all_tax_q['font'] = helv36
        inter_chat['font'] = helv36
        image = Image.open('logo.png')
        image = image.resize((156, 64))
        photo = ImageTk.PhotoImage(image)

        label = Label(self.root_tk, image = photo)
        label.image = photo
        #launch the app

        #view_inventory_reup.grid(row=0,column=0)
        SALE_ORDER.grid(row=0,column=1)
        add_return_order.grid(row=1,column=1)
        view_inve.grid(row=2,column=1)
        view_prime_inve.grid(row=1,column=2)
        update_img.grid(row=3,column=1)
        purchase_order.grid(row=0,column=2)
        label.grid(row=0)
        backup.grid(row=2,column=2)
        all_tax_m.grid(row=3,column=2)
        all_tax_q.grid(row=0,column=3)
        inter_chat.grid(row=1,column=3)
        # performing an infinite loop
        # for the window to display
        self.root_tk.mainloop()
        print("Thank you using {}".format(SOFTWARE_NAME))
        print("Create by Bhavan Vasu")
        
main_app_tk=tk.Tk()
helv36 = tkFont.Font(family='Helvetica', size=14, weight='bold')
helv362 = tkFont.Font(family='Helvetica', size=10, weight='bold')
main_app_tk.title(SOFTWARE_NAME)
main_app_auten = Autenti(main_app_tk)

main_app_auten.launch()
main_app_tk.mainloop()
