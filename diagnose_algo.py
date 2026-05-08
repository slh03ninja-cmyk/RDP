"""Diagnostic Algo Trading — exécuter sur le RDP pour voir l'état exact MT5.
Vérifie aussi les fichiers de config (common.ini, terminal.ini)."""
import MetaTrader5 as mt5
import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

print("=== DIAGNOSTIC ALGO TRADING ===\n")

# ── 1) Vérifier les fichiers de config ──
print("--- FICHIERS DE CONFIG ---")
mt5_dir = r"C:\Program Files\MetaTrader 5 EXNESS"
config_files = [
    os.path.join(mt5_dir, "config", "common.ini"),
    os.path.join(mt5_dir, "config", "terminal.ini"),
    os.path.join(os.environ.get("APPDATA", ""), "MetaQuotes", "Terminal", "Common", "config", "common.ini"),
]
for cf in config_files:
    if os.path.exists(cf):
        print(f"\n  📄 {cf}:")
        with open(cf, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    print(f"    {line}")
    else:
        print(f"  ❌ {cf} — N'EXISTE PAS")

print()

# ── 2) Connexion MT5 ──
if not mt5.initialize():
    print(f"❌ MT5 initialize failed: {mt5.last_error()}")
    sys.exit(1)

print(f"MT5 version: {mt5.version()}\n")

# Terminal info
terminal = mt5.terminal_info()
if terminal:
    t = terminal._asdict()
    print("--- TERMINAL INFO ---")
    for k, v in t.items():
        print(f"  {k} = {v}")
    print()
else:
    print("❌ terminal_info() returned None\n")

# Account info
account = mt5.account_info()
if account:
    a = account._asdict()
    print("--- ACCOUNT INFO ---")
    for k, v in a.items():
        print(f"  {k} = {v}")
    print()
else:
    print("❌ account_info() returned None\n")

# Résumé
print("=== RÉSUMÉ ===")
if terminal and account:
    ta = getattr(terminal, 'trade_allowed', None)
    td = getattr(terminal, 'tradeapi_disabled', None)
    te = getattr(account, 'trade_expert', None)
    tl = getattr(terminal, 'trade_allowed', None)
    print(f"  terminal.trade_allowed     = {ta}")
    print(f"  terminal.tradeapi_disabled = {td}")
    print(f"  account.trade_allowed      = {getattr(account, 'trade_allowed', 'N/A')}")
    print(f"  account.trade_expert       = {te}")
    print()
    if ta and te and not td:
        print("✅ Tout est OK — l'algo trading devrait fonctionner")
    else:
        print("❌ PROBLÈME DÉTECTÉ :")
        if not ta:
            print("   → terminal.trade_allowed = False")
            print("     Le terminal n'est pas connecté ou le trading est interdit")
        if td:
            print("   → terminal.tradeapi_disabled = True")
            print("     → Outils → Options → Conseillers experts → Autoriser le trading automatisé")
        if not te:
            print("   → account.trade_expert = False")
            print("     Le broker (Exness) bloque l'algo trading sur ce compte")
            print("     → Vérifiez que le type de compte supporte l'algo trading")
            print("     → Contactez Exness si le problème persiste")

mt5.shutdown()
