import os
import pandas as pd
import xml.etree.ElementTree as xmlET

from datetime import datetime
import logging
import traceback

from functions import log_init, pretty_xml, format_xml_body, fetch_data

def main():
    # Diretório desse arquivo .py
    PATH = os.path.dirname(os.path.abspath(__file__))
    PATH = PATH.replace('\\', '/') + '/'

    # Começa o processo de logging
    log_init(PATH)

    # Localização do arquivo Excel (em relação ao diretório PATH)
    excel_file: str = "itens/EXEMPLO-MOCK-Requisicoes.xlsx"

    # Dataframe (tabela) com os dados das requests
    df_itens: pd.DataFrame = pd.read_excel(PATH + excel_file, engine="openpyxl", dtype=str)

    # Parse do template xml
    template = xmlET.parse(PATH + "xml/template.xml")
    template_root = template.getroot()

    # Insere os namespaces na root do xml
    template_root.set('xmlns:urn', 'urn:sap-com:document:sap:soap:functions:mc-style')
    template_root.set('xmlns:soapenv', 'http://schemas.xmlsoap.org/soap/envelope/')

    # FOR LOOP das colunas do Dataframe
    for index, item in df_itens.iterrows():

        item_material: str = str(item['MATERIAL']) # Material do item atual

        # Roda as funções de formatação xml e request + logging
        logging.info(f'Iniciando formatação XML para: {item_material}')
        xml_str = format_xml_body(index, template_root, item)


        # # ME DESCOMENTE 🙏 (selecione esse trecho e "Ctrl + :")
        # # logging.info(f'Iniciando request para: {item_material}')
        # response = fetch_data(xml_str)
        
        # # Formatação do nome do arquivo de resposta
        # file_date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # file_name_response = f'{item_material}_{file_date_time}'

        # # Escreve a resposta da request em um arquivo dentro do dir "/logs/requests/", exemplo de nome: "000000000000037272_2025-03-21_12-09-52.json"
        # with open(PATH + f'logs/requests/{file_name_response}.json', 'w', encoding='utf-8') as file:
        #     file.write(response.json())


        # Trecho para DEBUG

        # Escreve um arquivo "output.xml" contendo o body da requisição atual em "/xml/"
        # with open(PATH + 'xml/output.xml', 'w') as f:
        #     f.write(pretty_xml(xml_str.decode('utf-8')))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception(f'Erro de exceção na função main.\n')
        traceback.print_exc()
