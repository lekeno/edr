<div align="center">
  <img Alt="Logo_ED_Recon" src="https://edrecon.com/img/icon-192x192.8422df55.png">
  <h1><a href="https://edrecon.com"><b>ED Recon</b></a>
  <br>
  Le Guide</h1>
</div>
<p align=right>
  Rédigé par le <b>CMDR Lekeno</b><br>
  Traduction par le <b>CMDR Lekeno</b><br>
  Version 2.7.7.0
</p>

<h1>Sommaire</h1>

- [Installation](#installation)
  - [Prérequis](#prérequis)
  - [Elite Dangerous Market Connector](#elite-dangerous-market-connector)
  - [ED Recon (aka EDR)](#ed-recon-aka-edr)
  - [Compte EDR](#compte-edr)
- [EDR en quelques mots](#edr-en-quelques-mots)
  - [Affichage](#affichage)
  - [Conseils et aide](#conseils-et-aide)
- [Fonctionnalités Commandants](#fonctionnalités-commandants)
  - [Profils de commandant automatiques](#profils-de-commandant-automatiques)
  - [Profils de commandant manuels](#profils-de-commandant-manuels)
  - [Annotations d'autres commandants](#annotations-dautres-commandants)
    - [Commandes génériques](#commandes-génériques)
    - [Tags d’alignement](#tags-dalignement)
    - [Mémo](#mémo)
  - [Comment interpréter les infos du profil](#comment-interpréter-les-infos-du-profil)
- [Karma EDR](#karma-edr)
  - [Qu'est ce que le Karma EDR?](#quest-ce-que-le-karma-edr)
  - [Comment est-il calculé?](#comment-est-il-calculé)
    - [Détails supplémentaires](#détails-supplémentaires)
- [Fonctionnalités Système](#fonctionnalités-système)
  - [Sitreps](#sitreps)
  - [Distance](#distance)
  - [Signaux connus](#signaux-connus)
  - [Informations sur votre destination](#informations-sur-votre-destination)
  - [Système courant](#système-courant)
- [Fonctionnalités Planète](#fonctionnalités-planète)
  - [Point d'intérêt](#point-dintérêt)
  - [Navigation](#navigation)
  - [Matériaux remarquables](#matériaux-remarquables)
- [Recherche de Services](#recherche-de-services)
- [Materials Features](#materials-features)
  - [Matériaux dépendant du BGS](#matériaux-dépendant-du-bgs)
  - [Recherche de matériaux spécifiques](#recherche-de-matériaux-spécifiques)
  - [Matières premières](#matières-premières)
    - [Profils](#profils)
      - [_Profils personnalisés_](#profils-personnalisés)
  - [Matériaux Odyssée](#matériaux-odyssée)
    - [Évaluation](#évaluation)
    - [Bar de Fleet Carrier](#bar-de-fleet-carrier)
- [Fonctionnalités Vaisseaux](#fonctionnalités-vaisseaux)
  - [Où ai-je parqué mon vaisseau?](#où-ai-je-parqué-mon-vaisseau)
  - [Priorités d’alimentation en énergie](#priorités-dalimentation-en-énergie)
  - [Trouver une place de parking pour votre Fleet Carrier](#trouver-une-place-de-parking-pour-votre-fleet-carrier)
  - [Atterrissage](#atterrissage)
- [Fonctionnalités Escadron](#fonctionnalités-escadron)
  - [Ennemis et alliés de l'escadron](#ennemis-et-alliés-de-lescadron)
    - [Tags](#tags)
- [Fonctionnalités pour les chasseurs de primes](#fonctionnalités-pour-les-chasseurs-de-primes)
  - [Alertes en temps réel](#alertes-en-temps-réel)
  - [Chasse à la prime: Statistiques et Graphiques](#chasse-à-la-prime-statistiques-et-graphiques)
- [Fonctionnalités Powerplay](#fonctionnalités-powerplay)
  - [Chasse Powerplay](#chasse-powerplay)
- [Fonctionnalités Minières](#fonctionnalités-minières)
- [Fonctionnalités Exobiology](#fonctionnalités-exobiology)
  - [Informations sur les biomes](#informations-sur-les-biomes)
    - [Informations sur l'ensemble du système](#informations-sur-lensemble-du-système)
    - [Informations spécifiques pour une planète](#informations-spécifiques-pour-une-planète)
  - [Navigation et suivi des progrès](#navigation-et-suivi-des-progrès)
  - [Recherche de planète propice pour Exobiologie](#recherche-de-planète-propice-pour-exobiologie)
- [HUD d'itinéraire](#hud-ditinéraire)
- [Compagnon Spansh](#compagnon-spansh)
- [Colonies Odyssée](#colonies-odyssée)
- [Intégration avec Discord](#intégration-avec-discord)
  - [Transférer des messages de chat dans le jeu](#transférer-des-messages-de-chat-dans-le-jeu)
    - [Conditions préalables](#conditions-préalables)
    - [Configuration des canaux Discord (webhooks)](#configuration-des-canaux-discord-webhooks)
    - [Fonctionnalités](#fonctionnalités)
      - [_Messages entrants_](#messages-entrants)
      - [_Messages sortants_](#messages-sortants)
      - [_Options de personnalisation_](#options-de-personnalisation)
  - [Envoi du plan de vol de votre Fleet Carrier sur discord](#envoi-du-plan-de-vol-de-votre-fleet-carrier-sur-discord)
  - [Envoi des ordres d'achat/vente de votre Fleet Carrier pour les matériaux Ingénieurs](#envoi-des-ordres-dachatvente-de-votre-fleet-carrier-pour-les-matériaux-ingénieurs)
- [Overlay](#overlay)
  - [Configurations multi-écrans et VR](#configurations-multi-écrans-et-vr)
    - [Placement VR avec SteamVR](#placement-vr-avec-steamvr)
  - [Overlay personnalisée](#overlay-personnalisée)
- [Signalement des crimes](#signalement-des-crimes)
- [Effets sonores](#effets-sonores)
  - [Commandes et options](#commandes-et-options)
  - [Personnalisation](#personnalisation)
    - [_Type d'événements_](#type-dévénements)
- [Annexe](#annexe)
  - [Dépannage](#dépannage)
    - [Rien ne s'affiche / La superposition ne fonctionne pas](#rien-ne-saffiche--la-superposition-ne-fonctionne-pas)
      - [_Vérifiez vos paramètres_](#vérifiez-vos-paramètres)
      - [_Autoriser l'exécution de l'overlay_](#autoriser-lexécution-de-loverlay)
  - [Votre Framerate a pris un coup](#votre-framerate-a-pris-un-coup)
    - [Option 1: désactiver Vsync](#option-1-désactiver-vsync)
    - [Option 2: essayez sans bordure / fenêtré / plein écran](#option-2-essayez-sans-bordure--fenêtré--plein-écran)
    - [Option 3: essayez l'interface utilisateur alternative d'EDR](#option-3-essayez-linterface-utilisateur-alternative-dedr)
  - [D'autres problèmes, non résolus?](#dautres-problèmes-non-résolus)
  - [Considérations relatives à la confidentialité](#considérations-relatives-à-la-confidentialité)

<br><br><br>

# Installation

Si vous êtes bloqué ou si vous avez des questions, n'hésitez pas à rejoindre [EDR central](https://discord.gg/meZFZPj), le serveur communautaire pour EDR avec accès au bot, aux alertes en temps réel et aide pour configurer ou utiliser EDR.

## Prérequis

- Windows
- Elite: Dangerous (LIVE)
- Elite Dangerous Market Connector (voir la [section ci dessous](#elite-dangerous-market-connector))
- Lire et comprendre la [politique de confidentialité](https://edrecon.com/privacy-policy) et les [conditions d'utilisation](https://edrecon.com/tos) d'EDR. **Continuer implique que vous comprenez et acceptez la politique de confidentialité et les conditions d’utilisation des services EDR.**

## Elite Dangerous Market Connector

**Si vous avez déjà installé Elite Dangerous Market Connector (EDMC), [passez à la section suivante](#ed-recon-aka-edr).**

ED Recon est proposé en tant que plugin pour Elite Dangerous Market Connector, un excellent outil tiers pour Elite: Dangerous. Vérifiez les [instructions officielles](https://github.com/EDCD/EDMarketConnector/wiki/Installation-&-Setup) si les explications ci-dessous ne suffisent pas.

Étapes:

1. Lisez la [politique de confidentialité d'EDMC](https://github.com/EDCD/EDMarketConnector/wiki/Privacy-Policy). Si vous n'êtes pas d'accord avec quoi que ce soit ou si vous ne comprenez pas tout, n'allez PAS plus loin.
2. [Téléchargez la dernière version d'EDMC](https://github.com/EDCD/EDMarketConnector/releases/latest) (le fichier .exe)
3. Double-cliquez sur le fichier téléchargé pour l'installer.
   - Il se peut que Windows refuse d'exécuter le fichier. Cliquez sur `Plus d'infos` puis sur `Exécuter quand même`. Si vous êtes inquiet, n'hésitez pas à lancer au préalable une analyse antivirus sur le fichier téléchargé.
4. Exécutez Elite Dangerous Market Connector à partir du menu Démarrer ou de l'écran de démarrage.
5. Configurer l’affichage EDMC en Français depuis les préférences, si nécessaire:
   - Menu `Ficgier`, `Paramètres`, onglet `Apparence`, Sélecteur de langue, Français.
6. Facultatif: autorisez EDMC à accéder à l'API de Frontier en votre nom (**Notez qu’EDR n'utilise PAS l'API Frontier, vous pouvez donc ignorer cette demande d'authentification**).

## ED Recon (aka EDR)

Étapes:

1. [Téléchargez la dernière version d'EDR](https://github.com/lekeno/EDR/releases/latest) (le fichier EDR.v#.#.#.zip où #.#.# est le numéro de version, ex. 1.0.0 dans la capture d'écran)

    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/lekeno/edr/blob/master/edr/docs/assets/EDR_1.0.0_Black.png?raw=true">
      <source media="(prefers-color-scheme: light)" srcset="https://github.com/lekeno/edr/blob/master/edr/docs/assets/EDR_1.0.0_White.png?raw=true">
      <img alt="Screenshot of the release page of EDR 1.0.0" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/EDR_1.0.0_White.png?raw=true">
    </picture>

2. Lancez EDMC.

3. Cliquez sur Fichier puis Paramètres.

    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_01-02_Black.png?raw=true">
      <source media="(prefers-color-scheme: light)" srcset="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_01-02_White.png?raw=true">
      <img alt="How to open EDMC settings" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_01-02_White.png?raw=true">
    </picture>

4. Cliquez sur l'onglet Plugins, puis cliquez sur Ouvrir.

    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_03-04_Black.png?raw=true">
      <source media="(prefers-color-scheme: light)" srcset="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_03-04_White.png?raw=true">
      <img alt="How to go to the plugin tab" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_03-04_White.png?raw=true">
    </picture>

5. Créez un sous-dossier nommé `EDR` dans le dossier `plugins`.

    <img alt="How to access the tab and then the plugins folder" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_05_White.png?raw=true">

6. Décompressez le contenu du fichier Zip que vous avez téléchargé à l'étape 2 directement dans le sous-dossier EDR.

    <img alt="EDR folder creation" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_06_White.png?raw=true">

7. Relancez EDMC.

8. Vous devriez voir une ligne d'état EDR (ex. `EDR: identité (invité)`) au bas de la fenêtre EDMC:

    <img alt="Location and folder structure of EDR" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_07_White.png?raw=true">

9. Lancez Elite: Dangerous, démarrez une nouvelle partie.

10. Vous devriez voir un message d'introduction (ex. EDR V1.0.0 […]) superposé sur Elite.
    - Sous Windows 10: la superposition devrait fonctionner pour tous les modes (Plein écran, Sans bordure, Fenêtré).
    - Sous Windows 7: la superposition ne fonctionne PAS en plein écran, utilisez plutôt Borderless ou Windowed.
    - Si la superposition ne fonctionne pas, consultez la [section de dépannage](#dépannage).

## Compte EDR

EDR fonctionne immédiatement sans aucun compte. Toutefois, si vous souhaitez fournir des informations à EDR et à ses utilisateurs, par ex. envoyer des observations de hors-la-loi, vous devrez [demander un compte](https://edrecon.com/account).

Remarques importantes:

- Les demandes de compte sont examinées manuellement pour maintenir la qualité du service. Cela peut prendre quelques semaines.
- Si vous avez demandé à être contacté via discord: acceptez la demande d'ami en provenance de `LeKeno`.
- Si vous avez demandé à être contacté par e-mail: assurez-vous que les emails en provenance de edrecon.com ne se trouvent pas dans le dossier de spam.

Après avoir obtenu vos informations d'identification, ouvrez les paramètres EDR (menu `Fichier` menu, `Paramètres`, onglet `EDR`), remplissez les champs email et mot de passe en conséquence, puis cliquez sur OK.

<img alt="Where to write email and password in EDMC settings for EDR" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_08_White.png?raw=true">

Si tout se passe comme prévu, vous devriez voir "identité vérifiée" dans la ligne d'état EDR.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_09_Black.png?raw=true">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_09_White.png?raw=true">
  <img alt="Location where it is indicated whether the login was successful" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_09_White.png?raw=true">
</picture>

# EDR en quelques mots

EDR propose un large éventail de fonctionnalités conçues pour faciliter et augmenter votre expérience dans Elite: Dangerous.

- Profil des joueurs basé sur les rapports en jeu
- Recherche de matériaux rares
- Évaluation de la valeur des matériaux d'odyssée, etc.

Ces fonctionnalités se déclenchent soit automatiquement en fonction de ce qui se passe dans le jeu, ou peuvent être déclenchées en envoyant des commandes EDR (ex. `!who lekeno`) via le chat du jeu (n'importe quel canal), ou via le champ de saisie EDR dans la fenêtre EDMC:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_10_Black.png?raw=true">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_10_White.png?raw=true">
  <img alt="Alterative position from where to send EDR commands in EDMC" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_10_White.png?raw=true">
</picture>

### Affichage

EDR affiche diverses informations utiles via une superposition graphique et une interface utilisateur textuelle dans la fenêtre EDMC.

- La superposition peut également être configurée comme une fenêtre autonome pour les configurations multi-écrans ou VR (menu `Fichier` menu, `Paramètres`, onglet `EDR`, `Écran superposé` sur `Séparé`).
- L'interface utilisateur textuel peut être rabattue ou agrandie avec la case à cocher sur le côté droit de la ligne d'état EDR dans EDMC.

### Conseils et aide

Lors du démarrage d'une nouvelle session de jeu, EDR affichera une astuce aléatoire concernant le jeu ou EDR lui-même.

- Vous pouvez aussi envoyer `!help` pour obtenir des conseils courts et simples sur les différentes commandes EDR.
- Si vous souhaitez voir une astuce aléatoire, envoyez la commande `!tip`, ou `!tip edr` pour une astuce EDR, et `!tip open` pour une astuce par rapport au mode Open.

# Fonctionnalités Commandants

## Profils de commandant automatiques

Si EDR détecte la présence d'un commandant potentiellement dangereux (ex. un hors-la-loi), le profil de ce commandant sera automatiquement affiché par EDR.
Exemples:

- Lors de la réception d'un message (direct, local, système, etc.) d'un hors-la-loi.
- Avoir son vaisseau interdit par un hors-la-loi.
- Rejoindre / former une équipe avec un hors-la-loi.
- Lorsqu'un hors-la-loi rejoint une session multi-équipage.

## Profils de commandant manuels

Vous pouvez aussi cibler un autre joueur pour révéler son profil EDR. Pour les utilisateurs disposant d'un compte, ceci entraînera aussi l'envoie des informations au serveur EDR pour le bénéfice d'autres utilisateurs EDR. Vous pouvez aussi déclencher une recherche de profil EDR + Inara avec les options ci-dessous:

- Envoi de **`o7`** au commandant qui vous intrigue (en message direct).
- Envoi de **<tt>!who _cmdrname_</tt>** ou **<tt>!w _cmdrname_</tt>** via le chat en jeu (n'importe quel canal: local, escadron, wing, système, etc.) ou via le champ de saisie EDR dans EDMC. Exemple: **`!w lekeno`**

EDR affichera également des informations clés (points de vie, taille/classe, historique) sur le vaisseau/véhicule de votre cible et le sous-module sélectionné le cas échéant:

<img alt="Interface integrity and hull and shield of the opponent" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_11.png?raw=true">

## Annotations d'autres commandants

Vous pouvez créer votre propre Commander Index (CmdrDex) pour personnaliser votre expérience EDR et aider les autres utilisateurs EDR à mieux évaluer les intentions d'autres commandants. Votre CmdrDex est personnel, EDR n'affichera que des statistiques agrégées pour les tags d'alignement, par ex. 79% hors-la-loi, 25% neutre, 5% exécuteur (abrégé en [!70% ?25%? +5%] dans le jeu).

### Commandes génériques

- `#=` ou `#friend` pour taguer le contact ciblé en tant qu'ami.
- <tt>#= _cmdrname_</tt> ou <tt>#friend _cmdrname_</tt> pour taguer un commandant spécifique en tant qu'ami.
- `-#=` ou <tt>-#friend _cmdrname_</tt> pour supprimer le tag ami sur le contact ciblé ou sur le commandant portant le nom cmdrname.
- `#tag` or <tt>#tag _cmdrname_</tt> pour taguer le contact ciblé ou le commandant portant le nom _cmdrname_ avec un tag personnalisée (ex. `#pirate jack sparrow`).
- `-#` or <tt>-# _cmdrname_</tt> pour supprimer le contact ciblé ou le commandant _cmdrname_ de votre index. (ex. `-# jack sparrow`).
- `-#tag` or <tt>-#tag _cmdrname_</tt> pour supprimer un tag sur le contact ciblé ou sur le commandant _cmdrname_ dans votre index (ex. `-#pirate jack sparrow`).

### Tags d’alignement

Vous pouvez taguer un commandant avec un tag d'alignement et ainsi aider les autres utilisateurs d'EDR à mieux évaluer les intentions d'autres commandants:

- Tag hors-la-loi si vous voyez un commandant poursuivre un autre commandant qui s'avère innocent et non-ennemi.
- Tag justicier si vous voyez un commandant appréhender, de manière systématique, les hors-la-loi.
- Tag neutre si vous n'êtes pas d'accord avec la classification d'EDR et souhaitez supprimer l’avertissement EDR, ou si un commandant semble simplement vaquer à ses propres occupations.

Commandes:

- `#outlaw` ou `#!` pour taguer le contact ciblé avec un tag hors-la-loi.
- <tt>#outlaw _cmdrname_</tt> ou <tt>#! _cmdrname_</tt> pour taguer le commandant _cmdrname_ avec un tag hors-la-loi (ex. `#! Vicious RDCS`).
- `#neutral` ou `#?` pour taguer le contact ciblé avec un tag neutre.
- <tt>#neutral _cmdrname_</tt> ou <tt>#? _cmdrname_</tt> pour taguer le commandant _cmdrname_ avec un tag neutre (ex. `#? filthy neutral jr`).
- `#enforcer` ou `#+` pour taguer le contact ciblé avec un tag justicier.
- <tt>#enforcer _cmdrname_</tt> ou <tt>#+ _cmdrname_</tt> pour taguer le commandant cmdrname avec un tag justicier (ex. `#+ lekeno`).
- <tt>-#_alignment-tag_</tt> or <tt>-#_alignment-tag cmdrname_</tt> pour supprimer le tag _alignement-tag_ du contact ciblé ou du commandant _cmdrname_ (ex. `-#+ lekeno`).

### Mémo

Vous pouvez attacher une petite note à un commandant. Cela peut être utile pour se rappeler des circonstances d’une rencontre avec un autre commandant.

Commandes:

- `@# “quelque chose de très important à retenir”` pour attacher une note personnalisée à un contact ciblé.
- <tt>@# _cmdrname_ memo=“distant worlds 2”</tt> pour attacher une note personnalisée au commandant _cmdrname_.
- `-@#` ou <tt>-@# _cmdrname_</tt> pour supprimer la note personnalisée d'un contact ciblé ou du commandant _cmdrname_.

## Comment interpréter les infos du profil

Le profil inclut des graphiques représentant un historique des infos pour les 12 derniers mois. Le mois en cours est sur le bord droit et l'axe remonte dans le temps à partir de là. En d'autre termes, le mois précédent est la barre à gauche de la dernière barre à droite, et ainsi de suite.

La section supérieure contient une vue combinée (même échelle verticale) des scans clean et scans avec une prime de recherche:

- [En haut] Nombre de scans clean: plus la barre est haute / plus la barre est verte, plus grand est le nombre de scans clean signalés par les utilisateurs EDR.
- [En bas] Nombre de scans avec prime de recherche: plus la barre s'étend vers le bas / plus la barre est rouge, plus grand est le nombre de scans avec prime de recherche signalés par les utilisateurs EDR.

La section inférieure montre la plus grande prime signalée pour un mois donné. La hauteur de la barre est relative aux autres primes signalées. C'est-à-dire que la barre la plus haute représente la prime maximale pour les 12 derniers mois, et une barre à mi-hauteur représente 50 % de cette prime maximale. Le montant de la prime est reflété dans la couleur de la barre: plus la couleur est chaude, plus le montant de la prime est élevé.

<img alt="Framing interface of a graphical box commander" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_12.png?raw=true">

La section textuelle inclut des informations provenant d'EDR et d'[Inara](https://inara.cz/).

La section EDR fournit divers signaux pour vous aider à former une opinion d'un autre commandant. Quoiqu'il advienne, cela reste une interprétation personnelle. **En tant que tel, utilisez toujours votre meilleur jugement et assumez l'entière responsabilité de votre comportement et de vos actions.**

- **EDR Karma:** une valeur entre -1000 et 1000 calculée à partir de l'historique des scans et des primes d'un commandant, tel que rapporté par d'autres utilisateurs d'EDR. La valeur du karma est aussi traduite en trois catégories (Outlaw ou Bandit, ambigu +/-, et Lawful ou Innocent) avec des symboles + pour indiquer le niveau dans une catégorie. Outlaw / Bandit indique qu’un commandant a été scanné avec une prime importante, Ambigu / Ambiguous indique un manque de données, Lawful / Innocent indique une série de scans clean. Voir [Karma EDR](karma-edr) pour plus de détails.
- **Tags de karma:** les utilisateurs EDR peuvent aussi marquer les autres commandants avec des tags prédéfinies (ou personnalisées). Cette section affiche un nombre (ou un pourcentage) de tag pour les catégories prédéfinies qui suivent:
  - bandit (représenté par !)
  - neutre (?)
  - justicier (représenté par +)
  - Si vous rencontrez un commandant avec des tags qui ne collent pas avec leur comportement, veuillez en informez le _Cmdr lekeno_.
- **Résumé sur 90 jours:** représente un sommaire des scans et primes tels que rapportés par les utilisateurs d'EDR pour les 90 derniers jours. L'affichage inclut le nombre de scan clean, le nombre de scan avec prime de recherche, ainsi que la plus grande prime signalée.
- **Divers:** EDR affiche également d'autres types d'information si disponible (ex. vos tags personnalisés).

La section Inara affiche des informations telles que le rôle, l'escadron, l'allégeance, etc en provenance du site Inara si le commandant s'y est inscrit.

<img alt="Framing interface of a commander" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_13.png?raw=true">

# Karma EDR

## Qu'est ce que le Karma EDR?

Il s'agit d'une valeur comprise entre -1000 et 1000 qui essayent de représenter le degré de respect ou d'infraction à la loi d'un commandant. Ce n'est just qu'indice pour informer votre opinion, en combinaison avec d'autres indices ou signaux dans le jeu (ex. vous avez vu le commandant partir à la chasse de commandants sans reproche, ou vous avez vu le commandant piloter un méta FdL recherché dans un CG minier, etc.). **Ne s'agissant que d'un indice parmi d'autres, vous devez continuer d'utiliser votre meilleur jugement et assumer l'entière responsabilité de votre comportement et de vos actions.**

## Comment est-il calculé?

Le karma EDR est actuellement calculé à partir des scans et primes signalées par d'autres utilisateurs EDR. C'est-à-dire que son propre statut juridique, ou ses propres primes, ne sont pas pris en compte; quelqu'un d'autre doit signaler votre statut juridique ou votre prime pour être pris en compte par le système.

Explication simplifiée:

- lorsqu’un commandant est scanné clean, sa valeur de karma augmente.
- lorsqu’un commandant est scanné avec un avis de recherche, sa valeur de karma diminue.
- lorsqu’un commandant est scanné avec une prime, sa valeur de karma peut être réajustée en fonction de la valeur de la prime. Plus la prime est important, plus le karma est ajusté vers l'extrême négatif à -1000.
- si un commandant est scanné après une période prolongée sans signalement, il verra son karma se dégrader au préalable:
  - si le commandant a un karma négatif (Bandit), il obtient le bénéfice du doute avec un boost de karma vers la classification Ambigu.
  - si le commandant a un karma positif (Innocent), il sera soumis à un ajustement conservateur avec une diminution du karma vers la classification Ambigu.

### Détails supplémentaires

L’amplitude des changements du Karma n'est pas uniforme:

- L’amplitude est plus petite vers les extrêmes. En d'autres termes, il est plus difficile d'obtenir le quatrième + (ex. Bandit++++) par rapport au troisième + (Bandit+++), et ainsi de suite. Ceci afin de mettre beaucoup plus de poids derrière chaque + qu'il ne serait possible avec une échelle linéaire.

Un scan avec une prime conséquente peut réduire le karma d’un coup en fonction du montant:

- Le karma est découpé en grades (c'est à dire le nombre de +)
- Chaque grade (y compris le karma Innocent) a un seuil de prime associé.

Si un commandant est scanné avec une prime qui dépasse ce seuil, il verra son Karma réajusté à une valeur plus appropriée (c'est-à-dire Bandit+++ au lieu de Bandit++). Cela s'applique également aux commandants avec un karma Innocent, aussi bien pour éviter des trolls que des commandants classés Innocent++++ qui se mettraient à abuser de leur karma positif.

Pour les commandants qui sont restés hors-radar pendant un certain temps, EDR poussera leur Karma vers la classification Ambigu d'un montant proportionnel au temps écoulé depuis le dernier scan.

Il existe d'autres subtilités telles que les seuils de temps entre les analyses / rapports de primes, ou les aspects de mise en cache côté client qui peuvent affecter le calcul ou refléter la dernière valeur de karma.

# Fonctionnalités Système

## Sitreps

EDR affiche un rapport de situation (aka sitrep) lors du démarrage d'une nouvelle session ou après avoir sauté dans un nouveau système.

Les informations peuvent inclure les éléments suivants:

- NOTAM: un court mémo sur le système (ex.objectif communautaire, hub PvP, point chaud connu, etc.)
- Une liste des hors-la-loi et des commandants récemment aperçus
- Une liste des commandants qui ont récemment interdit ou tué d'autres commandants (sans aucun jugement sur la légalité des actions)

Commandes:

- `!sitreps` pour afficher une liste des systèmes stellaires avec une activité récente (bons candidats pour une commande `!sitrep`).
- `!sitrep` pour afficher le sitrep du système actuel.
- <tt>!sitrep _system name_</tt> pour afficher le sitrep d'un système stellaire donné (ex. `!sitrep deciat`).
- `!notams` pour afficher une liste des systèmes stellaires avec des NOTAM actifs.
- <tt>!notam _system name_</tt> pour afficher le NOTAM d'un système stellaire donné (ex. `!notam san tu`).

## Distance

EDR peut calculer les distances entre votre position et un autre système, ou entre 2 systèmes arbitraires, tant qu'ils sont déjà connus par la communauté.

Commandes:

- <tt>!distance _system name_</tt> indique la distance entre votre emplacement et le nom du système (ex. `!distance deciat`)
- <tt>!distance _origin_ > _destination_</tt> affiche la distance entre l'_origine_ et la _destination_ (ex. `!distance deciat > borann`)

## Signaux connus

EDR affiche un aperçu des signaux connus pour le système actuel (ex. les sites d'extraction de ressources, les zones de combat, les Fleet Carriers, les stations, etc.)

- Une vue d'ensemble s'affiche automatiquement lorsque vous accéder à la carte du système.
- L'envoi de la commande `!signals` permet aussi de déclencher manuellement la vue d'ensemble

## Informations sur votre destination

**Odyssey uniquement:** EDR affiche des informations clés sur votre prochaine destination (s'il s'agit d'un spatioport, d'un Fleet Carrier ou d'un système). Pour les spatioports ou les Fleet Carriers, EDR affiche la liste des services disponibles ainsi que des informations sur la faction contrôlante (état BGS, gouvernement, allégeance et si la faction est soutenue par un groupe de joueurs, alias **P**layer **M**inor **F**action).

## Système courant

EDR montre une estimation de la valeur d'exploration ainsi que les informations clés pour les étoiles, planètes et systèmes. Cette fonctionnalité se déclenche après: un scan du système, une analyse du spectre complet, ou une analyse détaillée de la surface d'une planète.

# Fonctionnalités Planète

## Point d'intérêt

EDR a une liste de points d'intérêt (ex. des vaisseaux écrasés, des bases abandonnées, etc.). Le guidage s'affiche automatiquement lors de l'entrée dans un système avec des points d'intérêt, ainsi qu'à l'approche d'une planète avec des points d'intérêts. Il y aussi une fonction de navigation (cap, distance, altitude, tangage) pour vous aider à atterrir près d'un point d'intérêt.

## Navigation

L’assistance à la navigation vers un point spécifique est également disponible. (L’assistance s’affiche à l'approche d'une planète ou en étant à la surface d'une planète).

Commandes:

- `!nav 123.21 -32.21` pour définir la destination en fonction de sa latitude et de sa longitude.
- `!nav off` pour désactiver la fonction de navigation
- `!nav set` pour définir votre Latitude, Longitude actuelle comme destination pour la fonction de navigation.

## Matériaux remarquables

À l'approche d'une planète, EDR affiche une liste de matériaux remarquables (c'est-à-dire des matériaux avec une densité de présence supérieure à ce qui est typique au travers de la galaxie). Remarque: cette fonction nécessite des actions
préalables telles que scanner la balise de navigation ou analyser le système avec le Full Spectrum Scanner, etc.

Voir plus de détails dans [Fonctionnalités matériaux](materials-features).

# Recherche de Services

EDR peut vous aider à trouver des services près de votre position ou à proximité d'un système spécifique.

Commandes:

- `!if` ou `!if Lave` pour trouver un Interstellar Factors près de votre position ou de Lave.
- `!raw` ou `!raw Lave` pour trouver un négociant en matières premières près de votre position ou Lave.
- `!encoded`, `!enc` ou `!enc Lave` pour trouver un commerçant de données encodées près de votre position ou Lave.
- `!manufactured`, `!man` ou `!man Lave` pour trouver un négociant en matériaux manufacturés près de votre position ou de Lave.
- `!staging` ou `!staging Lave` pour trouver une bonne station de préparation près de votre position ou Lave, c'est-à-dire grandes plateformes, chantier naval, équipement, éparation/réarmement/ravitaillement.
- `!htb`, `!humantechbroker` ou `!htb Lave` pour trouver un Human Tech Broker proche de votre poste ou de Lave.
- `!gtb`, `!guardiantechbroker` ou `!gtb Lave` pour trouver un Guardian Tech Broker près de votre position ou de Lave.
- `!offbeat`, `!offbeat Lave` pour trouver une station qui n'a pas été visitée récemment près de votre position ou de Lave (utile pour trouver des combinaisons spatiales et des armes pré-conçues/pré-améliorées dans Odyssey).
- `!rrr`, `!rrr Lave`, `!rrr Lave < 10` pour trouver une station avec réparation, réarmement et ravitaillement près de votre position, ou lave, ou dans un rayon de 10 AL autour de Lave.
- `!rrrfc`, `!rrrfc Lave`, `!rrrfc Lave < 10` pour trouver un transporteur de flotte avec réparation, réarmement et ravitaillement près de votre position, ou lave, ou dans un rayon de 10 AL autour de Lave. S'il vous plaît, vérifiez l'accès à l'amarrage avant de vous y rendre !
- `!fc J6B`, `!fc recon`, `!station Jameson` pour afficher des informations sur les services au Fleet Carrier ou aux stations locales avec un indicatif/nom contenant respectivement J6B, Recon, Jameson.

# Materials Features

## Matériaux dépendant du BGS

Lorsque vous arrivez dans un nouveau système, EDR affichera parfois une liste de matériaux avec des probabilités estimées (provenant principalement de “sources de signaux”). Si votre inventaire actuel est faible sur un matériau particulier et que la probabilité est relativement élevée, recherchez une source d'émission de haute qualité pour collecter le matériau en question (après avoir vidé l’instance, quittez le jeu complètement, relancez, passez en supercruise, revenez au signal, collectez, répétez jusqu'à la fin du temps imparti).

## Recherche de matériaux spécifiques

Envoyez <tt>!search _ressource_</tt> pour trouver un bon endroit pour collecter une ressource spécifique (ex. `!search selenium`). Vous pouvez utiliser le nom complet de la ressource ou une abréviation. La plupart des ressources très rares, rares et standards (données, brutes, manufacturées) sont supportées. Exception: ressources liées à la technologie des Guardians. Bon à savoir: le nom du système est automatiquement copié dans le presse-papiers.

Abréviations (en Anglais):

- Les 3 premières lettres d'une ressource en un seul mot, ex. `!search cad` pour le cadmium,
- Les premières lettres de chaque mot, séparées par des espaces pour les ressources multi-mots, ex. `!search c d c` pour Core Dynamic Composites.

Les ressources dépendantes de l'état sont les meilleurs efforts, veuillez vérifier les informations obsolètes en regardant la date et l'état via la carte de la galaxie.

La recherche autour d'un système spécifique peut être effectuée en envoyant une commande comme celle-ci (notez le paramètre @systemname à la fin):

- `!search selenium @deciat`

## Matières premières

A l'approche d'une planète, EDR indiquera les matières rares disponibles si leur densité de présence dépasse la médiane galactique (plus il y a de +, mieux c'est).

### Profils

Si vous recherchez des matières premières de qualité inférieure ou quelque chose de spécifique, vous constaterez peut-être que les notifications de matières premières par défaut ne sont pas toujours utiles. Vous pouvez configurer un autre ensemble de matériaux en envoyant la commande !materials.

Par exemple, si vous recherchez des matériaux pour booster votre FSD, envoyez `!materials fsd`. Cela personnalisera les notifications pour n'afficher que les matériaux utilisés pour les injections FSD de synthèse.

Autres commandes:

- `!materials` pour voir la liste des profils disponibles.
- `!materials default` pour revenir au profil par défaut (c'est-à-dire matières premières rares)

#### _Profils personnalisés_

Vous pouvez également ajouter vos propres profils de matières premières:

1. Faites une copie du fichier `raw_profiles.json` (voir le dossier data d'EDR)
2. Renommez-le `user_raw_profiles.json`
3. Modifiez et renommez les profils selon vos besoins.
4. Enregistrez le fichier.

## Matériaux Odyssée

### Évaluation

EDR montrera une évaluation des matériaux Odyssey en fonction des événements suivants:

- Accepter une mission avec un matériau fourni pour la mission.
- Pointer un matériau avec le système gestuel du jeu (utilisations, rareté, emplacements typiques, requis par les ingénieurs ainsi qu’une indication de son utilité en fonction de votre progression, …). Cela fonctionne également pour les matériaux Horizons.

<img alt="On-foot material analysis interface" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_14.png?raw=true">

- Envoi d'une demande d'évaluation avec `!eval backpack`, `!eval locker`, <tt>!eval _nom du matériau_</tt> (ex. des `!eval air quality reports`).
- Validation d'un ordre d'achat ou de vente pour un matériau au bar de votre Fleet Carrier.

De plus, EDR montrera une évaluation des matériaux Odyssey dans le sac à dos ou le stock du joueur sur les événements suivants:

- Vendre des matériaux à un bar.
- Jeter des matériaux.

Ces fonctionnalités sont pratiques car il y a beaucoup de matériaux d'odyssée complètement inutiles…

### Bar de Fleet Carrier

Lorsque vous visitez un bar qui offre des matériaux, EDR vous montrera une liste des matériaux les plus utiles que vous pourriez envisager d'acheter. Chaque matériau est suivi d'une série de lettres + chiffres pour donner un aperçu supplémentaire de la valeur de chaque élément:

- B: nombre de plans utilisant cet élément
- U: nombre d'améliorations utilisant cet élément
- X: valeur marchande aux barres de station (pour échange)
- E: nombre d'ingénieurs déverrouillés

Si un bar n'a rien en stock, ou rien d'utile en stock, alors EDR affichera une liste des matériaux les moins utiles dont vous pourriez vous débarrasser au bar. Utilisez ces informations pour faire le ménage dans votre inventaire en vendant les choses les moins utiles.

Vous pouvez également déclencher ces évaluations pour le dernièr bar que vous avez visitée avec la commande suivante:

- `!eval bar` ou `!eval bar stock` pour évaluer les articles en vente.
- `!eval bar demande` pour évaluer les articles recherchés par le propriétaire du transporteur de la flotte.

    <img alt="Example of the interface and materials for the bar" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_15.png?raw=true">

# Fonctionnalités Vaisseaux

## Où ai-je parqué mon vaisseau?

EDR peut vous dire où vous avez garé vos vaisseaux.

Commandes:

- <tt>!ship _shiptype_</tt> pour trouver des vaisseaux d'un certain type (ex. \`!ship mamba')
- <tt>!ship _shipname_</tt> pour trouver des vaisseaux avec un certain nom (ex. `!ship Indestructible II`)
- <tt>!ship _shipid_</tt> pour trouver des vaisseaux avec un certain ID (ex. `!ship EDR-001`)

Remarque: cette fonctionnalité indiquera aussi l'ETA pour un vaisseau en train de transfert.

## Priorités d’alimentation en énergie

EDR peut évaluer la qualité de vos priorités d’alimentation en énergie pour une survie maximale. Remarque: cette fonctionnalité est un peu floue en raison d'un tas de bugs dans l'implémentation de Fdev.

Commande:

- `!eval power` pour obtenir une évaluation de vos priorités en matière d'alimentation.
- Si cela ne fonctionne pas, regardez votre panneau de droite, modifiez les priorités d'alimentation d'avant en arrière et réessayez.

## Trouver une place de parking pour votre Fleet Carrier

La commande !parking est là pour vous aider à trouver une place de parking pour votre transporteur de flotte.

- Envoyez `!parking` pour obtenir des informations sur les places de
  stationnement à votre emplacement actuel.
- Essayez les systèmes à proximité en envoyant `!parking #1`, `parking #2`, etc., pour obtenir des informations sur les emplacements de stationnement au système #1, #2, ... à proximité de votre emplacement actuel.
- Envoyez `!parking Deciat` ou `!parking Deciat #3` pour rechercher des emplacements de parking dans ou à proximité de Deciat (ou un système de votre choix).

Comme toujours, EDR copiera le nom du système dans votre presse-papiers, afin que vous puissiez rechercher celui-ci depuis la carte de la galaxie.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_16_Black.png?raw=true">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_16_White.png?raw=true">
  <img alt="Explanation of the interface of where the Fleet Carrier is parked" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_16_White.png?raw=true">
</picture>

## Atterrissage

EDR affichera des informations clés sur une station lors d’une demande d’atterrissage. Vous verrez aussi l'emplacement de votre aire d'atterrissage pour les stations Coriolis, Orbis, ainsi que les Fleet Carrier et certaines bases planétaires.

<img alt="Example of a planetary station interface when requesting the dock" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_17.png?raw=true">

# Fonctionnalités Escadron

## Ennemis et alliés de l'escadron

Si vous faites partie d'un escadron sur [Inara](https://inara.cz/), vous pouvez utiliser EDR pour marquer d'autres joueurs comme ennemis ou alliés de votre escadron. Cette fonctionnalité nécessite d'être un membre actif d'un escadron sur Inara et d’avoir un rang suffisamment élevé.

- Accès en lecture: copilote et supérieur.
- Accès en écriture: ailier et supérieur.
- Mise à jour/suppression d'un tag: rang égal ou supérieur à celui de la personne qui a tagué le joueur

### Tags

Envoyez les commandes suivantes pour marquer un autre joueur (ex. `#ally David Braben`) ou votre cible (ex. `#ally`) en tant qu'ennemi ou allié de votre escadron:

- `#ally` ou `#s+` pour marquer un commandant comme allié.
- `#ennemi` ou `#s!` marquer un commandant comme ennemi.
- `-#ally` ou `-#s+` pour supprimer une balise d'allié d'un commandant.
- `-#ennemi` ou `-#s!` pour retirer une balise ennemie d'un commandant.

# Fonctionnalités pour les chasseurs de primes

Envoyez les commandes suivantes pour obtenir des informations sur les bandits:

- `!outlaws` pour afficher une liste des hors-la-loi les plus récemment aperçus et leurs emplacements.
- <tt>!where _cmdrname_</tt> pour afficher le dernier signalement de _cmdrname_ (à condition qu'EDR les considère comme des bandits).

## Alertes en temps réel

Envoyez les commandes suivantes pour activer ou configurer les alertes en temps réel:

- `?outlaws on` pour activer les alertes en temps réel sur les hors-la-loi.
- `?outlaws off` pour désactiver les alertes en temps réel sur les hors-la-loi.
- `?outlaws cr 10000` pour fixer une prime minimale de 10k crédits.
- `?outlaws ly 120` pour fixer une distance maximale de 120 années-lumière de votre emplacement.
- `?outlaws cr -` pour supprimer la condition de prime minimale.
- `?outlaws ly -` pour supprimer la condition de distance maximale.

## Chasse à la prime: Statistiques et Graphiques

À FAIRE

# Fonctionnalités Powerplay

## Chasse Powerplay

Si vous avez été engagé assez longtemps à un pouvoir, vous pouvez utiliser les commandes suivantes pour obtenir des informations sur vos ennemis:

- `!enemies` pour afficher une liste des derniers ennemis aperçus et leurs emplacements.
- <tt>!where _cmdrname_</tt> pour afficher le dernier signalement de _cmdrname_ (à condition qu'EDR les considère comme un de vos ennemis).

# Fonctionnalités Minières

EDR affiche diverses statistiques et informations pour vous aider à miner plus efficacement (voir [cette vidéo](https://www.youtube.com/watch?v=1bp_Q3JgW3o) pour plus de détails):

<img alt="Example of mining assistance interface with explanation of parameters" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_18.png?raw=true">

De plus, EDR vous rappellera de vous réapprovisionner en drones avant de quitter la station.

# Fonctionnalités Exobiology

## Informations sur les biomes

### Informations sur l'ensemble du système

EDR indiquera si un système a des planètes avec les bonnes conditions pour l'exobiologie. Les informations s'afficheront lors du saut dans un système, après un scan de découverte, ou en envoyant la commande `!biology` sans aucun paramètre. Notez que l'information est une estimation, vérifiez la carte du système pour la présence de signaux biologiques et envisagez de scanner le système et/ou d'effectuer un scan planétaire pour plus de précision.

### Informations spécifiques pour une planète

EDR peut estimer quelles espèces biologiques sont susceptibles d'apparaître sur une planète en fonction de ses conditions atmosphériques et de son type. Les informations sont affichées dans les scénarios suivants:

- En ciblant une planète (voir les lignes “Bio attendue” et “Progression”), ou en envoyant la commande !biology pour une planète donnée (ex. `!biology A 1`):

  <img alt="Example of a planet's information interface with biological material" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_19.png?raw=true">

- Après avoir cartographié l'ensemble de la planète, EDR mettra à jour les informations “Bio attendue” pour refléter les genres réels que vous pouvez trouver sur la planète. Remarque: les espèces sont toujours les meilleures suppositions d'EDR.

  <img alt="Example of interface of relevant information of a planet with biological material" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_20.png?raw=true">

## Navigation et suivi des progrès

Pour améliorer votre efficacité avec les activités d'Exobiologie, EDR propose les fonctionnalités suivantes:

- Informations clés pour les espèces actuellement suivies:

  <img alt="Example of biological material information interface and how far to move for the next scan" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_21.png?raw=true">

  De haut en bas:

  - Nom de l'espèce.
  - Valeur en crédits de l'espèce.
  - Distance minimale requise pour la diversité génétique.
  - Distance et angle de cap par rapport aux échantillons précédents (si le cercle est rempli, cela signifie qu'il y a suffisamment de distance par rapport à un échantillon donné).

- Après avoir échantillonné avec succès une espèce (3 échantillons), EDR montrera vos progrès jusqu'à présent:

  <img alt="Example of an information interface on the scanning status of the biological forms available on the planet" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_22.png?raw=true">

  - Nombre de genres analysés par rapport au nombre total de genres connus.
  - Nom des genres analysés.
  - Nombre d'espèces analysées.

- Si vous rencontrez d'autres espèces en cours de route, vous pouvez enregistrer leurs positions. Cela peut se faire soit via le scanner de composition (vaisseau, srv), soit en utilisant le geste “pointer” à pied.
  - Ces points d'intérêt personnalisés peuvent être parcourus/rappelés en envoyant les commandes `!nav next` ou `!nav previous`.

  - Vous pouvez également effacer le POI actuel en envoyant la commande `!nav clear` et effacer tous les POI personnalisés en envoyant la commande `!nav reset`.

  - Remarque: ces points d'intérêt personnalisés sont éphémères (ex. effacés lorsque EDMC est fermé).

    <img alt="Example of a navigator interface that takes you to the next point" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_23.png?raw=true">

  - En haut: angle de cap à viser pour être sur la bonne voie.

  - Nom du point de navigation, et heure à laquelle il a été enregistré.

  - Distance.

  - Latitude et longitude

  - Angle de cap au moment où le point de navigation a été enregistré.

## Recherche de planète propice pour Exobiologie

Envoyez `!search genus` pour trouver une planète proche avec les conditions connues pour un genre donné (ex. `!search stratum`). Vous pouvez également utiliser le nom complet de l'espèce (ex. `!search stratum tectonicas`), ou certains types de planètes (ex. `!search water`, `!search ammonia` ou `!search biology`). Astuce: envoyez `!search` avec les premières lettres d'une espèce, d'un genre (ou d'une ressource pour ingénieur).

# HUD d'itinéraire

EDR affichera un aperçu d'un itinéraire tracé sur la carte de la galaxie tant que celui ci n'est pas trivial (moins de 3 sauts) ou trop complexe (plus de 50 sauts). Ce “HUD d'itinéraire” sera également affiché lors du saut vers la prochaine étape de la route.

Le HUD fournit les informations suivantes:

- Noms des systèmes actuel, suivant et destination de la route.

- Les noms non génériques des systèmes en cours de route.

- Un symbole visuel indiquant si l'étoile principale d'un système est récupérable (cercle) ou non (croix). Remarque: la couleur du symbole représente le type de l'étoile principale (notez que le waypoint actuel est toujours en bleu).

    <img alt="Example of interstellar navigation assistance interface, indicates different components for the various jumps to be made" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_24.png?raw=true">

- Les étoiles uniques ou dangereuses sont notées par un préfixe descriptif après le nom du système (ex. Neutron, White Dwarf, Black Hole, etc.).

- Statistiques sur l'itinéraire et votre progression.
  - Sur le système de démarrage, vous trouverez les informations suivantes:
    - Combien de sauts depuis le départ.
    - Distance depuis le départ.
    - Temps écoulé.

        <img alt="Example of interstellar navigation assistance interface, indicates route progress details (start system name, how many jumps you have made, distance from the start system and elapsed time)" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_25.png?raw=true">

  - Sur le système suivant, vous trouverez les informations suivantes:
    - une moyenne de la durée entre chaque saut (ex. 18 sec/j = 18 secondes par saut).
    - une estimation de votre vitesse de saut (ex. 1780 LY/HR = 1780 années-lumière par heure).

       <img alt="Example of interstellar navigation assistance interface, indicates route progress details on current system (current system name, average time to jump, average speed per hour in Ly/Hr)" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_26.png?raw=true">

  - Sur le système de destination, vous trouverez les informations suivantes:
    - Combien de sauts restants pour atteindre la destination.
    - Distance restante jusqu'à la destination.
    - Estimation du temps restant pour atteindre la destination

        <img alt="Example of interstellar navigation assistance interface, indicates route progress details on the final system (current system name, remaining hops, remaining distance and remaining time to the arrival system)" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_27.png?raw=true">

# Compagnon Spansh

EDR intègre un ensemble de fonctionnalités pour tirer le meilleur parti de [Spansh](https://spansh.co.uk/), qui est un site Web proposant divers outils de routage. EDR vous aidera aussi à comprendre votre progression, comme indiqué ci-dessous:

<img alt="Example of interface for Spanish integration, indicates the jumps to be made, the time needed and other information" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_28.png?raw=true">

- Systèmes de départ et de destination.
- Waypoint actuel et nombre total de waypoints.
- Nombre de corps à contrôler (pour certains types de routes espagnoles).
- ETA, distance restante et sauts.
- Statistiques: LY par heure, sauts par heure, LY par sauts, temps passé entre chaque saut, etc.

Principales caractéristiques:

- Envoyez `!journey new` pour commencer à créer un itinéraire en espagnol avec des informations pré-remplies (ex. votre distance de saut, votre position actuelle). Notez que vous pouvez également spécifier une destination (ex. `!journey new colonia`).
- L'envoi de `!journey fetch` tentera de télécharger une route espagnole à partir de son adresse/URL. (**Notez que l'adresse/URL doit d'abord être copiée dans le presse-papier!**).
- EDR avancera automatiquement l'itinéraire au fur et à mesure que vous vous dirigez vers le waypoint actuel et placera le prochain waypoint dans le presse-papiers pour votre commodité (c'est-à-dire pour faciliter le traçage de l'itinéraire jusqu'au prochain waypoint).
- Pour les itinéraires Spansh plus avancés (ex. Road to Riches, exomastery), EDR fournit également des informations sur les planètes à vérifier sur chaque waypoint. Envoyez `!journey bodies` pour obtenir la liste détaillée.
  - L'EDR marquera automatiquement une planète comme analysée (ex.cartographié pour Road to Riches, entièrement documentée ou en quittant son orbite pour l'exomastery).
  - Vous pouvez également marquer manuellement une liste de planètes en envoyant la commande `!journey check` (ex. `!journey check 1 A`, ou `!journey check 1 A, 1 B, 2 D`).
- Envoyez `!journey next` ou `!journey previous` pour ajuster manuellement le waypoint actuel.
- Si vous quittez le jeu au milieu d'un parcours, EDR reprendra le parcours là où vous l'avez laissé lors de la session suivante.

Autres commandes:

- `!journey overview` pour afficher des informations clés sur le trajet.
- `!journey waypoint` pour afficher des informations clés sur l’étape actuelle.
- `!journey load` pour charger manuellement un trajet depuis un fichier csv (journey.csv par défaut si aucun paramètre n'est fourni).
- `!journey clear` pour dire à EDR de ne plus suivre le trajet le cas échéant
- L'envoi de `!journey` sans aucun paramètre tentera de faire la bonne chose à chaque fois que la commande est envoyée:
  - S'il n'y a pas de trajet: récupérez un trajet Spansh depuis une URL dans le presse-papiers, ou chargez un trajet local depuis un fichier csv, ou démarrez un nouveau trajet Spansh dans le cas contraire.
  - S'il y a un trajet, montrer son aperçu.

# Colonies Odyssée

Vous pouvez utiliser la commande `!search` pour trouver des colonies Odyssey spécifiques.
Voici quelques exemples:

- `!search anarchy` trouvera la colonie anarchique la plus proche autour de votre position actuelle.
- `!search anarchy @ Lave` trouvera la colonie anarchique la plus proche autour de Lave.
- Tous les types de gouvernement connus sont pris en charge (ex. `!search democracy`)
- Autres conditions prises en charge:
  - États BGS (ex. `!search bust`)
  - Allégeances (ex. `!search imperial`)
  - Économies (ex. `!search tourism`)
- Plusieurs conditions peuvent être combinées pour restreindre la recherche (ex. `!search anarchy, military`)
- Enfin, des conditions peuvent également être exclues. Par exemple, `!search anarchy, -military` trouvera le règlement anarchique non militaire le plus proche. Remarque: par défaut, EDR exclut les états de guerre et de guerre civile, mais vous pouvez annuler cela en ajoutant ces conditions à votre commande (ex. `!search war, civil war` trouvera la colonie la plus proche dont l'état est considéré comme étant soit une guerre, soit une guerre civile).
- Deux raccourcis pratiques sont également fournis: `!search cz` pour trouver la colonie la plus proche qui est probablement une zone de combat, et `!search restore` pour trouver la colonie la plus proche qui est probablement abandonnée.

**Important**: en raison de la nature dynamique du BGS d'Elite Dangerous, il n'est pas garanti à 100 % que la fonction de recherche renvoie toujours des résultats parfaits. Utilisez les informations affichées par EDR lorsque vous approchez la colonie pour confirmer que les conditions réelles correspondent à ce que vous attendiez.

# Intégration avec Discord

Voici les fonctionnalités d'intégration Discord disponibles:

- Transférer les messages de discussion en jeu vers un canal discord de votre choix.
- Envoi des plans de vol de Fleet Carrier sur un canal discord de votre choix.
- Envoi d'ordres de marché aux transporteurs de flotte (achat/vente) pour les matières premières et les matériaux d'odyssée.

## Transférer des messages de chat dans le jeu

Vous pouvez configurer EDR pour transférer directement les messages de discussion en jeu vers un serveur Discord et un canal de votre choix.
Veuillez noter ce qui suit:

- Cela doit être configuré par vous. Par défaut, EDR ne transfère rien du tout.
- Si vous le configurez, le plugin EDR EDMC enverra directement les messages à votre serveur/canal Discord.
- Le backend EDR (serveur) n'est PAS du tout impliqué. **En d'autres termes, vos messages ne sont jamais partagés avec EDR, ni envoyés aux serveurs EDR.**
- _Ai-je mentionné que les messages que vous recevez et envoyez restent privés? Je l'ai fait? OK!_

### Conditions préalables

L'intégration de Discord nécessite les éléments suivants:

- Avoir [Discord](http://discord.com) et un serveur Discord personnel (ou un serveur que vous pouvez administrer ou demander à un administrateur de suivre les instructions).
- Connaître les bases sur les [webhooks dans Discord](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).

### Configuration des canaux Discord (webhooks)

Dans le dossier de configuration, recherchez un fichier nommé user\_config\_sample.ini et suivez les instructions.

### Fonctionnalités

L'intégration Discord offre les fonctionnalités suivantes:

#### _Messages entrants_

- Possibilité de transférer les messages reçus sur l'un des canaux du jeu (ex. local, système, aile, escadron, chefs d'escadron, équipage) vers un serveur Discord et un canal de votre choix (configurable par source).
- Possibilité de configurer si et comment les messages sont transmis pour chaque source et pour des commandants spécifiques. Voir les [options de personnalisation ci-dessous](#options-de-personnalisation).
- Possibilité de transférer les messages directs envoyés pendant que vous êtes AFK vers un serveur Discord et un canal de votre choix.

#### Messages sortants

- Possibilité d'envoyer des messages spécifiques à un serveur discord et à un canal de votre choix via la commande de chat `!discord` dans le jeu (ex. `!discord sur le point d'encaisser une mission, quelqu'un est-il intéressé par des crédits?`)
- Possibilité de transférer les messages envoyés sur l'un des canaux du jeu (ex. local, système, aile, escadron, chefs d'escadron, équipage) vers un serveur Discord et un canal de votre choix (configurable par source).

#### Options de personnalisation

Vous pouvez définir un ensemble de conditions de base pour le transfert par EDR. Ces conditions peuvent être modifiées pour des canaux spécifiques et des commandants spécifiques.

- `blocked`: booléen. Si défini sur true, bloque le transfert.
- `matching`: liste d'expressions régulières. Utilisez ceci pour limiter le transfert aux messages qui correspondent à au moins une de ces expressions régulières.
- `mismatching`: liste d'expressions régulières. Utilisez ceci pour limiter le transfert aux messages qui ne correspondent à aucune de ces expressions régulières.
- `min_karma`: nombre entre -1000 et 1000. Utilisez ceci pour limiter le transfert aux messages dont le karma EDR de l'auteur est supérieur à la valeur définie.
- `max_karma`: nombre entre -1000 et 1000. Utilisez ceci pour limiter le transfert aux messages dont le karma EDR de l'auteur est inférieur à la valeur définie.
- `name`: pour remplacer le nom du cmdr par quelque chose de votre choix.
- `color`: pour remplacer la couleur de l'intégration montrant des informations supplémentaires (RVB en décimal tel que 8421246; par défaut: rouge à vert en fonction du karma EDR du cmdr).
- `url`: pour remplacer le lien de l'intégration (par défaut: profil Inara le cas échéant).
- `icon_url`: pour remplacer l'icône dans l'intégration (par défaut: photo de profil Inara, le cas échéant, ou une icône unique générée automatiquement; attend une URL pour une image).
- `image`: utilisez ceci pour forcer une image dans l'intégration (par défaut: aucune image; attend une URL pour une image).
- `thumbnail`: utilisez cette option pour forcer une vignette dans l'intégration (par défaut: pas de vignette; attend une URL pour une image).
- `tts`: fonction de synthèse vocale de Discord (définie sur "true" si vous voulez que Discord lise le message de ce commandant à haute voix; vous devez être sur le bon canal Discord pour l'entendre).
- `spoiler`: définissez sur true si vous souhaitez masquer les messages de ce commandant derrière un spoiler (nécessite un clic pour révéler le contenu).

Exemple d'[un [bon fichier de configuration](https://imgur.com/a/2fflOo0). Explication:

- le niveau supérieur est utilisé pour définir les valeurs par défaut pour chaque commandant (ex. second):
  - les messages contenant git gud ne sont jamais transférés et l'expéditeur doit avoir un karma EDR supérieur à -100.
- les messages du commandant nommé Cranky North Star seront
  toujours bloqués.
- un commandant nommé Chatty Plantain a une règle de renommage pour forcer “[PNJ] Chatty Plantain” comme son nom de commandant, ses messages sont aussi cachés derrière un spoiler.
- changements par canal (ex. joueur, wing, escadron, chefs escadron, team) pour supprimer les restrictions mismatching et relatifs au karma.

Voir le fichier `user_discord_players.txt` dans le dossier de configuration pour plus d'instructions (votre fichier personnalisé doit être nommé `user_discord_players.json` et ne doit contenir aucun commentaire, c'est-à-dire aucune ligne ne doit commençer par `;`).

## Envoi du plan de vol de votre Fleet Carrier sur discord

Vous pouvez envoyer le plan de vol de votre Fleet Carrier vers EDR Central ou un canal Discord de votre choix. Pour EDR Central, sélectionnez Public dans les options d'EDR (rubrique: Diffusions). Pour le second choix, vous avez 2 options:

- (Préférable) Sélectionnez Direct dans les options d'EDR pour que votre plan de vol aille directement vers Discord. Vérifiez le reste des instructions dans le fichier `user_config_sample.ini` qui se trouve dans le dossier de config d'EDR.
- (Obsolète) Sélectionnez Privé dans les options d'EDR pour que votre plan de vol aille d'abord vers le serveur EDR, pour être retransmis vers Discord. Cette option peut être utile au cas où les propriétaires du serveur ne souhaitent pas partager directement l'URL du webhook pour éviter les abus. Passer par EDR permet de virer les abuseurs sans avoir à reconfigurer et recommuniquer le webhook aux autres utilisateurs. Ouvrez [ce formulaire](https://forms.gle/7pntJRpDgRBcbcfp8) et suivez les étapes ci-dessous:

1. [Créez un webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks#:~:text=making%20a%20webhook) pour le canal dans lequel vous souhaitez voir les plans de vol.
2. Copiez l'adresse de ce webhook et soumettez-le via [le formulaire](https://forms.gle/7pntJRpDgRBcbcfp8).
3. Attendez quelques jours / une semaine. Envoyez un message à _lekeno_ si rien ne se passe après environ une semaine.

## Envoi des ordres d'achat/vente de votre Fleet Carrier pour les matériaux Ingénieurs

Vous pouvez envoyer vos ordres d'achat/vente de matières premières et de matériaux Odyssey vers un canal Discord de votre choix. Vérifiez le reste des instructions dans le fichier `user_config_sample.ini` qui se trouve dans le dossier config d'EDR.

<img alt="Example of post on discord of requests to buy and sell materials in the bar" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_29.png?raw=true">

EDR placera également un résumé des commandes de vente/d'achat récentes dans le presse-papiers, après avoir validé les modifications à votre marché et/ou à votre bar. Vous pouvez copier-coller ce résumé dans le forum officiel pour Elite par exemple.

# Overlay

## Configurations multi-écrans et VR

Si vous avez une configuration multi-écrans ou un casque VR, vous pouvez définir la superposition sur autonome (menu Fichier, Paramètres, onglet EDR, liste déroulante Superposition). La superposition apparaîtra dans une fenêtre séparée avec quelques commandes visuelles:

<img alt="Example interface when the overlay is set as standalone" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_30.png?raw=true">

- **Coin supérieur gauche**: glisser-déposer pour déplacer la superposition, double-cliquer pour maximiser/restaurer.
- **Coin inférieur gauche**: survolez pour rendre la superposition transparente.
- **Coin inférieur droit**: saisissez pour redimensionner la superposition.
- **Coin supérieur droit**: survolez pour rendre la superposition opaque.
- **Carré vert en haut au milieu**: survolez pour que la superposition soit toujours en haut.
- **Carré rouge en bas au milieu**: survolez pour que la superposition soit une fenêtre normale (pas toujours en haut).

### Placement VR avec SteamVR

1. Lancer EDMC
2. Configurez les paramètres EDR (menu Fichier EDMC, Paramètres, onglet EDR) avec la superposition définie sur "Autonome"
3. Lancez le jeu en VR
4. Lancer une session de jeu
5. La superposition devrait démarrer automatiquement, ajuster sa taille et sa position selon les besoins (en dehors de la VR)
6. Lancez le menu du tableau de bord de SteamVR, sélectionnez "Desktops", puis sélectionnez le bon bureau s'il en existe plusieurs
7. Cliquez sur le +, sélectionnez `EDMCOverlay V1.1.0.0`
8. Ajuster la position et la taille en VR
9. Fermer le tableau de bord de SteamVR

    <img alt="Example of interface when the overlay is integrated into the VR headset" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_31.png?raw=true">

Consultez également ces [notes de mise à jour SteamVR](https://steamcommunity.com/games/250820/announcements/detail/2969548216412141657) pour plus de détails.

## Overlay personnalisée

Pour personnaliser la superposition, faites une copie de `igm_config.v7.ini` et `igm_config_spacelegs.v7.ini`, trouvés dans le dossier config, et renommez-les en `user_igm_config.v7.ini` et `user_igm_config_spacelegs.v7.ini` (notez s'il existe des versions supérieures que v7, utilisez plutôt ces numéros de version).

Le premier fichier sert à configurer la superposition à bord d'un vaisseau ou d'un SRV, tandis que le second fichier sert à configurer la superposition quand le commandant est à pied.

Suivez les instructions de chaque fichier pour ajuster les couleurs et les positions des divers éléments/messages. Vous pouvez également désactiver des types de messages spécifiques. Au fur et à mesure que vous apportez des modifications au fichier de configuration de superposition, envoyez la commande `!overlay` pour relire la mise en page, et pour afficher des données de test afin de vérifier vos ajustements.

# Signalement des crimes

Si vous ne souhaitez pas signaler les interactions ou les combats (ex. dans un scénario de PvP consensuel), sachez que vous pouvez désactiver le signalement des crimes. Ceci étant dit, EDR continuera à signaler les scans et repérages de pilotes.

- Pour désactiver le signalement des crimes, envoyez `!crimes off` ou décochez l'option “Signalement des crimes” dans le panneau des paramètres d'EDR.
- Pour activer le signalement des crimes, envoyez `!crimes on` ou cochez l'option “Signalement des crimes” dans le panneau des paramètres d'EDR.
- Vous pouvez aussi confirmer la configuration actuelle en envoyant `!crimes`.

# Gestes
## Commandes et options
L'utilisation de gestes pour déclencher les fonctionnalités EDR peut être désactivée ou activée via les commandes de chat `!gesture off` ou `!gesture on`.

# Sounds Effects
## Commands and options
Sound effects can be disabled or enabled from the EDR options in EDMC (`File` menu, `Settings`, `EDR` tab, `Feedback` section, `Sound` checkbox), or via the `!audiocue off` or `!audiocue on` chat commands.

# Effets sonores

## Commandes et options

Les effets sonores peuvent être désactivés ou activés à partir des options EDR dans EDMC (menu `Fichier`, `Paramètres`, onglet `EDR`, section `Commentaires`, case à cocher `Son`), ou via les commandes de chat `!audiocue off` ou `!audiocue on`.

## Personnalisation

Pour personnaliser les effets sonores, faites une copie du fichier `sfx_config.v1.ini`, qui se trouve dans le dossier config, et renommez-le `user_sfx_config.v1.ini`

Il y a 2 sections, une appelée `[SFX]` et une autre appelée `[SFX_SOFT]`. Le premier est pour les sons lorsque les effets sonores d'EDR sont réglés sur fort (via `!audiocue loud`), le second est pour quand EDR est réglé sur bas (via `!audiocue soft`)

- Chaque ligne représente un type particulier d'événement EDR.
- Pour désactiver un événement, laissez la valeur vide.

Placez vos sons personnalisés (format wav uniquement) dans le sous-dossier custom du dossier sounds.

Modifiez ensuite la ligne de l'événement associé pour spécifier votre son personnalisé, y compris le préfixe `custom/`.

#### Type d'événements

- `startup`: lorsque EDR démarre au début d'une session
- `intel`: quand EDR montre le profil d'un joueur neutre/loyal
- `warning`: quand EDR affiche le profil d'un joueur hors-la-loi
- `sitrep`: lorsque EDR affiche un résumé de l'activité d'un système (ou de tous les systèmes)
- `notify`: lorsque EDR affiche des informations en réponse à d'autres commandes (ex. !eval, etc.)
- `help`: quand EDR affiche l'interface d'aide via !help
- `navigation`: lorsque EDR affiche/met à jour l'UX de navigation
- `docking`: lorsque l'EDR affiche des instructions d'amarrage
- `mining`: quand EDR affiche des conseils de minage
- `bounty-hunting`: lorsque l'EDR affiche des conseils de chasse aux primes
- `target`: lorsque EDR affiche des informations sur une cible (ex. bouclier/coque, points de vie du sous-module)
- `searching`: quand EDR lance une recherche de service ou de matière rare
- `failed`: lorsque EDR rencontre une erreur
- `jammed`: lorsque les serveurs EDR sont trop occupés pour traiter vos requêtes
- `biology`: quand EDR affiche les informations de navigation pour les activités d'Exobiologie

# Annexe

## Dépannage

### Rien ne s'affiche / La superposition ne fonctionne pas

#### _Vérifiez vos paramètres_

Assurez-vous que vous n'avez pas désactivé la superposition par erreur.

Etapes:

1. Lancez EDMC.

2. Cliquez sur Fichier, puis sur Paramètres.

3. Cliquez sur l'onglet EDR.

4. Dans le menu déroulant superposé, sélectionnez Activé.

    <img alt="Setting menu, EDR tab, point where to activate the overlay" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_32.png?raw=true" height="450">

5. Dans Elite, revenez au menu principal et lancez une nouvelle partie.

Toujours rien? Vérifiez la section suivante.

#### _Autoriser l'exécution de l'overlay_

Par précaution, il se peut que votre antivirus empêche l'overlay de s'exécuter.

Suggestion: analysez l'exécutable et autorisez-le à s'exécuter après avoir confirmé qu'il ne présente aucune menace.

Etapes:

1. Lancez EDMC.

2. Cliquez sur Fichier, puis sur Paramètres.

3. Cliquez sur l'onglet Plugins, puis cliquez sur Ouvrir.

4. Allez dans le sous-dossier `EDR`, puis dans le dossier `EDMCOverlay`.

5. Faites un clic droit sur le fichier `edmcoverlay.exe`, sélectionnez votre option d'analyse antivirus.

    <img alt="Scan the overlay.exe file in the EDR/EDMCOverlay folder" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_33.png?raw=true">

6. Si votre antivirus ne se plaint pas, double-cliquez sur le fichier `edmcoverlay.exe` et laissez-le s'exécuter si votre antivirus vous demande une confirmation.

## Votre Framerate a pris un coup

Avant d'essayer l'une des options ci-dessous, assurez-vous que vos pilotes graphiques sont à jour, puis confirmez que le problème existe toujours.

### Option 1: désactiver Vsync

1. Accédez aux options en jeu d'Elite:

    <img alt="Panel to open the game Settings" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_34.png?raw=true">

2. Sélectionnez les options graphiques:

    <img alt="Panel to open the game's graphic settings" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_35.png?raw=true">

3. Trouvez Vertical sync, sous la section Affichage, et désactivez-le:

    <img alt="Panel to open the game's graphic settings to deactivate Vertical sync in the Display section" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_36.png?raw=true">

4. Retester l'EDR

### Option 2: essayez sans bordure / fenêtré / plein écran

1. Accédez aux options en jeu d'Elite
2. Sélectionnez les options graphiques
3. Dans la section Affichage, essayez les différents modes, par ex. Borderless / Windowed / Fullscreen, et voyez s'il y en a un qui fonctionne mieux.

### Option 3: essayez l'interface utilisateur alternative d'EDR

1. Sur le bord droit du statut EDR, cochez la case pour révéler l'interface utilisateur alternative d'EDR:

    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_37_Black.png?raw=true">
      <source media="(prefers-color-scheme: light)" srcset="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_37_White.png?raw=true">
      <img alt="Interface to activate alternative/extended view of EDR in EDMC application" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_37_White.png?raw=true" height="450">
    </picture>

2. Les informations qui auraient été affichées via la superposition seront affichées dans cette zone

3. Allez dans les paramètres d'EDMC depuis le menu Fichier, puis l'onglet EDR

4. Désactiver la superposition

5. Facultatif: si vous souhaitez superposer EDMC
   1. Allez dans l'onglet Apparence, sélectionnez Toujours visible.
   2. Activez le thème transparent si vous le souhaitez
   3. Accédez aux options graphiques d'Elite et sélectionnez sans bordure ou fenêtré.

## D'autres problèmes, non résolus?

N'hésitez pas à rejoindre [EDR central](https://edrecon.com/discord), le serveur communautaire pour EDR avec accès au bot, aux alertes en temps réel et à l'assistance au dépannage. Vous pouvez également partager votre fichier journal EDMC avec LeKeno sur Discord, voir ci-dessous pour les instructions.

Etapes:

1. Appuyez simultanément sur votre touche Windows et la touche R.

    <img alt="Run interface to go to Temp folder" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_38.png?raw=true">

2. Saisissez `%tmp%` (ou `%temp%`) et appuyez sur la touche Entrée.

3. Trouvez le fichier nommé `EDMarketConnector.log`

    <img alt="TEMP folder where the EDMC log files are present" src="https://github.com/lekeno/edr/blob/master/edr/docs/assets/IMG_39.png?raw=true">

4. Passez en revue et modifiez son contenu avec le bloc-notes (un double-clic devrait l'ouvrir avec le bloc-notes) si nécessaire.

5. Partagez-le avec LeKeno sur Discord.

## Considérations relatives à la confidentialité

Si vous êtes curieux de savoir comment EDR fonctionne et ce qu'il fait, vous pouvez vérifier le [code source](https://github.com/lekeno/edr/), et puisqu'il est écrit en Python, vous pouvez également examiner le code en cours d'exécution et confirmer qu'il est identique au code source publié sur GitHub. Frontier a également [examiné et félicité EDR](https://forums.frontier.co.uk/threads/flying-in-open-last-night-edr-saved-my-life-it-could-save-yours-too.388696/page-15#post-6118053), confirmant que son utilisation de l'API Player Journal est conforme à leurs règles et conditions de service.

La première fois que vous lancez EDMC en jouant au jeu, vous serez redirigé vers le [site Web d'authentification de Frontier](https://auth.frontierstore.net/) et vous serez invité à entrer votre nom d'utilisateur et votre mot de passe Elite: Dangerous. Cela **n'a rien à voir avec l'EDR** et **peut être carrément ignoré**. EDR n'utilise PAS l'API d'authentification de Frontier. EDR utilise [l'API Player Journal](https://forums.frontier.co.uk/threads/commanders-log-manual-and-data-sample.275151/) de Frontier qui ne contient que des informations sur ce qui se passe dans le jeu et ne contient AUCUNE information personnelle.

Cela dit, voici pourquoi vous voudrez peut-être toujours autoriser EDMC sans vous en soucier:

- L'objectif principal d'EDMC est, comme son nom l'indique “Market Connector”, de partager les informations sur le marché du jeu dans une [base de données centrale](https://github.com/EDSM-NET/EDDN/wiki) pour le bénéfice de tous. Pour ce faire, il accède aux données du marché des stations auxquelles vous êtes amarré via l'API d'authentification de Frontier. C'est ainsi que plusieurs outils sont capables de vous dire quels systèmes/stations achètent des diamants à basse température à un prix élevé, trouver des routes commerciales lucratives, ou même quelles stations ont certains modules ou vaisseaux disponibles.
- Certaines personnes non informées (ou pire) répandent des rumeurs non fondées selon lesquelles cette API donne accès à vos informations de facturation… Maintenant, pensez à ce que cela signifierait: une société cotée en bourse exposant des informations commerciales sensibles à des développeurs tiers?! Cela n'a absolument aucun sens. L'API n'expose pas ce genre d’informations.
- Reportez-vous à [la politique de confidentialité d'EDMC](https://github.com/Marginal/EDMarketConnector/wiki/Privacy-Policy) pour comprendre comment EDMC traite vos données.
