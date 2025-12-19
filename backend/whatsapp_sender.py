import pywhatkit as kit
import pyautogui
from datetime import datetime
import time
from relatorio import gerar_relatorio

# ============================================
# CONFIGURAÇÃO - ALTERE AQUI!
# ============================================

# Opção 1: Número de telefone (com código do país)
TELEFONE = "+5594991046274"

# Opção 2: Nome do grupo (deixe vazio se for usar número)
GRUPO = ""  # Ex: "Equipe Manutenção"

# Horário para enviar (24h)
HORARIO = "18:30"

# ============================================


def enviar_whatsapp(mensagem):
    """Envia mensagem pelo WhatsApp Web"""
    agora = datetime.now()
    
    # Calcula horário de envio (1 minuto no futuro para dar tempo de abrir)
    hora_envio = agora.hour
    minuto_envio = agora.minute + 2
    
    if minuto_envio >= 60:
        hora_envio += 1
        minuto_envio -= 60
    
    print(f"📱 Preparando envio para {hora_envio}:{minuto_envio:02d}...")
    print(f"📝 Mensagem com {len(mensagem)} caracteres")
    
    try:
        if GRUPO:
            # Enviar para grupo
            print(f"👥 Enviando para grupo: {GRUPO}")
            kit.sendwhatmsg_to_group(
                GRUPO,
                mensagem,
                hora_envio,
                minuto_envio,
                wait_time=20,
                tab_close=True
            )
        else:
            # Enviar para número
            print(f"📞 Enviando para: {TELEFONE}")
            kit.sendwhatmsg(
                TELEFONE,
                mensagem,
                hora_envio,
                minuto_envio,
                wait_time=25,
                tab_close=False
            )
        
        # Aguarda carregar e clica em ENTER para enviar
        print("⏳ Aguardando envio...")
        time.sleep(3)
        pyautogui.press('enter')
        print("✅ Mensagem enviada com sucesso!")
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return False


def executar_rotina():
    """Executa a rotina completa: gera relatório e envia"""
    print("\n" + "="*50)
    print("🚀 INICIANDO ROTINA DE RELATÓRIO")
    print("="*50 + "\n")
    
    # Gera o relatório
    print("📊 Gerando relatório...")
    mensagem = gerar_relatorio()
    print("✅ Relatório gerado!\n")
    
    # Envia pelo WhatsApp
    enviar_whatsapp(mensagem)


if __name__ == "__main__":
    executar_rotina()
