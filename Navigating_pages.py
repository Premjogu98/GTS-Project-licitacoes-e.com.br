from selenium import webdriver
import time
import html
import sys, os
from datetime import datetime,timedelta
import Global_var
import wx
import string
import re
import string
import pymysql.cursors
from Scraping_data import Scraping_data
app = wx.App()
def chromedriver():
    while True:
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_extension('C:\\Translation EXE\\BrowsecVPN.crx')
            # chrome_options.add_extension('F:\\Translation EXE\\Rumolacaptcha.crx')
            browser = webdriver.Chrome(chrome_options=chrome_options,executable_path=str(f"C:\\Translation EXE\\chromedriver.exe"))
            browser.maximize_window()
            wx.MessageBox(' -_-  Add Extension and Then Click On OK BUTTON -_- ', 'Contract Award GUI Google Translationlicitacoes-e.com.br', wx.OK | wx.ICON_ERROR)
            time.sleep(15)
            browser.get("http://www.licitacoes-e.com.br/aop/pesquisar-licitacao.aop?opcao=preencherPesquisar")
            time.sleep(4)
            # wx.MessageBox(' -_- if there is any problem on page load then refresh page -_- ', 'licitacoes-e.com.br', wx.OK | wx.ICON_ERROR)
            navigate_things(browser)
        except:
            wx.MessageBox(' -_- Error while navigate link (chromedriver Function) -_- ', 'licitacoes-e.com.br', wx.OK | wx.ICON_ERROR)
            time.sleep(4)
    
def navigate_things(browser):
    error_found = True
    while error_found == True:
        try:
            wx.MessageBox(' -_- Please Fill Captcha if page was not loaded properly then refresh page (navigate_things Function) -_- ', 'licitacoes-e.com.br', wx.OK | wx.ICON_ERROR)
            time.sleep(5)

            for select_publication in browser.find_elements_by_xpath('//*[@id="licitacaoPesquisaSituacaoForm"]/div[5]/span/input'):
                select_publication.clear()
                select_publication.send_keys('Publicada')
                break     
            for search in browser.find_elements_by_xpath('//*[@value="pesquisar"]'):
                search.click()
                time.sleep(5)    
                break
            error_found = False
            collect_link(browser)
        except:
            wx.MessageBox(' -_- Please Refresh Page Then Click On OK (navigate_things Function) -_- ', 'licitacoes-e.com.br', wx.OK | wx.ICON_ERROR)
            time.sleep(5)
            error_found = True

def collect_link(browser):
    table_found_or_not = True
    while table_found_or_not == True:
        for _ in browser.find_elements_by_xpath('//*[@id="tCompradores"]'):
            table_found_or_not = False
            break
        if table_found_or_not == False:
            break
        else:
            wx.MessageBox(' -_- Please Refresh Page Then Click On OK Or If Captcha (Collect_link Function) -_- ', 'licitacoes-e.com.br', wx.OK | wx.ICON_ERROR)
            time.sleep(5)
    try:
        mydb_Local = pymysql.connect(host='185.142.34.92',user='ams',password='TgdRKAGedt%h',db='tenders_db',charset='utf8',cursorclass=pymysql.cursors.DictCursor)
        mycursor = mydb_Local.cursor()
    except:
        print('Error On Database Connection')
        wx.MessageBox(' -_- Error On Database Connection (Collect_link Function) -_-  ', 'licitacoes-e.com.br ', wx.OK | wx.ICON_ERROR)
    collect_link_list = []
    link_no = 1
    next_page_end = True
    while next_page_end == True:
        for links in browser.find_elements_by_xpath('//*[@id="tCompradores"]/tbody/tr/td[4]/a'):
            link_id = links.get_attribute('id').strip()
            custom_link = f"http://www.licitacoes-e.com.br/aop/consultar-detalhes-licitacao.aop?numeroLicitacao={str(link_id)}&opcao=consultarDetalhesLicitacao"
            mycursor.execute(f"SELECT * FROM `tenders_db`.`americas_tenders_tbl` WHERE tender_doc_file = '{str(custom_link)}'")
            results = mycursor.fetchall()
            if len(results) > 0:
                print('Duplicate Link')
            else:
                print(f'Link NO {str(link_no)} = {str(custom_link)}')
                print('New Link')
                collect_link_list.append(custom_link)
                link_no += 1
        while True:
            try:
                for next_page in browser.find_elements_by_xpath('//*[@id="tCompradores_next"]'):
                    browser.execute_script("arguments[0].scrollIntoView();", next_page)
                    next_page_outer = next_page.get_attribute('outerHTML').replace('\n','').strip()
                    if 'ui-state-disabled' not in next_page_outer:
                        next_page.click()
                        time.sleep(2)
                        break
                    else:
                        next_page_end = False
                        break
                break
            except:
                print('Error On Next Page')
                time.sleep(3)
    navigate_link(browser,collect_link_list)
def navigate_link(browser,collect_link_list):
    print(f'\nTotal Link Collected: {str(len(collect_link_list))}\n')
    for link in collect_link_list:
        browser.get(link)
        wx.MessageBox(' -_- Please Fill Captcha Then Click On OK BUTTON (navigate_link Function) -_- ', 'licitacoes-e.com.br ', wx.OK | wx.ICON_ERROR)
        while True:
            outer_html = ''
            for Web_page in browser.find_elements_by_xpath('//*[@id="divConsultarDetalhesLicitacao"]'):
                outer_html = Web_page.get_attribute('outerHTML').strip()
                outer_html = outer_html.replace('src="../','src="http://www.licitacoes-e.com.br/aop/').replace('class="dropdownBB">','class="dropdownBB open">')
                break
            if outer_html != '':  
                Scraping_data(outer_html,link)
                print(f" Total: {str(len(collect_link_list))} Duplicate: {str(Global_var.duplicate)} Inserted: {str(Global_var.inserted)} Deadline Not Given: {str(Global_var.deadline_Not_given)} expired: {str(Global_var.expired)} QC Tender: {str(Global_var.QC_Tender)}\n")
                break
            else:
                wx.MessageBox(' -_- Please Fill Captcha Then Click On OK BUTTON (navigate_link Function) -_- ', 'licitacoes-e.com.br ', wx.OK | wx.ICON_ERROR)
    browser.close()
    wx.MessageBox(f' Total: {str(len(collect_link_list))}\n Duplicate: {str(Global_var.duplicate)}\n Inserted: {str(Global_var.inserted)}\n Deadline Not Given: {str(Global_var.deadline_Not_given)}\n expired: {str(Global_var.expired)}\n QC Tender: {str(Global_var.QC_Tender)} ', 'licitacoes-e.com.br ', wx.OK | wx.ICON_INFORMATION)
    sys.exit()

chromedriver()