import os
import json
import pandas as pd
import xml.etree.ElementTree as xmlET
from datetime import datetime
import logging
import traceback
import xml.dom.minidom
from functions import log_init, pretty_xml, format_xml_body, fetch_data, create_config_file

def main():
    PATH = os.path.dirname(os.path.abspath(__file__))
    PATH = PATH.replace('\\', '/') + '/'

    log_init(PATH)

    excel_file: str = "itens/EXEMPLO-MOCK-Requisicoes.xlsx"

    df_itens: pd.DataFrame = pd.read_excel(PATH + excel_file, engine="openpyxl", dtype=str)

    config_file_path = f'{PATH}config.json'

    if not os.path.exists(config_file_path):
        create_config_file(config_file_path)

    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
    
    url = config.get('fetch_URL')
    username = config.get('fetch_username')
    password = config.get('fetch_password')

    for index, item in df_itens.iterrows():

        template = xmlET.parse(PATH + "xml/template.xml")
        template_root = template.getroot()

        template_root.set('xmlns:urn', 'urn:sap-com:document:sap:soap:functions:mc-style')
        template_root.set('xmlns:soapenv', 'http://schemas.xmlsoap.org/soap/envelope/')
        
        item_material: str = str(item['MATERIAL']) 

        logging.info(f'Iniciando formatação XML para: {item_material}')
        xml_str = format_xml_body(index, template_root, item)

        file_date_time = datetime.now().strftime("%Y-%m-%d")

        log_xml_dir = os.path.join(f'{PATH}xml/', 'requests')
        os.makedirs(log_xml_dir, exist_ok=True)

        with open(log_xml_dir + f'/Request_{item_material}_{file_date_time}.xml', 'w') as f:
            f.write(pretty_xml(xml_str.decode('utf-8')))

        logging.info(f'Iniciando request para: {item_material}')
        response = fetch_data(xml_str, url, username, password)

        xml_dom = xml.dom.minidom.parseString(response.text)
        prettied_xml = xml_dom.toprettyxml(indent="  ")

        file_name_response = f'/Response_{item_material}_{file_date_time}'

        with open(log_xml_dir + f'{file_name_response}.xml', 'w', encoding='utf-8') as file:
            file.write(prettied_xml)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception(f'Erro de exceção na função main.\n')
        traceback.print_exc()
