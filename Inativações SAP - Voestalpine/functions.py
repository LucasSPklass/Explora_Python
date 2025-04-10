import os
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as xmlET
from xml.dom import minidom
from datetime import datetime
import logging

def pretty_xml(xml_string):
    reparsed = minidom.parseString(xml_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")

    pretty_xml = '\n'.join(line for line in pretty_xml.splitlines() if line.strip())
    
    result = '<?xml version="1.0" encoding="utf-8"?>' + pretty_xml[pretty_xml.index('?>') + 2:]

    return result

def log_init(PATH,):
    now = datetime.now()

    file_date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

    log_dir = os.path.join(PATH, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f'{file_date_time}.log')
    logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG, filemode='w')

def format_xml_body(index: int, root: xmlET.Element, item: pd.Series) -> bytes:

    item_material: str = str(item['MATERIAL']).strip()
    item_matl_type: str = str(item['MAT Type']).strip()
    item_description: str = str(item['MATERIALDESCRIPTION']).strip()
    item_longtext: str = str(item['MATERIALLONGTEXT']).strip()

    xml_item_description = xmlET.fromstring(item_description)
    xml_item_longtext = xmlET.fromstring(f'<itens>{item_longtext}</itens>')

    tag_material = root.find('HEADDATA/MATERIAL')
    tag_matl_type = root.find('HEADDATA/MATL_TYPE')
    tag_description = root.find('MATERIALDESCRIPTION')
    tag_longtext = root.find('MATERIALLONGTEXT')

    if item_material is None:
        raise ValueError(f'Material "None" para o índice: {index} do Dataframe')
    if item_matl_type is None:
        raise ValueError(f'Tipo do material "None" para o índice: {index} do Dataframe')
    if xml_item_description is None:
        raise ValueError(f'Descrição curta "None" para o índice: {index} do Dataframe')
    if xml_item_longtext is None:
        raise ValueError(f'Descrição longa "None" para o índice: {index} do Dataframe')

    tag_material.text = item_material
    tag_matl_type.text = item_matl_type
    tag_description.append(xml_item_description)
    for item in xml_item_longtext:
        tag_longtext.append(item)

    xml_str = xmlET.tostring(root, encoding='utf-8', xml_declaration=True)

    log_message = (
        f'XML alterado com as informações:\n'
        f'"HEADDATA/MATERIAL": {item_material}\n'
        f'"HEADDATA/MATL_TYPE": {item_matl_type}\n'
        f'"MATERIALDESCRIPTION": {item_description}\n'
        f'"MATERIALLONGTEXT": {item_longtext}\n'
    )

    logging.info(log_message)

    return xml_str

def fetch_data(xml_string: bytes) -> requests.Response:
    
    url = ""
    username = ""
    password = ""

    headers = {
        'Content-Type': 'application/xml',
        'DESTINATION': ''
    }

    try:
        response = requests.post(
            url,
            data=xml_string,
            headers=headers,
            auth=HTTPBasicAuth(username, password)
        )

        response.raise_for_status()

        logging.info(f'Status code: {response.status_code}')
        logging.debug(f'Headers da resposta: {response.headers}')
        logging.debug(f'Conteúdo da resposta:\n{response.text[:10000]}')  

    except requests.exceptions.RequestException as e:
        logging.error(f'Erro na requisição: {e.strerror}')
        raise

    return response
