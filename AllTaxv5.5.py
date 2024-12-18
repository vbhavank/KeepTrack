#!/usr/bin/env python3

#TODO: RAJSRI ADD breakdown and overall
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import PySimpleGUI as sg
from datetime import datetime

SOFT_NAME = "AllTax Monthly © version 5.5"

# datetime object containing current date and time
now = datetime.now()

#pd.set_option('display.width', 1000)
Fk_REQUIRED_FIELDS = ['Taxable Value (Final Invoice Amount -Taxes)', \
                   'IGST Amount','CGST Amount', 'SGST Amount (Or UTGST as applicable)',
                  'TCS IGST Amount','TCS SGST Amount','TCS CGST Amount','Customer\'s Delivery State']

AMZ_REQUIRED_FIELDS = ['Tax Exclusive Gross','Ship To State','Cgst Tax','Sgst Tax','Igst Tax','Shipping Cgst Tax', \
                      'Shipping Sgst Tax','Shipping Igst Tax','Tcs Cgst Amount','Tcs Sgst Amount','Tcs Igst Amount']

RAJ_REQUIRED_FIELDS = ['Invoice Date','Invoice Number', 'Taxable Value','Buyer\'s GST Number', 'Place of Supply','IGST Amount',\
             'CGST Amount', 'SGST Amount']

Amazon_purchase_fields = ['TCS CGST Amount', 'TCS SGST Amount', 'TCS IGST Amount', 'Shipping Cgst Tax', \
                      'Shipping Sgst Tax','Shipping Igst Tax']

Flipkart_purchase_fields = ['TCS CGST Amount', 'TCS SGST Amount', 'TCS IGST Amount']

sg.theme("DarkBrown2")
fname = 'logo.png'

#with open('{}'.format( fname)) as fh:
#    image1 = fh.read()

layout = [[sg.T("")],[sg.Image(filename=fname, size=(300, 120))], \
         [sg.Text("Choose FlipKart Sales Report(.xlsx): "), sg.Input(), sg.FileBrowse(key="-IN1-")], \
          [sg.Text("Choose Amazon Sales Report(.csv): "), sg.Input(), sg.FileBrowse(key="-IN2-")], \
          [sg.Text("Choose RAJSHRI Report(.xlsx): "), sg.Input(), sg.FileBrowse(key="-IN3-")], \
            [sg.Text("Choose Final Report Destination: "), sg.Input(key="-IN4-" ,change_submits=True), sg.FolderBrowse(key="-IN4-")], \
          [sg.Button('Load and Summarize Reports'), sg.Exit()]]

###Building Window
window = sg.Window('{} (created by Bhavan Vasu)'.format(SOFT_NAME), layout, size=(700,350))
    
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event=="Exit":
        print("Thank you for using {}".format(SOFT_NAME))
        sys.exit("Created By Bhavan Vasu")
        break
    elif event == "Load and Summarize Reports":
        fk_filename = values["-IN1-"]
        amazon_filename = values["-IN2-"]
        raj_filename = values["-IN3-"]
        save_path = values["-IN4-"]
        try:
            assert fk_filename.split('.')[-1] == 'xlsx'
            try:
                assert amazon_filename.split('.')[-1] == 'csv'
                try:
                    assert raj_filename.split('.')[-1] == 'xlsx'
                    try:
                        assert  os.path.isdir(save_path)
                        break
                    except:
                        sg.popup('Entered Destination path {} is not a folder, Please try again!'.format(save_path))                    
                except:
                    sg.popup('Entered path {} is not .xlsx, Please try again!'.format(raj_filename))
            except:
                sg.popup('Entered path {} is not .csv, Please try again!'.format(amazon_filename))
        except:
            sg.popup('Entered path {} is not .xlsx, Please try again!'.format(fk_filename))
window.close()

##layout = [[sg.T("")], [sg.Text("Choose Amazon Sales Report(.csv): "), sg.Input(), sg.FileBrowse(key="-IN-")],[sg.Button("Load Amazon Orders"), sg.Exit()]]
##
#####Building Window
##window = sg.Window('{} (created by Bhavan Vasu)'.format(SOFT_NAME), layout, size=(700,150))
##    
##while True:
##    event, values = window.read()
##    if event == sg.WIN_CLOSED or event=="Exit":
##        print("Thank you for using {}".format(SOFT_NAME))
##        sys.exit("Created By Bhavan Vasu")
##        break
##    
##    elif event == "Load Amazon Orders":
##        amazon_filename = values["-IN-"]
##        try:
##            assert amazon_filename.split('.')[-1] == 'csv'
##            break
##        except:
##            sg.popup('Entered path {} is not .csv, Please try again!'.format(amazon_filename))
##window.close()
##
##
##layout = [[sg.T("")], [sg.Text("Choose RAJASHRI Sales Report(.xlsx): "), sg.Input(), sg.FileBrowse(key="-IN-")],[sg.Button("Load RAJSHRI Sales"), sg.Exit()]]
##
#####Building RAJSHRI Window
##window = sg.Window('{} (created by Bhavan Vasu)'.format(SOFT_NAME), layout, size=(700,150))
##    
##while True:
##    event, values = window.read()
##    if event == sg.WIN_CLOSED or event=="Exit":
##        print("Thank you for using {}".format(SOFT_NAME))
##        sys.exit("Created By Bhavan Vasu")
##        break
##    
##    elif event == "Load RAJSHRI Sales":
##        raj_filename = values["-IN-"]
##        try:
##            assert raj_filename.split('.')[-1] == 'xlsx'
##            break
##        except:
##            sg.popup('Entered path {} is not .xlsx, Please try again!'.format(raj_filename))
##window.close()


##layout = [[sg.T("")], [sg.Text("Choose Final Report Destination: "), sg.Input(key="-IN2-" ,change_submits=True), sg.FolderBrowse(key="-IN-")],[sg.Button("Generate Report"), sg.Exit()]]
##
#####Building Window
##window = sg.Window('{} (created by Bhavan Vasu)'.format(SOFT_NAME), layout, size=(700,150))
##    
##while True:
##    event, values = window.read()
##    if event == sg.WIN_CLOSED or event=="Exit":
##        print("Thank you for using {}".format(SOFT_NAME))
##        sys.exit("Created By Bhavan Vasu")
##        break
##    
##    elif event == "Generate Report":
##        save_path = values["-IN-"]
##        break
##window.close()

writer = pd.ExcelWriter(os.path.join(save_path, 'Report_{}_{}_{}.xlsx'.format(now.month, now.day, now.year)),engine='xlsxwriter')   

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

def save_daraframe(dataf, sheet_name):
    dataf.to_excel(writer, sheet_name=sheet_name) 
    
def print_separator():
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

def get_flipkart(fk_filename, Fk_REQUIRED_FIELDS):
    final_Path = fk_filename
    xls = pd.ExcelFile(final_Path)
    df1 = pd.read_excel(xls, 'Sales Report')
    df = pd.DataFrame(df1, columns= Fk_REQUIRED_FIELDS)
      
    df.rename(columns={"Customer's Delivery State":"Place of Supply", "SGST Amount (Or UTGST as applicable)": "SGST Amount", "Taxable Value (Final Invoice Amount -Taxes)": "Taxable Value"}, inplace=True)
    # df["Customer's Delivery State"] = df["Place of Supply"].str.lower()
    df["Place of Supply"] = df["Place of Supply"].str.lower()
    states = df[ 'Place of Supply'].unique()
    n_by_state = df.groupby("Place of Supply").sum().round(decimals=2)
    #import pdb
    #pdb.set_trace()
    tot = n_by_state.sum(axis=0)
    tot = tot.append(pd.Series(df.loc[df['IGST Amount'] != 0,['Taxable Value']]['Taxable Value'].sum(), \
                           index=['IGST Taxable Value']))
    tot.drop(Flipkart_purchase_fields, inplace=True)
    print("================================ FLIPKART Total ============================================")
    print(tot)
    print('\n')
    save_daraframe(tot, "Flipkart-Overall")

    #n_by_state[""].plot.pie(subplots=True, figsize=(8, 8), fontsize=20,title='Final Invoice Amount vs States');
    #plt.show()
    with pd.option_context('display.max_columns', len(Fk_REQUIRED_FIELDS) - 1):  
        print("================================ FLIPKART State Breakdown ============================================")

        new_n_by_state = n_by_state.drop(Flipkart_purchase_fields, axis=1)
        print(repr(new_n_by_state.head(len(states))))
        print_separator()
        print('\n')
        save_daraframe(new_n_by_state, "Flipkart-State")
    return n_by_state, df, tot
    
def amazn(amazon_filename, AMZ_REQUIRED_FIELDS, Amazon_purchase_fields): 
    #final_Path = os.path.join(os.path.expanduser('~/Downloads'), '{}.csv'.format(amazon_filename))
    final_Path = amazon_filename
    df = pd.read_csv(final_Path)
    df_clean = df.dropna(subset=['Seller Gstin'])
    df2 = pd.DataFrame(df_clean, columns= AMZ_REQUIRED_FIELDS)
    df2.rename(columns={"Ship To State":"Place of Supply"}, inplace=True)
    df2["Place of Supply"] = df2["Place of Supply"].str.lower()
    states = df2[ 'Place of Supply'].unique()
    n_by_state = df2.groupby("Place of Supply").sum().round(decimals=2)
    n_by_state.rename(columns={"Tax Exclusive Gross":"Taxable Value","Cgst Tax": "CGST Amount", "Sgst Tax":"SGST Amount", "Igst Tax":"IGST Amount", "Tcs Cgst Amount":"TCS CGST Amount", "Tcs Sgst Amount":"TCS SGST Amount","Tcs Igst Amount":"TCS IGST Amount"}, inplace=True)
    this_n_by_state = n_by_state.drop(Amazon_purchase_fields, axis=1)

    tot = this_n_by_state.sum(axis=0)
    tot = tot.append(pd.Series(df2.loc[df2['Igst Tax'] != 0,['Tax Exclusive Gross']]['Tax Exclusive Gross'].sum(), \
                           index=['IGST Taxable Value']))
    print("================================ AMAZON Total ============================================")
    print(tot)
    print('\n')
    save_daraframe(tot, "Amazon-Sales-Overall")

    with pd.option_context('display.max_columns', len(AMZ_REQUIRED_FIELDS) - 1):  
        print("================================ AMAZON State Breakdown ============================================")
        print(repr(this_n_by_state.head(len(states))))
        print_separator()
        print('\n')
        save_daraframe(this_n_by_state, "Amazon-State")
    return n_by_state, df2, tot

def get_RAJSHRI_sales(raj_filename, RAJ_REQUIRED_FIELDS): 
    final_Path = raj_filename
    xls = pd.ExcelFile(final_Path)
    df = pd.read_excel(xls, 'SalesReport')
    df1 = pd.DataFrame(df, columns= RAJ_REQUIRED_FIELDS)
    df1["Place of Supply"] = df1["Place of Supply"].str.lower()
    states = df1[ 'Place of Supply'].unique()
    n_by_state = df1.groupby("Place of Supply").sum().round(decimals=2)
    n_by_state.drop('Invoice Number', inplace=True, axis=1)
    tot = n_by_state.sum(axis=0)
    print("================================ RAJSHRI Sales Total ============================================")
    print(tot)
    print('\n')

    save_daraframe(tot, "RAJSHRI-Sales-Overall")

    with pd.option_context('display.max_columns', len(RAJ_REQUIRED_FIELDS) - 1):  
        print("================================ RAJSHRI Sales State Breakdown ============================================")
        print(repr(n_by_state.head(len(states))))
        print_separator()
        print('\n')
        save_daraframe(n_by_state, "RAJSHRI-Sales-State")
    return n_by_state, df1, tot

def get_RAJSHRI_purchase(raj_filename, amaz_df, RAJ_REQUIRED_FIELDS, Amazon_purchase_fields, fk_state, Flipkart_purchase_fields): 
    final_Path = raj_filename
    xls = pd.ExcelFile(final_Path)
    Amazon_purchase_fields = ['TCS CGST Amount', 'TCS SGST Amount', 'TCS IGST Amount', 'Shipping Cgst Tax', \
                      'Shipping Sgst Tax','Shipping Igst Tax']
    amaz_df_state = pd.DataFrame(amaz_df, columns= Amazon_purchase_fields)
    fk_df_state = pd.DataFrame(fk_state, columns= Flipkart_purchase_fields)
    RAJ_REQUIRED_FIELDS[RAJ_REQUIRED_FIELDS.index('Buyer\'s GST Number')] = 'Seller\'s GST Number'
    df = pd.read_excel(xls, 'PurchaseReport')
    df1 = pd.DataFrame(df, columns= RAJ_REQUIRED_FIELDS)
    df1["Place of Supply"] = df1["Place of Supply"].str.lower()
    states = df1[ 'Place of Supply'].unique()
    n_by_state = df1.groupby("Place of Supply").sum().round(decimals=2)
    result_state = pd.concat([n_by_state, fk_df_state, amaz_df_state], axis=0)
    n_by_state = result_state.groupby("Place of Supply").sum().round(decimals=2)
    tot = n_by_state.sum(axis=0)
    tot = tot.append(pd.Series(df1.loc[df1['IGST Amount'] != 0,['Taxable Value']]['Taxable Value'].sum(), \
                           index=['IGST Taxable Value']))
    print("================================ Overall Purchase Total ============================================")
    print(tot)
    print('\n')
    save_daraframe(tot, "Overall Purchase")

    with pd.option_context('display.max_columns', (len(RAJ_REQUIRED_FIELDS) + len(Amazon_purchase_fields)) - 1):  
        print("================================ Overall Purchase State Breakdown ============================================")
        print(repr(n_by_state))
        print_separator()
        print('\n')
        save_daraframe(n_by_state, "Overall Purchase-State")
    return n_by_state, df1, tot

#try:
#    assert fk_filename
fk_state, fk_df, fk_total = get_flipkart(fk_filename, Fk_REQUIRED_FIELDS)
#except:
#    fk_state = pd.DataFrame()
#    pass

#try:
#    assert amazon_filename
amzn_state, amz_df, amz_total = amazn(amazon_filename, AMZ_REQUIRED_FIELDS, Amazon_purchase_fields)
#except:
#    amzn_state = pd.DataFrame()
#    pass

#try:
#    assert raj_filename
raj_state, raj_df, raj_total = get_RAJSHRI_sales(raj_filename, RAJ_REQUIRED_FIELDS)

raj_pur_state, raj_pur_df, _ = get_RAJSHRI_purchase(raj_filename, amzn_state, RAJ_REQUIRED_FIELDS, Amazon_purchase_fields, fk_state, Flipkart_purchase_fields)
#except:
#    raj_state = pd.DataFrame()
#    pass

v2_summary = pd.concat([fk_state, amzn_state, raj_state], sort=True).groupby("Place of Supply").sum()
v2_summary.drop(Amazon_purchase_fields,inplace=True, axis=1)
#v2_summary["Invoice Amount"].plot.pie(subplots=True, figsize=(8, 8), fontsize=20,title='Final Invoice Amount vs States');
#plt.show()
max_display = max(len(AMZ_REQUIRED_FIELDS), len(Fk_REQUIRED_FIELDS), len(RAJ_REQUIRED_FIELDS))

with pd.option_context('display.max_columns', max_display):  
    print("================================ Overall Sales State Breakdown ============================================")
    print(repr(v2_summary))
    save_daraframe(v2_summary, "Overall Sales-State")
    print('\n')


try:
    assert raj_total['IGST Amount']
except:
    raj_total['IGST Amount'] = 0
try:
    assert raj_total['IGST Taxable Value']
except:
    raj_total['IGST Taxable Value'] = 0

tot = fk_total + amz_total + raj_total
print("================================ Overall Sales Total ============================================")
print(tot)
print('\n')
save_daraframe(tot, "Overall Sales Total")
writer.save()

# IGST Taxable overall sales
