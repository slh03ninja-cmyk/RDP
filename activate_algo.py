"""
Activate Algo Trading — PyAutoGUI automation
Simule les mêmes gestes que l'activation manuelle :
1. Ouvre MT5 → Tools → Options → Expert Advisors
2. Coche "Allow Algo Trading"
3. Clique OK
4. Vérifie via API que trade_expert = True

Usage: python activate_algo.py [--mt5-path path] [--login N] [--password P] [--server S]
"""

import subprocess
import sys
import os
import time
import argparse

# Auto-install pyautogui
try:
    import pyautogui
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui", "-q"])
    import pyautogui

try:
    import pygetwindow as gw
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygetwindow", "-q"])
    import pygetwindow as gw

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# PyAutoGUI safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


def find_mt5_window():
    """Trouve la fenêtre principale de MT5."""
    for title in gw.getAllTitles():
        if "MetaTrader" in title or "Exness" in title or "terminal" in title.lower():
            return gw.getWindowsWithTitle(title)[0]
    return None


def wait_for_mt5_window(timeout=120):
    """Attend que la fenêtre MT5 apparaisse."""
    print(f"Recherche fenêtre MT5 (timeout {timeout}s)...")
    start = time.time()
    while time.time() - start < timeout:
        win = find_mt5_window()
        if win:
            print(f"Fenêtre trouvée: '{win.title}'")
            return win
        time.sleep(3)
    return None


def activate_algo_via_menu(win):
    """Active Algo Trading via le menu Tools → Options → Expert Advisors."""
    print("\n=== Activation Algo Trading via menu ===")

    # 1) Cliquer sur la fenêtre MT5 pour la focus
    try:
        win.activate()
        time.sleep(1)
    except Exception:
        # Fallback: cliquer au milieu de la fenêtre
        pyautogui.click(win.left + win.width // 2, win.top + win.height // 2)
        time.sleep(1)

    # 2) Ouvrir Tools → Options via clavier (Alt+T puis O)
    print("Ouverture Tools → Options...")
    pyautogui.hotkey('alt', 't')
    time.sleep(1)

    # Chercher "Options" dans le menu
    # Sur MT5, le raccourci est souvent Alt+T → O
    pyautogui.press('o')
    time.sleep(2)

    # 3) La boîte de dialogue Options devrait être ouverte
    # Aller dans l'onglet "Expert Advisors" (c'est souvent le dernier onglet)
    # Utiliser Ctrl+Tab pour naviguer entre onglets, ou cliquer directement
    print("Navigation vers l'onglet Expert Advisors...")

    # Essayer de trouver l'onglet "Expert Advisors" ou "Conseillers experts"
    # Cliquer sur le dernier onglet (Expert Advisors est souvent le dernier)
    # Méthode: utiliser Ctrl+Page Down pour aller au dernier onglet
    for _ in range(10):  # Max 10 onglets
        pyautogui.hotkey('ctrl', 'pagedown')
        time.sleep(0.3)

    time.sleep(1)

    # 4) Cocher "Allow algo trading" (Alt+A ou cliquer la checkbox)
    print("Coche 'Allow algo trading'...")
    # Le raccourci est souvent Alt+A pour "Allow algo trading"
    pyautogui.hotkey('alt', 'a')
    time.sleep(0.5)

    # Aussi essayer "Allow live trading" si présent
    pyautogui.hotkey('alt', 'l')
    time.sleep(0.5)

    # 5) Cliquer OK (Entrée ou Alt+O)
    print("Validation (OK)...")
    pyautogui.press('enter')
    time.sleep(2)

    print("Menu activation terminé.")


def activate_algo_via_toolbar(win):
    """Active Algo Trading via le bouton toolbar (méthode alternative)."""
    print("\n=== Activation Algo Trading via toolbar ===")

    try:
        win.activate()
        time.sleep(1)
    except Exception:
        pyautogui.click(win.left + win.width // 2, win.top + win.height // 2)
        time.sleep(1)

    # Le bouton Algo Trading est dans la toolbar
    # Essayer le raccourci clavier Ctrl+E (toggle Algo Trading dans certaines versions MT5)
    print("Tentative Ctrl+E (toggle Algo Trading)...")
    pyautogui.hotkey('ctrl', 'e')
    time.sleep(2)

    print("Toolbar activation terminée.")


def check_algo_status():
    """Vérifie l'état Algo Trading via l'API Python."""
    try:
        import MetaTrader5 as mt5
    except ImportError:
        print("❌ MetaTrader5 non installé")
        return False

    if not mt5.initialize():
        print(f"❌ MT5 init failed: {mt5.last_error()}")
        return False

    terminal = mt5.terminal_info()
    account = mt5.account_info()

    if terminal is None or account is None:
        print("❌ Impossible de récupérer les infos")
        mt5.shutdown()
        return False

    ta = getattr(terminal, "trade_allowed", None)
    td = getattr(terminal, "tradeapi_disabled", None)
    te = getattr(account, "trade_expert", None)

    print(f"\n--- ÉTAT ALGO TRADING ---")
    print(f"  terminal.trade_allowed     = {ta}")
    print(f"  terminal.tradeapi_disabled = {td}")
    print(f"  account.trade_expert       = {te}")

    mt5.shutdown()

    if ta and te and not td:
        print("\n✅ ALGO TRADING ACTIVÉ !")
        return True
    else:
        print("\n❌ Algo Trading toujours désactivé")
        return False


def main():
    parser = argparse.ArgumentParser(description="Activer Algo Trading MT5")
    parser.add_argument("--mt5-path", default=r"C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe")
    parser.add_argument("--login", default=os.getenv("MT5_LOGIN", ""))
    parser.add_argument("--password", default=os.getenv("MT5_PASSWORD", ""))
    parser.add_argument("--server", default=os.getenv("MT5_SERVER", ""))
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args()

    print("=" * 60)
    print("  ACTIVATION ALGO TRADING — PyAutoGUI")
    print("=" * 60)

    # Étape 0: Vérifier si déjà activé
    print("\n[ÉTAPE 0] Vérification état actuel...")
    if check_algo_status():
        print("Déjà activé, rien à faire !")
        return True

    # Étape 1: S'assurer que MT5 est lancé
    mt5_running = False
    try:
        import psutil
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and 'terminal' in proc.info['name'].lower():
                mt5_running = True
                break
    except ImportError:
        # Fallback: vérifier avec tasklist
        result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq terminal64.exe"],
                                capture_output=True, text=True)
        mt5_running = "terminal64" in result.stdout.lower()

    if not mt5_running:
        print(f"\n[ÉTAPE 1] Lancement MT5...")
        if os.path.exists(args.mt5_path):
            mt5_dir = os.path.dirname(args.mt5_path)
            cmd = [args.mt5_path]
            if args.login:
                cmd.extend([f"/login:{args.login}"])
            if args.password:
                cmd.extend([f"/password:{args.password}"])
            if args.server:
                cmd.extend([f"/server:{args.server}"])
            subprocess.Popen(cmd, cwd=mt5_dir)
            print(f"MT5 lancé, attente chargement...")
            time.sleep(30)
        else:
            print(f"❌ MT5 introuvable: {args.mt5_path}")
            return False
    else:
        print("\n[ÉTAPE 1] MT5 déjà en cours d'exécution")

    # Étape 2: Attendre la fenêtre MT5
    print("\n[ÉTAPE 2] Attente fenêtre MT5...")
    win = wait_for_mt5_window(timeout=60)
    if not win:
        print("❌ Fenêtre MT5 introuvable après 60s")
        return False

    # Attendre que la fenêtre soit complètement chargée
    time.sleep(10)

    # Étape 3: Activer Algo Trading (tentatives multiples)
    for attempt in range(1, args.max_attempts + 1):
        print(f"\n{'='*40}")
        print(f"  TENTATIVE {attempt}/{args.max_attempts}")
        print(f"{'='*40}")

        # Méthode 1: Via menu
        try:
            activate_algo_via_menu(win)
            time.sleep(3)
            if check_algo_status():
                return True
        except Exception as e:
            print(f"Erreur menu: {e}")

        # Méthode 2: Via toolbar (Ctrl+E)
        try:
            activate_algo_via_toolbar(win)
            time.sleep(3)
            if check_algo_status():
                return True
        except Exception as e:
            print(f"Erreur toolbar: {e}")

        if attempt < args.max_attempts:
            print(f"Retry dans 10s...")
            time.sleep(10)

    print("\n❌ ÉCHEC activation après toutes les tentatives")
    return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Algo Trading activé — le bot peut démarrer !")
    else:
        print("\n⚠️ Algo Trading non activé — le bot risque de ne pas trader")
    sys.exit(0 if success else 1)
