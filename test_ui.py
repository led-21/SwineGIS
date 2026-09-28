# -*- coding: utf-8 -*-
"""
Teste de validação do arquivo .ui
"""
import xml.etree.ElementTree as ET
import os

ui_file = "suino_alpha_dialog_base.ui"

try:
    # Tentar fazer parse do arquivo XML
    tree = ET.parse(ui_file)
    root = tree.getroot()
    
    print("✅ Arquivo .ui está válido!")
    print(f"   Classe: {root.find('class').text}")
    print(f"   Widget principal: {root.find('widget').get('name')}")
    
    # Contar elementos
    widgets = root.findall(".//widget")
    print(f"   Total de widgets: {len(widgets)}")
    
    # Verificar se o arquivo termina corretamente
    with open(ui_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if content.strip().endswith('</ui>'):
            print("   ✅ Arquivo termina corretamente com </ui>")
        else:
            print("   ⚠️ AVISO: Arquivo pode não terminar corretamente")
            print(f"   Últimos 50 caracteres: {content[-50:]}")
    
except ET.ParseError as e:
    print(f"❌ ERRO no arquivo .ui:")
    print(f"   {e}")
    
except Exception as e:
    print(f"❌ ERRO geral:")
    print(f"   {e}")
