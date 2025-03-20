import os
import pandas as pd
import logging
import requests
import xml.etree.ElementTree as xmlET

if __name__ == "__main__":
    PATH = os.path.dirname(os.path.abspath(__file__))
    PATH = PATH.replace('\\', '/') + '/'

    dfItens = pd.read_excel(PATH + "itens/EXEMPLO-MOCK-Requisicoes.xlsx", engine="openpyxl", dtype=str)

    template = xmlET.parse(PATH + "/xml/template.xml")
    template_root = template.getroot()

    # Create a new root element with the specified namespaces
    template_root.set('xmlns:urn', 'urn:sap-com:document:sap:soap:functions:mc-style')
    template_root.set('xmlns:soapenv', 'http://schemas.xmlsoap.org/soap/envelope/')

    # FOR LOOP das colunas do Data Frame (tabela do Excel)
    for index, item in dfItens.iterrows():

        materialString: str = item['MATERIALDESCRIPTION'].strip()
        longTextString: str = (f"<MATERIALLONGTEXT>{item['MATERIALLONGTEXT'].strip()}</MATERIALLONGTEXT>")

        # Variáveis de cada ITEM da tabela
        material: str = str(item['MATERIAL'])
        matType: str = item['MAT Type']
        description = xmlET.fromstring(materialString)
        longText = xmlET.fromstring(longTextString)

        # Local no XML das descrições
        descriptionLoc = xmlET.SubElement(template_root, 'MATERIALDESCRIPTION')
        longTextLoc = xmlET.SubElement(template_root, 'MATERIALLONGTEXT')
        matl_type_tag = template_root.find('HEADDATA/MATL_TYPE')

        # EXECUÇÃO

        # Iteração das tags "MATERIAL" no template
        for i in template_root.iter("MATERIAL"):
            i.text = material

        # Altera o tipo de material
        if matl_type_tag is not None:
            matl_type_tag.text = matType

        # Insere os subelementos XML nas descrições
        descriptionLoc.append(description)
        template_root.append(longText)

    # Write the XML to a string with the XML declaration
    xml_str = xmlET.tostring(template_root, encoding='utf-8', xml_declaration=True)

    with open(PATH + '/xml/output.xml', 'wb') as f:
        f.write(xml_str)
