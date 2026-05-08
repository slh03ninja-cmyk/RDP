# Context.md — Projet TradingBot V4

## 📅 Dernière session : 2026-05-09

## 👤 Utilisateur
- **Nom :** SaLah
- **Username Telegram :** @SLH_GZL
- **ID Telegram :** 1632453651
- **Langue :** Français
- **Fuseau :** GMT+8
- **GitHub :** slh03ninja-cmyk

## 📦 Projet
- **Repo :** https://github.com/slh03ninja-cmyk/RDP
- **Type :** Bot de copy trading Telegram → MT5 (MetaTrader 5)
- **Broker :** Exness (compte démo)
- **Fichier principal :** `telegram_listener.py` (v4.3.2, ~2000 lignes)
- **Workflow :** `rdp-tailscale-bot-v4-gzl2.yml`

## 🏗️ Architecture du bot
- **Telegram listener** (Telethon) — écoute 4 canaux de signaux
- **Signal Parser V5** — parse les signaux (symbole, action, zone, TP, SL)
- **MT5 Bridge** — exécute les ordres sur MetaTrader 5
- **Trade Manager** — gère TP partiel, breakeven, trailing stop
- **News Manager** — filtre Forex Factory (news HIGH impact USD/XAU)
- **Supabase Logger** — log distant
- **Dashboard Streamlit** — UI basique

## 🔧 Ce qu'on a fait

### Session 1 (2026-05-08) : Bug retcode=10027
- **Problème :** MT5 refuse les ordres avec retcode=10027
- **Cause :** `trade_expert` vérifié sur `terminal_info()` au lieu de `account_info()`
- **Fix :** `_check_algo()` corrigé + `common.ini` avec `AllowAlgoTrading=1`
- **Commits :** `68fa9cf`, `ddfa8f2`, `78c90b5`

### Session 2 (2026-05-08) : Bug "Autotrading disabled by client" (GitHub Actions)
- **Problème :** Le zip MT5 pré-installé a Algo Trading désactivé par défaut
- **Cause :** Le bouton vert ne peut être activé que manuellement dans l'UI MT5
- **Tentatives :**
  - ❌ `common.ini` avec `AllowAlgoTrading=1` → ne marche pas
  - ❌ Registre Windows → ne marche pas
  - ❌ PyAutoGUI → ne marche pas sur GitHub Actions (pas de bureau interactif)
- **Décision :** Activation manuelle via RDP/Tailscale
- **Fix code :**
  - `_check_algo()` : retry 10×15s au lieu de crash
  - Mode observation : le bot démarre même si algo désactivé
  - Flag `algo_trading_active` vérifié avant chaque ordre
- **Commits :** `834f9d3`, `b440251`, `608eb9b`, `1d4f55b`, `5e7b648`

### Session 3 (2026-05-08-09) : Diagnostic + Fix installation MT5
- **Problème :** Le zip MT5 extrait ne fonctionne pas correctement — les configs ne sont pas lues, les signaux ne s'exécutent pas même après activation manuelle d'Algo Trading
- **Cause racine :** L'installation par zip ne crée pas les bons chemins/registre. Le dossier hash `53785E09...` dans AppData contient la vraie config que MT5 lit, mais le workflow n'y écrivait pas
- **Diagnostic E0 :** Révélé 3 emplacements de config, seul le dossier hash (281 bytes common.ini) compte
- **Tentatives :**
  - ❌ Écrire `common.ini` dans `Program Files\config` et `Terminal\Common\config` → MT5 ignore
  - ✅ Étape D2 : écrire dans le dossier hash après premier lancement → ajouté mais IPC timeout
  - ❌ Attente 30s après restart → insuffisant (IPC timeout -10005)
  - ✅ Attente 60s + retry 10×10s → ajouté
- **Décision finale :** Remplacer le zip par l'installateur officiel `exness5setup.exe /silent`
- **Fix :** Workflow gzl2 modifié pour utiliser l'installateur officiel Exness
- **Commits :** `10389f2`, `12eacca`, `abf5734`, `576112a`

### Workflow final (installateur officiel)
1. ✅ Télécharge `exness5setup.exe` depuis Exness
2. ✅ Installe silencieusement (`/silent`)
3. ✅ Localise `terminal64.exe`
4. ✅ Pre-config `common.ini` + `terminal.ini` avec `AllowAlgoTrading=1`
5. ✅ Lance MT5 avec auto-login (`/login /password /server`)
6. ✅ Attend chargement complet (RAM > 100MB)
7. ✅ Étape D2 : écrit config dans le dossier hash (`53785E09...`)
8. ✅ Redémarre MT5 (attente 60s)
9. ✅ Étape E0 : diagnostic chemins INI
10. ✅ Diagnostic API Python (trade_allowed, trade_expert, tradeapi_disabled)
11. ❌ Lancement bot bloqué (code Telegram requis, manuel)

## ⚠️ Sécurité
- **Tokens GitHub exposés** — À RÉVOQUER :
  - `ghp_...okHD` (session 1)
  - `ghp_...zMc` (session 2, utilisé 2 fois)
  - `ghp_...7zMc` (session 3, utilisé 3 fois)

## 🎯 Prochaines étapes
- [ ] Lancer le workflow avec l'installateur officiel et vérifier les logs
- [ ] Vérifier que le diagnostic API donne ALGO_OK
- [ ] Se connecter en RDP via Tailscale
- [ ] Activer Algo Trading manuellement si nécessaire (bouton vert MT5)
- [ ] Lancer le bot manuellement
- [ ] Vérifier que les trades s'exécutent
- [ ] Révoquer les tokens GitHub exposés
- [ ] Envisager VPS Windows (plus stable, 24/7, ~5-10$/mois)

## 🔄 Plans de secours
1. **VPS Windows** : Le plus fiable — vrai bureau, MT5 24/7
2. **Modifier le zip MT5** : Re-packager avec Algo Trading déjà activé
3. **AutoHotkey** : Script AHK au démarrage de MT5

## 🐛 Bugs connus restants
- Doublon `SignalParser` entre `signal_parser.py` et `telegram_listener.py`
- `_get_filling()` et `_force_filling()` identiques (doublon)
- `check_conflict()` désactivé en mode démo
- `_get_last_pnl()` inefficace
- GitHub Actions timeout 6h
- Encodage Windows cp1252 + emojis
