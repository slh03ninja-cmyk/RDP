"""Diagnostic Algo Trading — exécuter sur le RDP pour voir l'état exact MT5."""
import MetaTrader5 as mt5
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

print("=== DIAGNOSTIC ALGO TRADING ===\n")

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
    print(f"  terminal.trade_allowed   = {getattr(terminal, 'trade_allowed', 'N/A')}")
    print(f"  terminal.tradeapi_disabled = {getattr(terminal, 'tradeapi_disabled', 'N/A')}")
    print(f"  account.trade_allowed    = {getattr(account, 'trade_allowed', 'N/A')}")
    print(f"  account.trade_expert     = {getattr(account, 'trade_expert', 'N/A')}")
    print()
    ta = getattr(terminal, 'trade_allowed', None)
    te = getattr(account, 'trade_expert', None)
    td = getattr(terminal, 'tradeapi_disabled', None)
    if ta and te and not td:
        print("✅ Tout est OK — l'algo trading devrait fonctionner")
    else:
        print("❌ PROBLÈME DÉTECTÉ :")
        if not ta:
            print("   → terminal.trade_allowed = False")
        if td:
            print("   → terminal.tradeapi_disabled = True")
        if not te:
            print("   → account.trade_expert = False (broker bloque l'algo trading)")

mt5.shutdown()
