import schedule
import time
from datetime import datetime
from whatsapp_sender import executar_rotina

# Horário do relatório diário
HORARIO_RELATORIO = "18:30"


def job_relatorio():
    """Job que executa o relatório"""
    print(f"\n⏰ [{datetime.now().strftime('%H:%M:%S')}] Executando job agendado...")
    executar_rotina()


def iniciar_agendador():
    """Inicia o agendador de tarefas"""
    print("="*60)
    print("📅 AGENDADOR DE RELATÓRIOS - WHATSAPP")
    print("="*60)
    print(f"\n✅ Relatório agendado para: {HORARIO_RELATORIO}")
    print("🔄 Aguardando horário...\n")
    print("💡 Dica: Deixe este terminal aberto!")
    print("💡 O WhatsApp Web será aberto automaticamente no horário.\n")
    
    # Agendar para rodar todo dia às 18:30
    schedule.every().day.at(HORARIO_RELATORIO).do(job_relatorio)
    
    # Loop infinito verificando agenda
    while True:
        schedule.run_pending()
        time.sleep(30)  # Verifica a cada 30 segundos


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--agora":
            # Teste imediato
            print("🧪 Executando teste imediato...")
            executar_rotina()
        elif sys.argv[1] == "--preview":
            # Apenas mostra o relatório
            from relatorio import gerar_relatorio
            print(gerar_relatorio())
    else:
        # Iniciar agendador
        iniciar_agendador()
