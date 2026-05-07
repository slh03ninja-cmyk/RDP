#!/usr/bin/env python3
"""
Test de connexion MT5 — diagnostic complet.
Vérifie que MetaTrader5 est accessible et que le compte est valide.

Usage:
    python test_mt5_connection.py [--env chemin/.env]

Sans argument, cherche .env dans le répertoire courant.
"""

import sys
import os
import time

def load_env(path=".env"):
    """Charge les variables depuis un fichier .env."""
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, _, value = line.partition('=')
                env[key.strip()] = value.strip()
    return env

def test_connection():
    """Test complet de connexion MT5."""
    try:
        import MetaTrader5 as mt5
    except ImportError:
        print("❌ MetaTrader5 non installé.")
        print("   pip install MetaTrader5")
        return False

    # Charger .env
    env_path = ".env"
    for arg in sys.argv[1:]:
        if arg == "--env" and len(sys.argv) > sys.argv.index(arg) + 1:
            env_path = sys.argv[sys.argv.index(arg) + 1]
        elif os.path.exists(arg):
            env_path = arg

    env = load_env(env_path)
    login = int(env.get("MT5_LOGIN", os.getenv("MT5_LOGIN", "0")))
    pwd = env.get("MT5_PASSWORD", os.getenv("MT5_PASSWORD", ""))
    srv = env.get("MT5_SERVER", os.getenv("MT5_SERVER", ""))

    if not login or not pwd or not srv:
        print("❌ Variables manquantes dans .env:")
        print(f"   MT5_LOGIN    = {'✅' if login else '❌ MANQUANT'}")
        print(f"   MT5_PASSWORD = {'✅' if pwd else '❌ MANQUANT'}")
        print(f"   MT5_SERVER   = {'✅' if srv else '❌ MANQUANT'}")
        return False

    print(f"📋 Config: login={login} server={srv}")
    print()

    # Test avec retry
    for attempt in range(1, 6):
        print(f"--- Tentative {attempt}/5 ---")

        # Test 1: initialize()
        try:
            if not mt5.initialize():
                err = mt5.last_error()
                print(f"  ❌ mt5.initialize() échoué: {err}")
                mt5.shutdown()
                if attempt < 5:
                    print(f"  ⏳ Retry dans 10s...")
                    time.sleep(10)
                continue
        except Exception as e:
            print(f"  ❌ Exception mt5.initialize(): {e}")
            if attempt < 5:
                time.sleep(10)
            continue

        # Test 2: account_info() sans credentials
        info = mt5.account_info()
        if info and info.login > 0:
            print(f"  ✅ Déjà connecté: {info.name} | Balance: {info.balance} {info.currency}")
            mt5.shutdown()
            return True

        mt5.shutdown()
        print(f"  ⚠️ Pas de compte actif, tentative avec credentials...")

        # Test 3: initialize() avec credentials
        try:
            if not mt5.initialize(login=login, password=pwd, server=srv):
                err = mt5.last_error()
                print(f"  ❌ mt5.initialize(login=...) échoué: {err}")
                mt5.shutdown()
                if attempt < 5:
                    print(f"  ⏳ Retry dans 10s...")
                    time.sleep(10)
                continue
        except Exception as e:
            print(f"  ❌ Exception mt5.initialize(login=...): {e}")
            mt5.shutdown()
            if attempt < 5:
                time.sleep(10)
            continue

        # Test 4: account_info() avec credentials
        info = mt5.account_info()
        if info and info.login > 0:
            print()
            print("=" * 50)
            print(f"  ✅ CONNEXION RÉUSSIE!")
            print(f"  📛 Nom:     {info.name}")
            print(f"  🔢 Login:   {info.login}")
            print(f"  💰 Balance: {info.balance} {info.currency}")
            print(f"  🏦 Server:  {info.server}")
            print(f"  📊 Leverage: 1:{info.leverage}")
            print("=" * 50)
            mt5.shutdown()
            return True
        else:
            print(f"  ⚠️ Connecté mais pas de compte")
            mt5.shutdown()
            if attempt < 5:
                time.sleep(10)

    print()
    print("❌ ÉCHEC après 5 tentatives")
    print()
    print("🔧 Vérifiez:")
    print(f"   1. MT5 est lancé? (terminal64.exe en cours d'exécution)")
    print(f"   2. Login correct? ({login})")
    print(f"   3. Mot de passe correct?")
    print(f"   4. Serveur correct? ({srv})")
    print(f"   5. Le compte est actif chez le broker?")
    return False

if __name__ == '__main__':
    print("=" * 50)
    print("  TEST CONNEXION MT5 — DIAGNOSTIC")
    print("=" * 50)
    print()
    
    success = test_connection()
    
    print()
    if success:
        print("✅ Tout est bon! Le bot peut démarrer.")
    else:
        print("❌ Problème détecté. Corrigez avant de lancer le bot.")
    
    sys.exit(0 if success else 1)
