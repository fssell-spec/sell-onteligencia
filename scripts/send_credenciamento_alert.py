"""
Alerta de credenciamentos ativos no PNCP.

Detecta editais de credenciamento abertos, gera um resumo e envia por e-mail.
Pode ser agendado diariamente após run_accreditation_crawler.py.

Uso:
    python scripts/send_credenciamento_alert.py
    python scripts/send_credenciamento_alert.py --dry-run   # mostra o e-mail sem enviar
    python scripts/send_credenciamento_alert.py --destinatarios vendas@sell.com.br
"""
import argparse
import os
import smtplib
import sys
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.accreditation_notice import AccreditationNotice
from app.models.municipality import Municipality


# ── Configuração SMTP ─────────────────────────────────────────────────────────
# Pode vir do .env ou ser definida aqui para testes
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER", "")          # seu e-mail
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")      # senha ou app password
EMAIL_FROM    = os.getenv("EMAIL_FROM", SMTP_USER)
EMAIL_TO_DEFAULT = os.getenv("EMAIL_ALERT_TO", "")  # destinatário padrão
# ─────────────────────────────────────────────────────────────────────────────


def build_alert_data(db) -> list[dict]:
    """Retorna credenciamentos ativos com dados do município."""
    hoje = date.today()
    rows = (
        db.query(AccreditationNotice, Municipality)
        .join(Municipality, AccreditationNotice.municipality_id == Municipality.id)
        .filter(AccreditationNotice.is_active == True)
        .order_by(AccreditationNotice.data_encerramento.asc().nullslast())
        .all()
    )

    alerts = []
    for notice, muni in rows:
        # Urgência: quantos dias até encerrar
        dias_restantes = None
        urgencia = "normal"
        if notice.data_encerramento:
            dias_restantes = (notice.data_encerramento - hoje).days
            if dias_restantes <= 3:
                urgencia = "critica"
            elif dias_restantes <= 7:
                urgencia = "alta"
            elif dias_restantes <= 14:
                urgencia = "media"

        alerts.append({
            "municipio": muni.name,
            "populacao": muni.population or 0,
            "objeto": notice.objeto or "Credenciamento de shows/eventos",
            "valor_estimado": float(notice.valor_estimado) if notice.valor_estimado else None,
            "data_publicacao": notice.data_publicacao,
            "data_encerramento": notice.data_encerramento,
            "dias_restantes": dias_restantes,
            "urgencia": urgencia,
            "url_pncp": f"https://pncp.gov.br/app/editais/{notice.numero_controle}",
            "numero_controle": notice.numero_controle,
        })

    return alerts


def render_html(alerts: list[dict], hoje: date) -> str:
    urgencia_color = {
        "critica": "#dc2626",
        "alta":    "#ea580c",
        "media":   "#d97706",
        "normal":  "#16a34a",
    }
    urgencia_label = {
        "critica": "🔴 CRÍTICO",
        "alta":    "🟠 URGENTE",
        "media":   "🟡 ATENÇÃO",
        "normal":  "🟢 ABERTO",
    }

    rows_html = ""
    for a in alerts:
        cor = urgencia_color[a["urgencia"]]
        label = urgencia_label[a["urgencia"]]
        valor = f"R$ {a['valor_estimado']:,.0f}".replace(",", ".") if a["valor_estimado"] else "—"
        enc = a["data_encerramento"].strftime("%d/%m/%Y") if a["data_encerramento"] else "—"
        dias = f"{a['dias_restantes']} dias" if a["dias_restantes"] is not None else "—"
        objeto_curto = (a["objeto"][:90] + "...") if len(a["objeto"]) > 90 else a["objeto"]

        rows_html += f"""
        <tr>
          <td style="padding:10px;border-bottom:1px solid #e5e7eb;">
            <strong>{a["municipio"]}</strong><br>
            <small style="color:#6b7280;">Pop. {a["populacao"]:,}".replace(",",".")".strip()</small>
          </td>
          <td style="padding:10px;border-bottom:1px solid #e5e7eb;font-size:13px;">{objeto_curto}</td>
          <td style="padding:10px;border-bottom:1px solid #e5e7eb;text-align:center;">{valor}</td>
          <td style="padding:10px;border-bottom:1px solid #e5e7eb;text-align:center;">{enc}<br><small>{dias}</small></td>
          <td style="padding:10px;border-bottom:1px solid #e5e7eb;text-align:center;">
            <span style="color:{cor};font-weight:bold;">{label}</span>
          </td>
          <td style="padding:10px;border-bottom:1px solid #e5e7eb;text-align:center;">
            <a href="{a["url_pncp"]}" style="background:#2563eb;color:white;padding:4px 10px;border-radius:4px;text-decoration:none;font-size:12px;">Ver edital</a>
          </td>
        </tr>"""

    criticos = sum(1 for a in alerts if a["urgencia"] == "critica")
    urgentes = sum(1 for a in alerts if a["urgencia"] == "alta")

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;background:#f9fafb;margin:0;padding:20px;">
  <div style="max-width:900px;margin:0 auto;background:white;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1);">

    <div style="background:#1e3a5f;color:white;padding:24px;">
      <h1 style="margin:0;font-size:20px;">🎯 Sell Inteligência — Alertas de Credenciamento</h1>
      <p style="margin:6px 0 0;opacity:0.8;">{hoje.strftime("%d/%m/%Y")} · {len(alerts)} edital(is) ativo(s)
      {f' · <strong style="color:#fbbf24;">{criticos} crítico(s)</strong>' if criticos else ''}
      {f' · <strong style="color:#fb923c;">{urgentes} urgente(s)</strong>' if urgentes else ''}
      </p>
    </div>

    <div style="padding:20px;">
      {"<div style='background:#fef2f2;border:1px solid #fecaca;border-radius:6px;padding:12px;margin-bottom:16px;'><strong style='color:#dc2626;'>⚠️ Ação imediata necessária:</strong> há " + str(criticos) + " edital(is) encerrando em até 3 dias!</div>" if criticos else ""}

      <table style="width:100%;border-collapse:collapse;">
        <thead>
          <tr style="background:#f3f4f6;">
            <th style="padding:10px;text-align:left;font-size:13px;">Município</th>
            <th style="padding:10px;text-align:left;font-size:13px;">Objeto</th>
            <th style="padding:10px;text-align:center;font-size:13px;">Valor Est.</th>
            <th style="padding:10px;text-align:center;font-size:13px;">Encerra</th>
            <th style="padding:10px;text-align:center;font-size:13px;">Status</th>
            <th style="padding:10px;text-align:center;font-size:13px;">PNCP</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>

    <div style="background:#f3f4f6;padding:16px;text-align:center;font-size:12px;color:#6b7280;">
      Gerado automaticamente pelo Sell Inteligência · Dados: PNCP
    </div>
  </div>
</body>
</html>"""


def render_text(alerts: list[dict], hoje: date) -> str:
    lines = [
        f"SELL INTELIGÊNCIA — Alertas de Credenciamento",
        f"Data: {hoje.strftime('%d/%m/%Y')} | {len(alerts)} edital(is) ativo(s)",
        "=" * 60,
    ]
    for a in alerts:
        enc = a["data_encerramento"].strftime("%d/%m/%Y") if a["data_encerramento"] else "Sem prazo"
        dias = f"({a['dias_restantes']} dias)" if a["dias_restantes"] is not None else ""
        valor = f"R$ {a['valor_estimado']:,.0f}" if a["valor_estimado"] else "Valor n/d"
        urgencia_map = {"critica": "🔴 CRÍTICO", "alta": "🟠 URGENTE", "media": "🟡 ATENÇÃO", "normal": "✅ ABERTO"}
        lines += [
            f"\n{urgencia_map[a['urgencia']]} — {a['municipio']}",
            f"  Objeto:  {a['objeto'][:80]}",
            f"  Valor:   {valor}",
            f"  Prazo:   {enc} {dias}",
            f"  Edital:  {a['url_pncp']}",
        ]
    return "\n".join(lines)


def send_email(
    destinatarios: list[str],
    alerts: list[dict],
    hoje: date,
    dry_run: bool = False,
) -> None:
    criticos = sum(1 for a in alerts if a["urgencia"] == "critica")
    assunto_prefix = "🔴 AÇÃO URGENTE" if criticos else "🎯 Sell Inteligência"
    assunto = f"{assunto_prefix} — {len(alerts)} Credenciamento(s) Ativo(s) no PNCP"

    html_body = render_html(alerts, hoje)
    text_body = render_text(alerts, hoje)

    if dry_run:
        print("=" * 60)
        print("DRY-RUN — e-mail que seria enviado:")
        print(f"Para:    {', '.join(destinatarios)}")
        print(f"Assunto: {assunto}")
        print("-" * 60)
        print(text_body)
        return

    if not SMTP_USER or not SMTP_PASSWORD:
        print("⚠️  SMTP não configurado. Defina SMTP_USER e SMTP_PASSWORD no .env")
        print("\nConteúdo do alerta (para copiar manualmente):")
        print(text_body)
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(destinatarios)
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, destinatarios, msg.as_string())

    print(f"✅ E-mail enviado para {', '.join(destinatarios)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Alerta de credenciamentos ativos")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o e-mail sem enviar")
    parser.add_argument(
        "--destinatarios", nargs="+",
        default=[d for d in [EMAIL_TO_DEFAULT] if d],
        help="E-mails destinatários",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        alerts = build_alert_data(db)
    finally:
        db.close()

    if not alerts:
        print("Nenhum credenciamento ativo no momento. Nada a alertar.")
        return

    hoje = date.today()
    print(f"Credenciamentos ativos: {len(alerts)}")
    for a in alerts:
        dias = f"({a['dias_restantes']}d)" if a["dias_restantes"] is not None else ""
        print(f"  [{a['urgencia'].upper():8}] {a['municipio']} {dias}")

    destinatarios = args.destinatarios
    if not destinatarios:
        print("\n⚠️  Nenhum destinatário configurado.")
        print("Use --destinatarios seu@email.com ou defina EMAIL_ALERT_TO no .env")
        print("\nRodando em dry-run automático:")
        args.dry_run = True
        destinatarios = ["(não configurado)"]

    send_email(destinatarios, alerts, hoje, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
