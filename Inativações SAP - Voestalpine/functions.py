import pandas as pd
import requests
import xml.etree.ElementTree as xmlET
from xml.dom import minidom

from datetime import datetime
import logging

# Deixa o XML legível (para um humano)
def pretty_xml(xml_string):
    reparsed = minidom.parseString(xml_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")

    pretty_xml = '\n'.join(line for line in pretty_xml.splitlines() if line.strip())
    
    result = '<?xml version="1.0" encoding="utf-8"?>' + pretty_xml[pretty_xml.index('?>') + 2:]

    return result


# Configuração do arquivo .log
def log_init(PATH):
    now = datetime.now()

    date_time = now.strftime("%Y/%m/%d %H:%M:%S")
    file_date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

    logging.basicConfig(filename=f'{PATH}logs/exec/{file_date_time}.log', encoding='utf-8', level=logging.DEBUG, filemode='w')
    logging.info(f'Agora são: {date_time}')


# Cria o body XML para a request
def format_xml_body(index: int, root: xmlET.Element, item: pd.Series) -> bytes:

    # SET UP

    # Variáveis de cada ITEM da tabela
    item_material: str = str(item['MATERIAL'].strip())
    item_matl_type: str = str(item['MAT Type'].strip())
    item_description: str = str(item['MATERIALDESCRIPTION'].strip())
    item_longtext: str = str(item['MATERIALLONGTEXT'].strip())

    # Passa as descrições como XML
    xml_item_description = xmlET.fromstring(item_description)
    xml_item_longtext = xmlET.fromstring(f'<itens>{item_longtext}</itens>')

    # Local no XML das tags: material, material type, descrição curta e descrição longa
    tag_material = root.find('HEADDATA/MATERIAL')
    tag_matl_type = root.find('HEADDATA/MATL_TYPE')
    tag_description = root.find('MATERIALDESCRIPTION')
    tag_longtext = root.find('MATERIALLONGTEXT')

    # Verifica se as informações existem no Dataframe // Uma verificação mais robusta seria interessante
    if item_material is None:
        raise ValueError(f'Material "None" para o índice: {index} do Dataframe')
    if item_matl_type is None:
        raise ValueError(f'Tipo do material "None" para o índice: {index} do Dataframe')
    if xml_item_description is None:
        raise ValueError(f'Descrição curta "None" para o índice: {index} do Dataframe')
    if xml_item_longtext is None:
        raise ValueError(f'Descrição longa "None" para o índice: {index} do Dataframe')


    # EXECUÇÃO

    # Altera o texto das tags
    tag_material.text = item_material
    tag_matl_type.text = item_matl_type
    tag_description.append(xml_item_description)
    for item in xml_item_longtext:
        tag_longtext.append(item)

    xml_str = xmlET.tostring(root, encoding='utf-8', xml_declaration=True)

    # Logging
    log_message = (
        f'XML alterado com as informações:\n'
        f'"HEADDATA/MATERIAL": {item_material}\n'
        f'"HEADDATA/MATL_TYPE": {item_matl_type}\n'
        f'"MATERIALDESCRIPTION": {item_description}\n'
        f'"MATERIALLONGTEXT": {item_longtext}\n'
    )

    logging.info(log_message)

    return xml_str


# Faz uma request e retorna sua resposta
def fetch_data(xml_string: bytes) -> requests.Response:
    # Variáveis
    url = ""

    # Request
    response = requests.post(url, data=xml_string, headers={'Content-Type': 'application/xml'})

    response.raise_for_status()

    # Logging
    logging.info(f'Status code da request: {response.status_code}') # ALTERAR PARA FAZER UM LOG MELHOR DA RESPOSTA (e não só do status como eu fiz)

    return response
