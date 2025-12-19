"""
CLI Principal do Dashboard de Manutenção
Interface de linha de comando para todas as operações
"""
import argparse
import sys
from pathlib import Path

# Adiciona path do projeto
sys.path.insert(0, str(Path(__file__).parent))


def cmd_init():
    """Inicializa o banco de dados"""
    from database.db_manager import init_database
    init_database()


def cmd_sync(source='csv', clear=False):
    """Sincroniza dados"""
    from sync.data_sync import load_from_csv, load_from_google_sheets, sync_to_database
    
    if source == 'csv':
        df = load_from_csv()
    else:
        df = load_from_google_sheets()
    
    sync_to_database(df, clear_existing=clear)


def cmd_report(date1=None, date2=None):
    """Gera relatório"""
    from reports.daily_report import generate_comparison_report, format_report_text, save_report_files
    
    comparison = generate_comparison_report(date1, date2)
    
    if comparison:
        print(format_report_text(comparison))
        save_report_files(comparison)
    else:
        print("❌ Não foi possível gerar o relatório")


def cmd_whatsapp(numbers=None, test=False):
    """Envia via WhatsApp"""
    from whatsapp.sender import send_daily_report_whatsapp
    from reports.daily_report import generate_comparison_report, format_report_text
    
    if test:
        comparison = generate_comparison_report()
        if comparison:
            print(format_report_text(comparison))
    else:
        send_daily_report_whatsapp(numbers)


def cmd_dashboard():
    """Inicia o dashboard Streamlit"""
    import subprocess
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "dashboard.py"
    ])


def cmd_scheduler(daemon=False, run_now=None):
    """Gerencia agendador"""
    from scheduler import run_scheduler, run_now as execute_now
    
    if run_now:
        execute_now(run_now)
    elif daemon:
        run_scheduler()


def main():
    parser = argparse.ArgumentParser(
        description='🔧 Dashboard de Manutenção - CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s init                    # Inicializa banco de dados
  %(prog)s sync --source csv       # Sincroniza do CSV local
  %(prog)s sync --source sheets    # Sincroniza do Google Sheets
  %(prog)s report                  # Gera relatório de hoje vs ontem
  %(prog)s whatsapp --test         # Testa relatório sem enviar
  %(prog)s dashboard               # Inicia dashboard web
  %(prog)s scheduler --daemon      # Inicia agendador automático
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando: init
    subparsers.add_parser('init', help='Inicializa o banco de dados')
    
    # Comando: sync
    sync_parser = subparsers.add_parser('sync', help='Sincroniza dados')
    sync_parser.add_argument('--source', choices=['csv', 'sheets'], default='csv',
                            help='Fonte dos dados')
    sync_parser.add_argument('--clear', action='store_true',
                            help='Limpa dados antes de inserir')
    
    # Comando: report
    report_parser = subparsers.add_parser('report', help='Gera relatório')
    report_parser.add_argument('--date1', help='Data atual (YYYY-MM-DD)')
    report_parser.add_argument('--date2', help='Data anterior (YYYY-MM-DD)')
    
    # Comando: whatsapp
    wa_parser = subparsers.add_parser('whatsapp', help='Envia via WhatsApp')
    wa_parser.add_argument('--numbers', nargs='+', help='Números para enviar')
    wa_parser.add_argument('--test', action='store_true', help='Modo teste')
    
    # Comando: dashboard
    subparsers.add_parser('dashboard', help='Inicia dashboard web')
    
    # Comando: scheduler
    sched_parser = subparsers.add_parser('scheduler', help='Agendador de tarefas')
    sched_parser.add_argument('--daemon', action='store_true', help='Modo daemon')
    sched_parser.add_argument('--run-now', choices=['sync', 'report', 'all'],
                             help='Executa tarefa agora')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Executa comando
    if args.command == 'init':
        cmd_init()
    elif args.command == 'sync':
        cmd_sync(args.source, args.clear)
    elif args.command == 'report':
        cmd_report(args.date1, args.date2)
    elif args.command == 'whatsapp':
        cmd_whatsapp(args.numbers, args.test)
    elif args.command == 'dashboard':
        cmd_dashboard()
    elif args.command == 'scheduler':
        cmd_scheduler(args.daemon, args.run_now)


if __name__ == '__main__':
    main()
