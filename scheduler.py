"""
Agendador de Tarefas
Executa sincronização e envio de relatórios em horários específicos
"""
import schedule
import time
import sys
from pathlib import Path
from datetime import datetime

# Adiciona path do projeto
sys.path.append(str(Path(__file__).parent))

from config import SCHEDULE_CONFIG
from sync.data_sync import sync_from_csv, sync_from_sheets
from reports.daily_report import generate_daily_report
from whatsapp.sender import send_daily_report_whatsapp


def job_sync_data():
    """Job: Sincroniza dados do Google Sheets"""
    print(f"\n{'='*50}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔄 Executando sincronização de dados...")
    print('='*50)
    
    try:
        # Tenta do Google Sheets, senão usa CSV
        result = sync_from_sheets()
        print(f"✅ Sincronização concluída: {result}")
    except Exception as e:
        print(f"❌ Erro na sincronização: {e}")
        # Fallback para CSV local
        try:
            result = sync_from_csv()
            print(f"✅ Sincronização do CSV: {result}")
        except Exception as e2:
            print(f"❌ Erro no fallback: {e2}")


def job_send_report():
    """Job: Gera e envia relatório via WhatsApp"""
    print(f"\n{'='*50}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 Gerando e enviando relatório...")
    print('='*50)
    
    try:
        # Gera relatório
        generate_daily_report()
        
        # Envia via WhatsApp
        send_daily_report_whatsapp()
        
        print("✅ Relatório enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar relatório: {e}")


def run_scheduler():
    """Executa o agendador"""
    print("""
╔═══════════════════════════════════════════════════╗
║     🤖 AGENDADOR DE TAREFAS - MANUTENÇÃO         ║
╠═══════════════════════════════════════════════════╣
║                                                   ║
║  📅 Tarefas agendadas:                           ║
║                                                   ║
║  🔄 Sincronização: {sync_time}                      ║
║  📊 Relatório:     {report_time}                      ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
    """.format(
        sync_time=SCHEDULE_CONFIG['sync_time'],
        report_time=SCHEDULE_CONFIG['report_time']
    ))
    
    # Agenda sincronização (18:30)
    schedule.every().day.at(SCHEDULE_CONFIG['sync_time']).do(job_sync_data)
    
    # Agenda envio de relatório (19:00)
    schedule.every().day.at(SCHEDULE_CONFIG['report_time']).do(job_send_report)
    
    print("✅ Agendador iniciado. Pressione Ctrl+C para parar.\n")
    
    # Loop principal
    while True:
        schedule.run_pending()
        
        # Mostra próxima execução
        next_run = schedule.next_run()
        if next_run:
            print(f"\r⏳ Próxima execução: {next_run.strftime('%H:%M:%S')}", end="", flush=True)
        
        time.sleep(60)  # Verifica a cada minuto


def run_now(task: str = "all"):
    """Executa tarefas imediatamente (para testes)"""
    if task in ["sync", "all"]:
        job_sync_data()
    
    if task in ["report", "all"]:
        job_send_report()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Agendador de tarefas')
    parser.add_argument('--run-now', choices=['sync', 'report', 'all'],
                       help='Executa tarefa imediatamente')
    parser.add_argument('--daemon', action='store_true',
                       help='Executa em modo daemon (agendador)')
    
    args = parser.parse_args()
    
    if args.run_now:
        run_now(args.run_now)
    elif args.daemon:
        run_scheduler()
    else:
        # Padrão: mostra ajuda
        parser.print_help()
        print("\n💡 Exemplos:")
        print("   python scheduler.py --run-now sync    # Sincroniza agora")
        print("   python scheduler.py --run-now report  # Gera relatório agora")
        print("   python scheduler.py --daemon          # Inicia agendador")
