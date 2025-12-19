"""
Integração com WhatsApp para envio de relatórios
Suporta: Evolution API, Z-API, ou WhatsApp Web via Selenium
"""
import os
import sys
import json
import time
import base64
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional

# Adiciona path do projeto
sys.path.append(str(Path(__file__).parent.parent))

from config import WHATSAPP_CONFIG
from reports.daily_report import generate_comparison_report, format_report_text, generate_html_report


class WhatsAppSender:
    """Classe base para envio de mensagens WhatsApp"""
    
    def __init__(self):
        self.api_url = WHATSAPP_CONFIG['api_url']
        self.api_key = WHATSAPP_CONFIG['api_key']
        self.instance = WHATSAPP_CONFIG['instance']
    
    def send_text(self, number: str, message: str) -> bool:
        """Envia mensagem de texto"""
        raise NotImplementedError
    
    def send_image(self, number: str, image_path: str, caption: str = "") -> bool:
        """Envia imagem"""
        raise NotImplementedError


class EvolutionAPISender(WhatsAppSender):
    """Integração com Evolution API"""
    
    def send_text(self, number: str, message: str) -> bool:
        """Envia mensagem de texto via Evolution API"""
        try:
            url = f"{self.api_url}/message/sendText/{self.instance}"
            headers = {
                "apikey": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "number": number,
                "text": message
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                print(f"✅ Mensagem enviada para {number}")
                return True
            else:
                print(f"❌ Erro ao enviar: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na API: {e}")
            return False
    
    def send_image(self, number: str, image_path: str, caption: str = "") -> bool:
        """Envia imagem via Evolution API"""
        try:
            url = f"{self.api_url}/message/sendMedia/{self.instance}"
            headers = {
                "apikey": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Converte imagem para base64
            with open(image_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode()
            
            payload = {
                "number": number,
                "mediatype": "image",
                "media": f"data:image/png;base64,{image_base64}",
                "caption": caption
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                print(f"✅ Imagem enviada para {number}")
                return True
            else:
                print(f"❌ Erro ao enviar imagem: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False


class ZAPISender(WhatsAppSender):
    """Integração com Z-API"""
    
    def send_text(self, number: str, message: str) -> bool:
        """Envia mensagem de texto via Z-API"""
        try:
            url = f"{self.api_url}/send-text"
            headers = {
                "Client-Token": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "phone": number,
                "message": message
            }
            
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def send_image(self, number: str, image_path: str, caption: str = "") -> bool:
        """Envia imagem via Z-API"""
        try:
            url = f"{self.api_url}/send-image"
            headers = {
                "Client-Token": self.api_key,
                "Content-Type": "application/json"
            }
            
            with open(image_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode()
            
            payload = {
                "phone": number,
                "image": image_base64,
                "caption": caption
            }
            
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False


def take_screenshot_of_report(html_path: str, output_path: str) -> bool:
    """Tira screenshot do relatório HTML usando Playwright"""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 650, 'height': 900})
            
            # Abre o HTML local
            page.goto(f'file:///{html_path}')
            time.sleep(1)  # Aguarda renderização
            
            # Tira screenshot
            page.screenshot(path=output_path, full_page=True)
            browser.close()
            
            print(f"✅ Screenshot salvo: {output_path}")
            return True
            
    except ImportError:
        print("⚠️ Playwright não instalado. Instale com: pip install playwright && playwright install")
        return False
    except Exception as e:
        print(f"❌ Erro ao tirar screenshot: {e}")
        return False


def send_daily_report_whatsapp(phone_numbers: list = None):
    """Envia relatório diário via WhatsApp"""
    
    print("📱 Preparando envio do relatório via WhatsApp...")
    
    # Gera relatório
    comparison = generate_comparison_report()
    
    if not comparison:
        print("❌ Não foi possível gerar o relatório")
        return False
    
    # Gera texto do relatório
    report_text = format_report_text(comparison)
    
    # Gera HTML e screenshot
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    date_str = datetime.now().strftime('%Y%m%d')
    html_path = reports_dir / f"report_{date_str}.html"
    screenshot_path = reports_dir / f"report_{date_str}.png"
    
    # Salva HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(generate_html_report(comparison))
    
    # Tenta tirar screenshot
    screenshot_success = take_screenshot_of_report(str(html_path), str(screenshot_path))
    
    # Configura sender (pode alternar entre APIs)
    sender = EvolutionAPISender()
    
    # Números para enviar (pode ser grupo ou números individuais)
    if phone_numbers is None:
        phone_numbers = [WHATSAPP_CONFIG.get('group_id', '')]
    
    phone_numbers = [n for n in phone_numbers if n]  # Remove vazios
    
    if not phone_numbers:
        print("⚠️ Nenhum número configurado para envio")
        print("\n📋 Relatório gerado (não enviado):")
        print(report_text)
        return False
    
    # Envia para cada número
    for number in phone_numbers:
        print(f"\n📤 Enviando para {number}...")
        
        if screenshot_success and screenshot_path.exists():
            # Envia imagem com legenda resumida
            caption = f"📊 Relatório de Manutenção - {datetime.now().strftime('%d/%m/%Y')}"
            sender.send_image(number, str(screenshot_path), caption)
        
        # Envia texto completo
        sender.send_text(number, report_text)
    
    print("\n✅ Envio concluído!")
    return True


# CLI para testes
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Envia relatório via WhatsApp')
    parser.add_argument('--numbers', nargs='+', help='Números para enviar (com DDD)')
    parser.add_argument('--test', action='store_true', help='Modo teste (não envia)')
    
    args = parser.parse_args()
    
    if args.test:
        # Modo teste - apenas mostra o relatório
        comparison = generate_comparison_report()
        if comparison:
            print(format_report_text(comparison))
    else:
        send_daily_report_whatsapp(args.numbers)
