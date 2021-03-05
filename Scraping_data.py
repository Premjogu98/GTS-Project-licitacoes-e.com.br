# This Python file uses the following encoding: utf-8
import time
from datetime import datetime
import Global_var
import sys, os
import urllib.request
import urllib.parse
import re
import string
import time
import requests
import html
from Insert_On_Datbase import insert_in_Local
import wx
app = wx.App()

def remove_html(string_s):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', string_s)
    return cleantext
def Scraping_data(get_htmlSource,link):
    a = False
    while a == False:
        try:
            SegField = []
            for data in range(45):
                SegField.append('')
            # Email
            custom_get_htmlSource = html.unescape(str(get_htmlSource)).replace('\n',' ').replace('\t','')
            SegField[1] = ''

            # Address
            
            SegField[2] = 'Brazil<BR>[Disclaimer : For Exact Organization/Tendering Authority details, please refer the tender notice.]'

            # Tender Details
            Title = custom_get_htmlSource.partition('Resumo da licitação</label>')[2].partition('</div>')[0].strip()
            if Title != "":
                main_title = remove_html(Title)
                main_title = string.capwords(str(main_title))  # string in capitalize
                SegField[19] = main_title

            Close_Date = custom_get_htmlSource.partition('Limite acolhimento de propostas</label>')[2].partition('</div>')[0].strip()
            Close_Date = remove_html(Close_Date).strip()
            if Close_Date != '':
                datetime_object = datetime.strptime(Close_Date, "%d/%m/%Y-%H:%M")
                mydate = datetime_object.strftime("%Y-%m-%d")
                SegField[24] = mydate
            else:
                SegField[24] = ''

            SegField[7] = 'BR'
            
            purchaser = custom_get_htmlSource.partition('Cliente</label>')[2].partition('</div>')[0].strip()
            if purchaser != "":
                purchaser = remove_html(purchaser).strip()
                purchaser = string.capwords(str(purchaser))
                purchaser = html.unescape(str(purchaser))
                SegField[12] = purchaser.upper().strip()
            
            Tender_id = custom_get_htmlSource.partition('Edital</label>')[2].partition('</div>')[0].strip()
            if Tender_id !="":
                Tender_id = remove_html(Tender_id).strip()
                SegField[13] = str(Tender_id).strip()
            
            Driving_way = custom_get_htmlSource.partition('Forma de condução</label>')[2].partition('</div>')[0].strip()
            if Driving_way !="":
                Driving_way = remove_html(Driving_way).strip()
            
            Bidding_language = custom_get_htmlSource.partition('Idioma da licitação</label>')[2].partition('</div>')[0].strip()
            if Bidding_language !="":
                Bidding_language = remove_html(Bidding_language).strip()
            
            Bidding_currency = custom_get_htmlSource.partition('Moeda da licitação</label>')[2].partition('</div>')[0].strip()
            if Bidding_currency !="":
                Bidding_currency = remove_html(Bidding_currency).strip()
            
            Proposal_currency = custom_get_htmlSource.partition('Moeda da proposta</label>')[2].partition('</div>')[0].strip()
            if Proposal_currency !="":
                Proposal_currency = remove_html(Proposal_currency).strip()
            ncb_icb_main = 'icb'
            Scope_of_the_dispute = custom_get_htmlSource.partition('Abrangência da disputa</label>')[2].partition('</div>')[0].strip()
            if Scope_of_the_dispute !="":
                Scope_of_the_dispute = remove_html(Scope_of_the_dispute).strip()
                if Scope_of_the_dispute == 'Nacional':
                    ncb_icb_main = 'ncb'
            SegField[18] = f"{str(SegField[19])}<br>\nForma de condução: {str(Driving_way)}<br>\nIdioma da licitação: {str(Bidding_language)}<br>\nMoeda da licitação: {str(Bidding_currency)}<br>\nMoeda da proposta: {str(Proposal_currency)}<br>\nAbrangência da disputa: {str(Scope_of_the_dispute)}"
            SegField[14] = '2'
            SegField[22] = "0"
            SegField[26] = "0.0"
            SegField[27] = "0"   # Financier
            SegField[28] = str(link)
            SegField[20] = ""
            SegField[21] = ""
            SegField[42] = SegField[7]
            SegField[43] = ""

            SegField[31] = 'licitacoes-e.com.br'

            for SegIndex in range(len(SegField)):
                print(SegIndex, end=' ')
                print(SegField[SegIndex])
                SegField[SegIndex] = html.unescape(str(SegField[SegIndex]))
                SegField[SegIndex] = str(SegField[SegIndex]).replace("'", "''")

            if len(SegField[19]) >= 200:
                SegField[19] = str(SegField[19])[:200]+'...'

            if len(SegField[18]) >= 1500:
                SegField[18] = str(SegField[18])[:1500]+'...'

            
            if SegField[19] == '':
                wx.MessageBox(' Short Desc Blank ','bzp.uzp.gov.pl', wx.OK | wx.ICON_INFORMATION)
            else:
                check_date(get_htmlSource, SegField,ncb_icb_main)
                
                # create_filename(get_htmlSource, SegField,ncb_icb_main)
            a = True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",
                  exc_tb.tb_lineno)
            a = False


def check_date(get_htmlSource, SegField,ncb_icb_main):
    deadline = str(SegField[24])
    curdate = datetime.now()
    curdate_str = curdate.strftime("%Y-%m-%d")
    try:
        if deadline != '':
            datetime_object_deadline = datetime.strptime(deadline, '%Y-%m-%d')
            datetime_object_curdate = datetime.strptime(curdate_str, '%Y-%m-%d')
            timedelta_obj = datetime_object_deadline - datetime_object_curdate
            day = timedelta_obj.days
            if day > 0:
                insert_in_Local(get_htmlSource, SegField,ncb_icb_main)
            else:
                print("Expired Tender")
                Global_var.expired += 1
        else:
            print("Deadline Not Given")
            Global_var.deadline_Not_given += 1
    except Exception as e:
        exc_type , exc_obj , exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Error ON : " , sys._getframe().f_code.co_name + "--> " + str(e) , "\n" , exc_type , "\n" , fname , "\n" ,exc_tb.tb_lineno)