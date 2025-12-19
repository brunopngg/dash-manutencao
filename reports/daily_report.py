"""
Gerador de Relatórios Diários
Compara dia atual com dia anterior e gera relatório visual
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional

# Adiciona path do projeto
sys.path.append(str(Path(__file__).parent.parent))

from database.db_manager import get_db, MaintenanceRepository


def generate_comparison_report(date1: str = None, date2: str = None) -> Dict:
    """
    Gera relatório comparativo entre dois dias
    Se não especificado, compara hoje com ontem
    """
    if date1 is None:
        date1 = datetime.now().strftime('%Y-%m-%d')
    if date2 is None:
        yesterday = datetime.now() - timedelta(days=1)
        date2 = yesterday.strftime('%Y-%m-%d')
    
    db = get_db()
    repo = MaintenanceRepository(db)
    
    comparison = repo.get_comparison(date1, date2)
    db.close()
    
    return comparison


def format_report_text(comparison: Dict) -> str:
    """Formata relatório como texto para WhatsApp"""
    if not comparison:
        return "❌ Não foi possível gerar o relatório. Dados insuficientes."
    
    atual = comparison['atual']
    anterior = comparison['anterior']
    diff = comparison['diferenca']
    
    def arrow(value):
        if value > 0:
            return f"📈 +{value}"
        elif value < 0:
            return f"📉 {value}"
        return "➡️ 0"
    
    report = f"""
📊 *RELATÓRIO DIÁRIO DE MANUTENÇÃO*
📅 {comparison['data_atual']}

━━━━━━━━━━━━━━━━━━━━━━
📋 *RESUMO DO DIA*
━━━━━━━━━━━━━━━━━━━━━━

✅ *Total de Serviços:* {atual['total'] or 0}
   {arrow(diff['total'])} vs dia anterior

━━━━━━━━━━━━━━━━━━━━━━
🏢 *POR POLO*
━━━━━━━━━━━━━━━━━━━━━━

🔹 *MARABÁ:* {atual['maraba'] or 0} serviços
   {arrow(diff['maraba'])}

🔹 *TUCURUÍ:* {atual['tucurui'] or 0} serviços
   {arrow(diff['tucurui'])}

🔹 *PARAUAPEBAS:* {atual['parauapebas'] or 0} serviços
   {arrow(diff['parauapebas'])}

🔹 *REDENÇÃO:* {atual['redencao'] or 0} serviços
   {arrow(diff['redencao'])}

━━━━━━━━━━━━━━━━━━━━━━
📈 *INDICADORES*
━━━━━━━━━━━━━━━━━━━━━━

✅ Com Baixa: {atual['com_baixa'] or 0}
👥 Equipes Ativas: {atual['equipes'] or 0}

━━━━━━━━━━━━━━━━━━━━━━
📊 *COMPARATIVO*
━━━━━━━━━━━━━━━━━━━━━━

Ontem ({comparison['data_anterior']}): {anterior['total'] or 0} serviços
Hoje ({comparison['data_atual']}): {atual['total'] or 0} serviços
Variação: {arrow(diff['total'])}

━━━━━━━━━━━━━━━━━━━━━━
🤖 _Relatório gerado automaticamente_
⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
    return report


def generate_html_report(comparison: Dict) -> str:
    """Gera relatório em HTML para screenshot"""
    if not comparison:
        return "<html><body><h1>Erro ao gerar relatório</h1></body></html>"
    
    atual = comparison['atual']
    anterior = comparison['anterior']
    diff = comparison['diferenca']
    
    def get_trend_class(value):
        if value > 0:
            return "positive"
        elif value < 0:
            return "negative"
        return "neutral"
    
    def get_trend_icon(value):
        if value > 0:
            return f"↑ +{value}"
        elif value < 0:
            return f"↓ {value}"
        return "→ 0"
    
    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório Diário - Manutenção</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            font-size: 1.8rem;
            margin-bottom: 5px;
        }}
        .header .date {{
            color: #00d4ff;
            font-size: 1.2rem;
        }}
        .card {{
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
        }}
        .card-title {{
            font-size: 1rem;
            color: #888;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .big-number {{
            font-size: 3rem;
            font-weight: bold;
            color: #00d4ff;
        }}
        .trend {{
            font-size: 1rem;
            padding: 5px 10px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 10px;
        }}
        .positive {{
            background: rgba(0, 255, 100, 0.2);
            color: #00ff64;
        }}
        .negative {{
            background: rgba(255, 100, 100, 0.2);
            color: #ff6464;
        }}
        .neutral {{
            background: rgba(255, 255, 255, 0.2);
            color: #fff;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        .polo-item {{
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}
        .polo-name {{
            font-size: 0.9rem;
            color: #888;
            margin-bottom: 5px;
        }}
        .polo-value {{
            font-size: 1.8rem;
            font-weight: bold;
            color: #fff;
        }}
        .polo-trend {{
            font-size: 0.8rem;
            margin-top: 5px;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 0.8rem;
            margin-top: 20px;
        }}
        .comparison-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
        }}
        .comparison-item {{
            text-align: center;
        }}
        .comparison-label {{
            font-size: 0.8rem;
            color: #888;
        }}
        .comparison-value {{
            font-size: 1.5rem;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 Relatório de Manutenção</h1>
            <div class="date">📅 {datetime.strptime(comparison['data_atual'], '%Y-%m-%d').strftime('%d/%m/%Y')}</div>
        </div>
        
        <div class="card">
            <div class="card-title">Total de Serviços</div>
            <div class="big-number">{atual['total'] or 0}</div>
            <div class="trend {get_trend_class(diff['total'])}">{get_trend_icon(diff['total'])} vs ontem</div>
        </div>
        
        <div class="card">
            <div class="card-title">Serviços por Polo</div>
            <div class="grid">
                <div class="polo-item">
                    <div class="polo-name">MARABÁ</div>
                    <div class="polo-value">{atual['maraba'] or 0}</div>
                    <div class="polo-trend {get_trend_class(diff['maraba'])}">{get_trend_icon(diff['maraba'])}</div>
                </div>
                <div class="polo-item">
                    <div class="polo-name">TUCURUÍ</div>
                    <div class="polo-value">{atual['tucurui'] or 0}</div>
                    <div class="polo-trend {get_trend_class(diff['tucurui'])}">{get_trend_icon(diff['tucurui'])}</div>
                </div>
                <div class="polo-item">
                    <div class="polo-name">PARAUAPEBAS</div>
                    <div class="polo-value">{atual['parauapebas'] or 0}</div>
                    <div class="polo-trend {get_trend_class(diff['parauapebas'])}">{get_trend_icon(diff['parauapebas'])}</div>
                </div>
                <div class="polo-item">
                    <div class="polo-name">REDENÇÃO</div>
                    <div class="polo-value">{atual['redencao'] or 0}</div>
                    <div class="polo-trend {get_trend_class(diff['redencao'])}">{get_trend_icon(diff['redencao'])}</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">Comparativo</div>
            <div class="comparison-bar">
                <div class="comparison-item">
                    <div class="comparison-label">Ontem</div>
                    <div class="comparison-value">{anterior['total'] or 0}</div>
                </div>
                <div class="comparison-item">
                    <div class="comparison-label">→</div>
                </div>
                <div class="comparison-item">
                    <div class="comparison-label">Hoje</div>
                    <div class="comparison-value" style="color: #00d4ff;">{atual['total'] or 0}</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">Indicadores</div>
            <div class="grid">
                <div class="polo-item">
                    <div class="polo-name">Com Baixa</div>
                    <div class="polo-value" style="color: #00ff64;">✓ {atual['com_baixa'] or 0}</div>
                </div>
                <div class="polo-item">
                    <div class="polo-name">Equipes</div>
                    <div class="polo-value">👥 {atual['equipes'] or 0}</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            🤖 Relatório gerado automaticamente | ⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>
    </div>
</body>
</html>
"""
    return html


def save_report_files(comparison: Dict) -> Dict[str, str]:
    """Salva relatório em diferentes formatos"""
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    date_str = datetime.now().strftime('%Y%m%d')
    
    # Salva texto
    text_path = reports_dir / f"report_{date_str}.txt"
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(format_report_text(comparison))
    
    # Salva HTML
    html_path = reports_dir / f"report_{date_str}.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(generate_html_report(comparison))
    
    print(f"✅ Relatórios salvos em:")
    print(f"   📄 {text_path}")
    print(f"   🌐 {html_path}")
    
    return {
        'text': str(text_path),
        'html': str(html_path)
    }


def generate_daily_report():
    """Função principal para gerar relatório diário"""
    print("📊 Gerando relatório diário...")
    
    comparison = generate_comparison_report()
    
    if comparison:
        files = save_report_files(comparison)
        text_report = format_report_text(comparison)
        print("\n" + "="*50)
        print(text_report)
        print("="*50)
        return files
    else:
        print("❌ Não foi possível gerar o relatório")
        return None


if __name__ == "__main__":
    generate_daily_report()
