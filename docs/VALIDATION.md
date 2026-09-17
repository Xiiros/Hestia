# Checklist de validation terrain

À dérouler lors du **premier montage sur une vraie Raspberry Pi**. Elle vérifie
surtout ce qui n'a **pas pu être testé hors matériel** : sonde DHCP (scapy),
écran e-paper, schéma de l'API AdGuard, et la chaîne OTA de bout en bout.

Cocher au fur et à mesure. Noter la version testée : `______`  Date : `______`
Testeur : `______`

## 0. Points à risque connus (à confirmer en priorité)

Ces éléments reposent sur des hypothèses non vérifiées en conditions réelles :

- [ ] **Schéma de l'API DHCP d'AdGuard** : les champs envoyés par `configure_dhcp`
  (`interface_name`, `v4.gateway_ip`, `range_start`…) correspondent bien à la
  version d'AdGuard Home installée.
- [ ] **Modèle e-paper** : `display.model` correspond au module `waveshare_epd`
  réellement branché ; `width`/`height` sont les bons.
- [ ] **Sonde DHCP (scapy)** : fonctionne sur l'interface réelle avec les
  privilèges du service (root / `CAP_NET_RAW`).
- [ ] **Signature OTA** : la signature produite par la CI (OpenSSL Ed25519) est
  acceptée par la vérification côté appareil (`cryptography`).

## 1. Matériel et système

- [ ] Raspberry Pi reliée en **Ethernet filaire** (pas de Wi-Fi pour le service).
- [ ] Raspberry Pi OS **Lite 64-bit** installé, à jour (`apt full-upgrade`).
- [ ] **SPI activé** : `ls /dev/spidev*` renvoie au moins un périphérique.
- [ ] Port 53 libre : `sudo ss -lntup 'sport = :53'` ne montre pas
  `systemd-resolved` (voir étape 2 du guide).

## 2. AdGuard Home

- [ ] `systemctl status AdGuardHome` → actif.
- [ ] Interface accessible, identifiant/mot de passe définis.
- [ ] DNS chiffré (DoH/DoT) configuré en amont.
- [ ] Depuis la Pi : `dig @127.0.0.1 example.com` répond.
- [ ] Un domaine de pub est **bloqué** (ex. `dig @127.0.0.1 doubleclick.net`
  renvoie `0.0.0.0` ou NXDOMAIN selon la liste).

## 3. Installation de Hestia

- [ ] `scripts/install.sh` s'est terminé sans erreur.
- [ ] `/opt/hestia/.venv/bin/hestia --version` affiche la bonne version.
- [ ] `/etc/hestia/config.toml` renseigné (mot de passe AdGuard, `display`, `dhcp`).
- [ ] `/etc/hestia/update-key.pub` présent (clé publique OTA).
- [ ] Pilote Waveshare présent :
  `/opt/hestia/.venv/bin/python -c "import waveshare_epd"` ne lève pas d'erreur.

## 4. Écran e-paper

- [ ] `systemctl start hestia-agent` puis l'écran affiche le **tableau de bord**
  (ou l'écran de premier démarrage).
- [ ] Texte **lisible**, pas de débordement, bonnes dimensions.
- [ ] Rafraîchissement correct (pas de fantômes persistants après quelques cycles).
- [ ] Les valeurs affichées (requêtes, bloquées, taux) correspondent à AdGuard.

## 5. Premier démarrage (détection DHCP)

> À faire avec le **DHCP de la box encore actif**, puis en le désactivant.

- [ ] Sans marqueur (`/var/lib/hestia/first-boot-done` absent), l'agent lance la
  détection.
- [ ] Avec le DHCP de la box actif : l'écran affiche **« Action requise »** avec
  la **bonne box** détectée et son adresse d'admin.
- [ ] Journaux sans erreur scapy : `journalctl -u hestia-agent -f`.
- [ ] Après désactivation du DHCP de la box : l'écran passe à **« Hestia pret »**.
- [ ] Le marqueur `/var/lib/hestia/first-boot-done` est créé.
- [ ] Si `[dhcp] enable_on_first_boot = true` : le **DHCP d'AdGuard est activé**
  (`GET /control/dhcp/status` → `enabled: true`), avec la bonne passerelle et plage.

## 6. DHCP / DNS pour un vrai client

> Brancher un appareil de test (téléphone, portable) sur le réseau.

- [ ] Le client reçoit un bail dans la **plage configurée**.
- [ ] Le client utilise **la Pi comme DNS** et **la box comme passerelle Internet**.
- [ ] Navigation Internet OK ; pubs/traqueurs **bloqués** (les requêtes
  apparaissent dans AdGuard).
- [ ] Un seul serveur DHCP répond (pas de conflit résiduel).

## 7. Mises à jour OTA (bout en bout)

> Publier une version de test signée sur le canal **beta** et pointer la Pi dessus.

- [ ] `hestia-update` détecte la nouvelle version du canal configuré.
- [ ] Signature **valide** → installée ; le lien `current` pointe sur la nouvelle
  version, l'ancienne est conservée.
- [ ] Artefact **falsifié / non signé** → **refusé** (statut `bad_signature`,
  rien n'est installé).
- [ ] **Rollback** : simuler un contrôle de santé en échec → retour à la version
  précédente, l'agent redémarre correctement.
- [ ] `systemctl list-timers hestia-updater.timer` montre la prochaine exécution.

## 8. Résilience

- [ ] **Redémarrage** de la Pi : les services repartent seuls (`enable` OK), le
  marqueur de premier démarrage est respecté (pas de reconfiguration).
- [ ] **Coupure réseau** temporaire : l'agent affiche « AdGuard indisponible »
  sans planter, et récupère au retour du réseau.
- [ ] Redémarrage d'AdGuard : l'agent se reconnecte (nouvelle session).

## 9. Sécurité et vie privée

- [ ] Interface d'administration d'AdGuard **protégée** et non exposée hors du LAN.
- [ ] **Aucune télémétrie** sortante inattendue (vérifier le trafic de la Pi).
- [ ] Clé **privée** de signature absente de l'appareil (`/etc/hestia` ne contient
  que la clé publique).

## Bilan

- Anomalies relevées → ouvrir une *issue* par point, en référant cette checklist.
- Corrections des hypothèses de la section 0 → mettre à jour le code et la doc
  correspondante (`docs/INSTALL.md`, `hestia/adguard`, `hestia/display`).
