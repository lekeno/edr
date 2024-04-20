<div align="center">
  <img Alt="Logo_ED_Recon" src="https://edrecon.com/img/icon-192x192.8422df55.png">
  <h1><a href="https://edrecon.com"><b>ED Recon</b></a>
  <br>
  Il Manuale Mancante</h1>
</div>
<p align=right>
  Stesura a cura del <b>CMDR Lekeno</b><br>
  Traduzione a cura del <b>CMDR FrostBit</b><br>
  Versione 2.7.7.0
</p>

<h1>Sommario</h1>

- [Installazione](#installazione)
  - [Pre-requisiti](#pre-requisiti)
  - [Elite Dangerous Market Connector](#elite-dangerous-market-connector)
  - [ED Recon (aka EDR)](#ed-recon-aka-edr)
  - [Account EDR](#account-edr)
- [EDR in breve](#edr-in-breve)
  - [Output](#output)
  - [Aiuto e Suggerimenti](#aiuto-e-suggerimenti)
- [Funzionalità Dedicate ai Commander](#funzionalità-dedicate-ai-commander)
  - [Profilazione Automatica dei Comandanti](#profilazione-automatica-dei-comandanti)
  - [Profilazione Manuale dei Comandanti](#profilazione-manuale-dei-comandanti)
  - [Annotazioni su altri comandanti](#annotazioni-su-altri-comandanti)
    - [Comandi generici](#comandi-generici)
    - [Tags di allineamento](#tags-di-allineamento)
    - [Memo](#memo)
  - [Come leggere le informazioni del profilo](#come-leggere-le-informazioni-del-profilo)
- [EDR Karma](#edr-karma)
  - [Che cos'è il Karma in EDR?](#che-cosè-il-karma-in-edr)
  - [Come viene calcolato?](#come-viene-calcolato)
    - [Dettagli extra](#dettagli-extra)
- [Funzionalità Dedicate al System](#funzionalità-dedicate-al-system)
  - [Sitreps](#sitreps)
  - [Distanza](#distanza)
  - [Segnali conosciuti](#segnali-conosciuti)
  - [Informazioni sulla tua destinazione](#informazioni-sulla-tua-destinazione)
  - [Sistema attuale](#sistema-attuale)
- [Funzionalità Dedicate al Planet](#funzionalità-dedicate-al-planet)
  - [Punto di Interesse (PoI)](#punto-di-interesse-poi)
  - [Navigazione](#navigazione)
  - [Materiali interessanti](#materiali-interessanti)
- [Trovare Servizi](#trovare-servizi)
- [Funzionalità Dedicate ai Materials](#funzionalità-dedicate-ai-materials)
  - [Materiali dipendenti dallo stato del BGS](#materiali-dipendenti-dallo-stato-del-bgs)
  - [Ricerca di materiali specifici](#ricerca-di-materiali-specifici)
  - [Materiali Raw](#materiali-raw)
    - [Profili](#profili)
      - [_Profili dei materiali personalizzati_](#profili-dei-materiali-personalizzati)
  - [Materiali Odyssey](#materiali-odyssey)
    - [Valutazione](#valutazione)
    - [Bar delle Fleet Carrier](#bar-delle-fleet-carrier)
- [Funzionalità Dedicate alla Ship](#funzionalità-dedicate-alla-ship)
  - [Dove ho parcheggiato la mia nave?](#dove-ho-parcheggiato-la-mia-nave)
  - [Proprietà del Sistema di Alimentazione](#proprietà-del-sistema-di-alimentazione)
  - [Trovare un parcheggio per la tua Fleet Carrier](#trovare-un-parcheggio-per-la-tua-fleet-carrier)
  - [Atterraggio](#atterraggio)
- [Funzionalità Dedicate allo Squadron](#funzionalità-dedicate-allo-squadron)
  - [Nemici e alleati dello squadrone](#nemici-e-alleati-dello-squadrone)
    - [Tag](#tag)
- [Funzionalità Dedicate al Bounty Hunting](#funzionalità-dedicate-al-bounty-hunting)
  - [Avvisi in tempo reale](#avvisi-in-tempo-reale)
  - [Statistiche e Grafici della Caccia alle Taglie](#statistiche-e-grafici-della-caccia-alle-taglie)
- [Funzionalità Dedicate al Powerplay](#funzionalità-dedicate-al-powerplay)
  - [Caccia in powerplay](#caccia-in-powerplay)
- [Funzionalità Dedicate al Mining](#funzionalità-dedicate-al-mining)
- [Funzionalità Dedicate all'Exobiology](#funzionalità-dedicate-allexobiology)
  - [Informazioni sul bioma](#informazioni-sul-bioma)
    - [Info sul sistema](#info-sul-sistema)
    - [Info specifiche sul pianeta](#info-specifiche-sul-pianeta)
  - [Navigazione e monitoraggio dei progressi](#navigazione-e-monitoraggio-dei-progressi)
  - [Alla ricerca di un pianeta buono per l'esobiologia](#alla-ricerca-di-un-pianeta-buono-per-lesobiologia)
- [HUD rotta](#hud-rotta)
- [Spansh companion](#spansh-companion)
- [Insediamenti Odyssey](#insediamenti-odyssey)
- [Integrazione Discord](#integrazione-discord)
  - [Inoltro dei messaggi della chat di gioco](#inoltro-dei-messaggi-della-chat-di-gioco)
    - [Pre-requisiti](#pre-requisiti-1)
    - [Configurazione dei canali Discord (webhook)](#configurazione-dei-canali-discord-webhook)
    - [Funzionalità](#funzionalità)
      - [_Messaggi in arrivo_](#messaggi-in-arrivo)
      - [_Messaggi in uscita_](#messaggi-in-uscita)
      - [_Opzioni di personalizzazione_](#opzioni-di-personalizzazione)
  - [Invio del piano di volo della propria Fleet Carrier a Discord](#invio-del-piano-di-volo-della-propria-fleet-carrier-a-discord)
  - [Invio degli ordini di acquisto/vendita di materie prime e materiali Odyssey da parte della vostra Fleet Carrier](#invio-degli-ordini-di-acquistovendita-di-materie-prime-e-materiali-odyssey-da-parte-della-vostra-fleet-carrier)
- [Overlay](#overlay)
  - [Impostazioni multi monitor e VR](#impostazioni-multi-monitor-e-vr)
    - [Posizionamento VR con SteamVR](#posizionamento-vr-con-steamvr)
  - [Personalizza overlay](#personalizza-overlay)
- [Segnalazione dei reati](#segnalazione-dei-reati)
- [Effetti audio](#effetti-audio)
  - [Comandi e opzioni](#comandi-e-opzioni)
  - [Personalizzazione](#personalizzazione)
    - [_Tipo di eventi_](#tipo-di-eventi)
- [Appendice](#appendice)
  - [Risoluzione dei problemi](#risoluzione-dei-problemi)
    - [Non viene visualizzato nulla / L'overlay non funziona](#non-viene-visualizzato-nulla--loverlay-non-funziona)
      - [_Controllare le impostazioni_](#controllare-le-impostazioni)
      - [_Consentire l'esecuzione dell'overlay_](#consentire-lesecuzione-delloverlay)
  - [La frequenza dei fotogrammi è diminuita in modo significativo](#la-frequenza-dei-fotogrammi-è-diminuita-in-modo-significativo)
    - [Opzione 1: disattivare Vsync](#opzione-1-disattivare-vsync)
    - [Opzione 2: prova borderless / windowed / fullscreen](#opzione-2-prova-borderless--windowed--fullscreen)
    - [Opzione 3: provare l'interfaccia utente alternativa di EDR](#opzione-3-provare-linterfaccia-utente-alternativa-di-edr)
  - [Altri problemi non risolti?](#altri-problemi-non-risolti)
  - [Informazioni sulla privacy](#informazioni-sulla-privacy)

<br><br><br>

# Installazione

Se rimani bloccato o hai domande, non esitare a unirti a [EDR central](https://discord.gg/meZFZPj), il server della community per EDR con accesso al bot, avvisi in tempo reale e supporto per la risoluzione dei problemi.

## Pre-requisiti

- Windows
- Elite: Dangerous (LIVE)
- Elite Dangerous Market Connector (Vedi la [sezione sottostante](#elite-pericoloso-market-connector))
- Leggere e comprendere [l'informativa sulla privacy](https://edrecon.com/privacy-policy) e i [termini di servizio](https://edrecon.com/tos) di EDR. **Procedere ulteriormente implica comprendere e accettare l'informativa sulla privacy e i termini di servizio.**

## Elite Dangerous Market Connector

**Se hai già installato Elite Dangerous Market Connector (EDMC), [passa alla sezione successiva](#ed-recon-aka-edr).**

ED Recon è offerto come plug-in per Elite Dangerous Market Connector, un ottimo strumento di terze parti per Elite: Dangerous. Controlla le [istruzioni ufficiali](https://github.com/EDCD/EDMarketConnector/wiki/Installation-&-Setup) se le spiegazioni seguenti non sono sufficienti.

Passaggi:

1. Leggi [l'informativa sulla privacy di EDMC](https://github.com/EDCD/EDMarketConnector/wiki/Privacy-Policy). Se non sei d'accordo con qualcosa o non capisci tutto, NON procedere oltre.
2. [Scarica l'ultima versione di EDMC](https://github.com/EDCD/EDMarketConnector/releases/latest) (il file .exe)
3. Fare doppio clic sul file scaricato per installarlo.
   - Windows potrebbe darti un avviso sul file. Clicca su `maggiori informazioni` poi su `Esegui comunque`. Se sei preoccupato, sentiti libero di eseguire prima una scansione antivirus sul file scaricato.
4. Esegui Elite Dangerous Market Connector dal menu Start o dalla schermata Start.
5. Configura la visualizzazione EDMC in italiano dalle preferenze, se necessario:
   - Menu `File`, `Impostazioni`, scheda `Aspetto`, selettore di Lingua, Italiano.
6. Facoltativo: consenti a EDMC di accedere all'API di Frontier per tuo conto (**EDR NON utilizza l'API di Frontier, quindi sentiti libero di ignorare questa richiesta di autenticazione**).

## ED Recon (aka EDR)

Passaggi:

1. [Scarica l'ultima versione di EDR](https://github.com/lekeno/EDR/releases/latest) (il file EDR.v#.#.#.zip dove #.#.# è il numero di versione, es. 1.0.0 nello screenshot seguente)

    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/GLWine/edr/blob/master/edr/docs/assets/EDR_1.0.0_Black.png?raw=true">
      <source media="(prefers-color-scheme: light)" srcset="https://github.com/GLWine/edr/blob/master/edr/docs/assets/EDR_1.0.0_White.png?raw=true">
      <img alt="Screenshot of the release page of EDR 1.0.0" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/EDR_1.0.0_White.png?raw=true">
    </picture>

2. Avvia EDMC.

3. Fare clic su File, poi su Impostazioni.

    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_01-02_Black.png?raw=true">
      <source media="(prefers-color-scheme: light)" srcset="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_01-02_White.png?raw=true">
      <img alt="How to open EDMC settings" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_01-02_White.png?raw=true">
    </picture>

4. Clicca sulla scheda Plugin, quindi fare clic su Sfoglia.

    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_03-04_Black.png?raw=true">
      <source media="(prefers-color-scheme: light)" srcset="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_03-04_White.png?raw=true">
      <img alt="How to go to the plugin tab" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_03-04_White.png?raw=true">
    </picture>

5. Crea una sotto cartella denominata `EDR` nella cartella dei `plugins`.

    <img alt="How to access the tab and then the plugins folder" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_05_White.png?raw=true">

6. Estrai il contenuto del file Zip scaricato al passaggio 2 in questa sotto cartella EDR.

    <img alt="EDR folder creation" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_06_White.png?raw=true">

7. Riavviare EDMC.

8. Dovresti vedere una riga di stato EDR (es. `EDR: autenticato (guest)`) nella parte inferiore di EDMC:

    <img alt="Location and folder structure of EDR" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_07_White.png?raw=true">

9. Avvia Elite, avvia una nuova sessione.

10. Dovresti vedere un messaggio introduttivo (es. `EDR V0.9.5 […]`) sovrapposto a Elite.
    - Su Windows 10: l'overlay dovrebbe funzionare per tutte le modalità (Fullscreen, Borderless, Windowed).
    - Su Windows 7: l'overlay NON funziona in Fullscreen, utilizza invece il Borderless o il Windowed.
    - Se l'overlay non funziona, consultare la sezione sulla [risoluzione dei problemi](#risoluzione-dei-problemi).

## Account EDR

EDR funziona subito senza alcun account. Tuttavia, se desideri fornire informazioni a EDR e ai suoi utenti, ad es. inviando avvistamenti di fuorilegge, dovrai [richiedere un account](https://edrecon.com/account).

Osservazioni importanti:

- Le domande vengono valutate manualmente per garantire un servizio di alta qualità. Questo potrebbe richiedere alcune settimane.
- Se hai chiesto di essere contattato su Discord: controlla un'eventuale richiesta di amicizia da `LeKeno`.
- Se hai richiesto di essere contattato via email: assicurati che l'email da edrecon.com non sia finita nella tua cartella spam.

Dopo aver ottenuto le credenziali, apri le impostazioni EDR (`File` menu, `Impostazioni`, scheda `EDR`) compila di conseguenza i campi e-mail e password e fai clic su OK.

<img alt="Where to write email and password in EDMC settings for EDR" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_08_White.png?raw=true">

Se tutto procede secondo i piani, dovresti vedere "autenticato" nella riga di stato EDR.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_09_Black.png?raw=true">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_09_White.png?raw=true">
  <img alt="Location where it is indicated whether the login was successful" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_09_White.png?raw=true">
</picture>

# EDR in breve

L'EDR offre una vasta gamma di funzionalità progettate per facilitare e migliorare la tua esperienza in Elite Dangerous: profili dei giocatori basati su segnalazioni in gioco, ricerca di materiali rari, valutazione del valore dei materiali di Odyssey, ecc.

- Profilo dei giocatori basato sui rapporti in gioco
- Ricerca di materiali rari
- Valutazione del valore dei materiali di Odyssey, ecc.

Queste funzionalità si attivano automaticamente in base a ciò che accade nel gioco, oppure possono essere attivate inviando comandi EDR (es. `!who lekeno`) tramite la chat in gioco (qualsiasi canale), o tramite il campo di input EDR nella finestra di EDMC:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_10_Black.png?raw=true">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_10_White.png?raw=true">
  <img alt="Alterative position from where to send EDR commands in EDMC" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_10_White.png?raw=true">
</picture>

### Output

L'EDR mostra varie informazioni utili tramite un overlay grafico e un'interfaccia utente testuale nella finestra di EDMC.

- L'overlay può anche essere configurato come una finestra indipendente per monitor multipli o VR setups (nel menu `File`, seleziona `Impostazioni`, quindi vai alla scheda `EDR`, e imposta `Overlay` su `standalone`).
- L'interfaccia utente testuale può essere espansa o compressa con la casella di controllo sul lato destro della riga di stato EDR in EDMC.

### Aiuto e Suggerimenti

Quando si avvia una nuova sessione di gioco, EDR mostrerà un suggerimento casuale riguardante il gioco o EDR stesso.

- Inviando `!help` otterrai una guida breve e chiara sui vari comandi EDR.
- Puoi anche richiedere un suggerimento casuale inviando il comando `!tip`, oppure `!tip edr` per suggerimenti su EDR, e `!tip open` per suggerimenti sul giocare in modalità Open.

# Funzionalità Dedicate ai Commander

## Profilazione Automatica dei Comandanti

Se EDR rileva la presenza di un comandante potenzialmente pericoloso (es. un fuorilegge), mostrerà automaticamente il profilo di quel comandante.
Esempi:

- Quando si riceve un messaggio (direct, local, system, ecc.) da un fuorilegge.
- Essere interdetti da un fuorilegge.
- Unirsi / formare un team con un fuorilegge.
- Avere un fuorilegge che si unisce a una sessione multicrew.

## Profilazione Manuale dei Comandanti

Traghettare un altro giocatore svelerà il loro profilo EDR. Per gli utenti con un account, completare una scansione comporterà l'invio delle informazioni al server EDR a beneficio degli altri utenti EDR. In alternativa, puoi attivare una ricerca del profilo del comandante EDR + Inara tramite:

- Invio di **`o7`** al cmdr che ti interessa (come direct message).
- Inviando **<tt>!who _nome_cmdr_</tt>** o **<tt>!w _nome_cmdr_</tt>** tramite la chat in gioco (qualsiasi canale: locale, squadrone, team, sistema, ecc.), oppure tramite il campo di input EDR nella finestra di EDMC. Esempio: **`!w lekeno`**

EDR mostrerà anche informazioni chiave (HP, dimensione/classe, tendenze) sulla nave/veicolo del tuo bersaglio e sul sottomodulo selezionato, se presente:

<img alt="Interface integrity and hull and shield of the opponent" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_11.png?raw=true">

## Annotazioni su altri comandanti

Puoi creare il tuo indice personalizzato dei comandanti (CmdrDex) per personalizzare la tua esperienza con EDR e aiutare gli altri utenti di EDR a fare supposizioni fondate sulle intenzioni degli altri comandanti. Il tuo CmdrDex è personale; EDR mostrerà solo statistiche aggregate per le etichette di allineamento, es. 79% fuorilegge, 25% neutrale, 5% enforcer (abbreviato come [!70% ?25%? +5%] in-game).

### Comandi generici

- `#=` o `#friend` per contrassegnare un contatto come amico.
- <tt>#= _nome_cmdr_</tt> o <tt>#friend _nome_cmdr_</tt> per contrassegnare un comandante specifico come amico.
- `-#=` o <tt>-#friend _nome_cmdr_</tt> per rimuovere un'etichetta di amico da un contatto o da un comandante specifico nel tuo indice comandante.
- `#tag` o <tt>#tag _nome_cmdr_</tt> per contrassegnare un contatto o _nome_cmdr_ con un'etichetta personalizzata nel tuo indice comandante (es. `#pirata jack sparrow`).
- `-#` o <tt>-# _nome_cmdr_</tt> per rimuovere l'etichetta (untag) da un contatto o _nome_cmdr_ dal tuo indice comandante. (es. `-# jack sparrow`).
- `-#tag` o <tt>-#tag _nome_cmdr_</tt> per rimuovere un'etichetta specifica da un contatto o _nome_cmdr_ nel tuo indice comandante, (es. `-#pirata jack sparrow`).

### Tags di allineamento

Puoi contrassegnare un comandante con un tag di allineamento e aiutare gli altri utenti di EDR a fare supposizioni fondate su altri giocatori.

- Taggali Outlaw se li vedi attaccare un comandante innocente e che non fa parte di un power ostile.
- Taggali Enforcer se li hai visti continuamente prendere di mira fuorilegge.
- Taggali neutral se non sei d'accordo con la classificazione di EDR e desideri sopprimere il suo avvertimento, oppure se un comandante sembra semplicemente occuparsi dei propri affari.

Comandi:

- `#outlaw` o `#!` per taggare un contatto con un'etichetta di fuorilegge.
- <tt>#outlaw _name_cmdr_</tt> o <tt>#! _name_cmdr_</tt> per etichettare un comandante specifico con un'etichetta di fuorilegge (es. `#! Vicious RDCS`).
- `#neutral` o `#?` per etichettare un contatto con un tag neutrale.
- <tt>#neutral _name_cmdr_</tt> o <tt>#? _name_cmdr_</tt> per etichettare un comandante specifico con un'etichetta neutrale (es. `#? filthy neutral jr`).
- `#enforcer` o `#+` per etichettare un contatto con un'etichetta di enforcer.
- <tt>#enforcer _name_cmdr_</tt> o <tt>#+ _name_cmdr_</tt> per etichettare un comandante specifico con un'etichetta di enforcer (es. `#+ lekeno`).
- <tt>-#_tag_allin._</tt> o <tt>-#_tag_allin. name_cmdr_</tt> per rimuovere l'_tag_allineamento_ da un contatto o comandante specifico nel tuo indice comandante (es. `-#+ lekeno`).

### Memo

Puoi allegare un memo (breve promemoria) a un comandante. Questo può essere utile per ricordare come li hai incontrati o chi sono.

Comandi:

- `@# “qualcosa di molto importante da ricordare”` per allegare una nota personalizzata a un contatto.
- <tt>@# _name_cmdr_ memo=“distant worlds 2”</tt> per allegare una nota personalizzata a un comandante specifico.
- `-@#` o <tt>-@# _nome_cmdr_</tt> per rimuovere la nota personalizzata da un contatto o un comandante specifico.

## Come leggere le informazioni del profilo

Il profilo include alcuni grafici che mostrano dati storici per 12 mesi. Il mese corrente si trova sul bordo destro, e l'asse retrocede nel tempo da lì (cioè il mese precedente è la barra sul lato sinistro dell'ultima barra a destra).

La sezione superiore contiene una vista combinata (stessa scala) di scansioni pulite e ricercate:

- [In alto] Numero di scansioni pulite in tonalità di verde: più alta è la barra / più verde è la barra, più scansioni pulite sono state segnalate.
- [In basso] Numero di scansioni ricercate: più bassa è la barra / più rossa è la barra, più scansioni ricercate sono state segnalate.

La sezione inferiore mostra la taglia più alta segnalata del comandante per ogni mese. L'altezza della barra è relativa ad altre taglie segnalate (la barra più alta corrisponde alla taglia massima assoluta, la barra a metà altezza corrisponde al 50% della taglia massima assoluta). La quantità della taglia è rappresentata dal colore della barra: più caldo è il colore, più elevato è l'importo della taglia.

<img alt="Framing interface of a graphical box commander" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_12.png?raw=true">

Il profilo testuale include informazioni da EDR e [Inara](https://inara.cz/).

Le sezioni di EDR forniscono vari segnali per aiutarti a formulare un'opinione fondata su altri comandanti. In definitiva, resta la tua interpretazione e opinione. **Quindi, usa sempre il tuo buon senso e assumiti piena responsabilità per il tuo comportamento e le tue azioni.**

- **Karma EDR:** un valore compreso tra -1000 e 1000 calcolato in base alla storia di scansioni e taglie di un comandante, come riportato da altri utenti EDR. Per comodità, il valore del karma viene tradotto in tre etichette (Outlaw, Ambiguous +/-, Lawful) con i simboli + per indicare il livello all'interno di una categoria. Outlaw indica che questo comandante è stato scansionato con una taglia considerevole, Ambiguous indica una mancanza di dati o entrambi i segnali positivi/negativi, Lawful indica una striscia di scansioni pulite. Vedere [EDR karma](#edr-karma) per maggiori dettagli.
- Tag karma:\*\* gli utenti EDR possono etichettare altri comandanti con tag predefiniti (o personalizzati). Questa sezione mostra un numero (o percentuale) di tag per le seguenti categorie predefinite:
  - outlaw (rappresentato come !)
  - neutral (?)
  - enforcer (rappresentato come +)
  - Se vedete un comandante con tag utente fuorvianti, fatelo sapere a _Cmdr lekeno_.
- **Riassunto dei 90 giorni:** riepilogo delle scansioni e delle taglie come riportato dagli utenti EDR. Include il numero di scansioni pulite, il numero di scansioni come ricercato e la taglia più alta segnalata.
- **Varie:** EDR mostrerà anche altri tipi di informazioni, se pertinenti (es. i tag personalizzati, se presenti).

La sezione Inara mostra informazioni come il ruolo, lo squadrone, la fedeltà, ecc.

<img alt="Framing interface of a commander" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_13.png?raw=true">

# EDR Karma

## Che cos'è il Karma in EDR?

È un valore compreso tra -1000 e 1000 che ha lo scopo di fornire un indicatore (**hint**) di quanto un comandante sia stato rispettoso o meno della legge. Questo è solo un suggerimento per influenzare la tua opinione, in combinazione con altri suggerimenti o segnali nel gioco (es. l'aver visto inseguire comandanti onesti, pilotare un FdL meta ricercato in una CG mineraria, ecc.). **Quindi, usate sempre il vostro buon senso e assumetevi la piena responsabilità del vostro comportamento e delle vostre azioni.**

## Come viene calcolato?

Il karma dell'EDR è attualmente calcolato sulla base del valore delle scansioni e delle taglie segnalate da altri utenti dell'EDR (cioè il proprio stato legale o le proprie taglie non sono presi in considerazione; qualcun altro deve segnalare il vostro stato legale o la vostra taglia per essere preso in considerazione).

Con un livello elevato:

- se un comandante viene segnalato come onesto, il suo valore di karma aumenterà.
- se un comandante viene segnalato come ricercato, il suo valore di karma diminuirà.
- se un comandante viene segnalato con una taglia, il suo valore di karma può diminuire ulteriormente.
- se un comandante viene scansionato ma non è stato visto per un po' di tempo, prima di riflettere le nuove informazioni della scansione, vedrà il suo karma diminuire:
  - ottenere il beneficio del dubbio con un aumento di karma verso l'Ambiguo se avevano un karma da Fuorilegge.
  - ottengono un adeguamento graduale con una diminuzione del karma verso Ambiguo se avevano un karma Legale.

### Dettagli extra

La quantità di aumento/diminuzione del karma dalla scansione onesto/ricercato non è uniforme:

- La quantità è minore ai bordi della scala del karma. In altre parole, è più difficile ottenere il quarto +, che il terzo +, e così via. In questo modo si intende attribuire a ciascun + un peso molto maggiore di quello che sarebbe possibile con una scala lineare.

Un report della taglia può far scendere ulteriormente il karma, a seconda dell'importo:

- Il karma è suddiviso in gradi (ovvero il numero di +)
- Ogni grado (compreso il karma legale) ha una soglia di taglia associata.

Se un comandante viene scansionato con una taglia che supera questa soglia, verrà riassegnato a una fascia di karma più appropriata (es. Outlaw+++ invece di Outlaw++). Questo vale anche per i comandanti con un karma legittimo, per prevenire episodi di trolling, ma anche per evitare che comandanti legali++++ abusino del loro karma per scatenarsi.

Per i comandanti che sono stati scansionati dopo essere stati sotto osservazione per un po' di tempo, l'EDR farà decadere il loro Karma di una quantità che dipende dal tempo trascorso dalla precedente scansione (cioè, più a lungo sono rimasti in silenzio, maggiore sarà il decadimento).

Ci sono altre sfumature, come le soglie di tempo tra le scansioni e i rapporti sulle taglie, o gli aspetti di caching sul lato client che possono influenzare il calcolo o il riflettersi dell'ultimo valore del karma.

# Funzionalità Dedicate al System

## Sitreps

All'avvio di una nuova sessione o dopo il passaggio a un nuovo sistema, EDR mostra un rapporto sulla situazione (alias sitrep).

Le informazioni possono includere:

- NOTAM: un breve promemoria sul sistema (es. Community Goal, PvP Hub, Hot spot conosciuti, ecc.)
- Un elenco di fuorilegge e cmdr avvistati di recente
- Un elenco di comandanti che hanno recentemente interdetto o ucciso altri comandanti (senza alcun giudizio sulla legalità di tali azioni)

Comandi:

- `!sitreps` per visualizzare un elenco di sistemi stellari con attività recente (buoni candidati per un comando `!sitrep`).
- `!sitrep` per visualizzare il report della situazione corrente nel sistema.
- <tt>!sitrep _nome_sistema_</tt> per visualizzare il sitrep di un determinato sistema stellare (es. `!sitrep deciat`).
- `!notams` per visualizzare un elenco di sistemi stellari con NOTAM attivi.
- <tt>!notam _nome_sistema_</tt> per visualizzare il NOTAM di un dato sistema stellare (es. `!notam san tu`).

## Distanza

L'EDR può calcolare le distanze tra la propria posizione e un altro sistema, o tra due sistemi arbitrari, purché siano già noti alla community.

Comandi:

- <tt>!distance _nome_sistema_</tt> mostra la distanza tra la propria posizione e _nome_sistema_ (es. `!distance deciat`)
- <tt>!distance _origine_ > _destinazione_</tt> mostra la distanza tra l'_origine_ e la _destinazione_ (es. `!distance deciat > borann`)

## Segnali conosciuti

EDR può mostrare una panoramica dei segnali conosciuti per il sistema corrente (es. siti di estrazione delle risorse, zone di combattimento, fleet carrier, stazioni, ecc.)

- La panoramica viene visualizzata automaticamente quando si guarda la mappa del sistema.
- L'invio del comando `!signals` attiverà manualmente la panoramica

## Informazioni sulla tua destinazione

**Solo per Odissey:** EDR mostrerà le informazioni chiave sulla prossima destinazione (stazione, fleet carrier, sistema). Per le stazioni o le fleet carriers, EDR mostrerà l'elenco dei servizi disponibili, nonché le informazioni sulla fazione che le controlla (stato BGS, governo, fedeltà e se la fazione è una **P**layer **M**inor **F**action).

## Sistema attuale

EDR mostrerà il valore di esplorazione stimato e le informazioni chiave per le stelle, i pianeti e i sistemi. Questa funzione si attiva quando usi: Discovery Scanner honk, Full Spectrum Scan, e Detailed Surface Scan.

# Funzionalità Dedicate al Planet

## Punto di Interesse (PoI)

EDR dispone di un elenco di punti d'interesse (es. navi precipitate, basi abbandonate, ecc.). La guida verrà mostrata automaticamente quando si entra in un sistema che presenta dei PoI, così come quando ci si avvicina a un corpo che presenta dei PoI. Include una funzione di navigazione (rotta, distanza, altitudine, passo) per aiutarvi ad atterrare vicino a un PoI.

## Navigazione

È supportata anche la navigazione manuale (visualizzata quando ci si avvicina a un corpo o quando ci si trova sulla superficie di un corpo).

Comandi:

- `!nav 123.21 -32.21` per impostare la destinazione in base alla sua latitudine e longitudine.
- `!nav off` per disabilitare la funzione di navigazione
- `!nav set` per impostare l'latitudine e la longitudine correnti come punto di riferimento per la funzione di navigazione.

## Materiali interessanti

Quando si avvicina a un corpo, EDR mostrerà un elenco di materiali degni di nota (cioè materiali con una densità superiore a quella tipica attraverso la galassia). Nota: ciò richiede un'azioni preliminari come la scansione del navigation beacon o l'analisi del sistema con il Full Spectrum Scanner, ecc.

Per saperne di più, vedi [Funzionalità Dedicate ai Materials](#funzionalità-dedicate-ai-materials).

# Trovare Servizi

EDR può aiutarti a trovare i servizi più vicini a te o a un sistema specifico.

Comandi:

- `!if` o `!if Lave` per trovare un Interstellar Factors vicino alla vostra posizione o al sistema Lave.
- `!raw` o `!raw` Lave per trovare un Raw Material Trader vicino alla propria posizione o al sistema Lave.
- `!encoded`, `!enc` o `!enc Lave` per trovare un Encoded Data Trader vicino alla propria posizione o al sistema Lave.
- `!manufactured`, `!man` o `!man Lave` per trovare un Manufactured Material Trader vicino alla propria posizione o al sistema Lave.
- `!staging` o `!staging Lave` per trovare una buona stazione di staging vicino alla propria posizione o al sistema Lave, es. pad grandi, shipyard, outfitting, riparazione/riarmo/rifornimento.
- `!htb`, `!humantechbroker` o `!htb Lave` per trovare uno Human Tech Broker vicino alla propria posizione o al sistema Lave.
- `!gtb`, `!guardiantechbroker` o `!gtb Lave` per trovare un Guardian Tech Broker vicino alla propria posizione o al sistema Lave.
- `!offbeat`, `!offbeat Lave` per trovare una stazione che non è stata visitata di recente vicino alla propria posizione o al sistema Lave (utile per trovare tute spaziali e armi pre-ingegnerizzate/pre-aggiornate in Odyssey).
- `!rrr`, `!rrr Lave`, `!rrr Lave < 10` per trovare una stazione con funzioni di riparazione, riarmo e rifornimento vicino alla propria posizione, o al sistema Lave, o entro un raggio di 10 LY da Lave.
- `!rrrfc`, `!rrrfc Lave`, `!rrrfc Lave < 10` per trovare una fleet carrier con funzioni di riparazione, riarmo e rifornimento vicino alla propria posizione, o al sistema Lave, o entro un raggio di 10 LY da Lave. Prima di andare lì, controllate l'accesso al docking!
- `!fc J6B`, `!fc recon`, `!station Jameson` per visualizzare informazioni sui servizi presso la Fleet Carrier locale o le Stazioni con un callsign/nome contenente rispettivamente J6B, Recon, Jameson.

# Funzionalità Dedicate ai Materials

## Materiali dipendenti dallo stato del BGS

Quando si arriva in un nuovo sistema, EDR a volte mostra un elenco di materiali con una probabilità stimata (per lo più da un signal sources). Se le scorte attuali sono scarse di un particolare materiale e la disponibilità è relativamente alta, si può cercare un (HGES) High Grade Emission source e farmarlo fino a riempirsi (dopo aver raccolto i materiali, uscire dal gioco, rilanciarlo, andare in supercruise a velocità 0, saltare di nuovo nel segnale, ripetere fino allo scadere del timer).

## Ricerca di materiali specifici

Inviando <tt>!search _risorsa_</tt> per trovare un buon punto di farming di una risorsa specifica (es. `!search selenium`). È possibile utilizzare il nome completo della risorsa o un'abbreviazione. Sono supportate le risorse molto rare, rare e standard (data, raw, manufactured). Eccetto: le risorse relative alle guardian technology. Suggerimento: il nome del sistema verrà copiato negli appunti.

Abbreviazioni:

- Le prime 3 lettere di una risorsa composta da una sola parola, es. `!search cad` per il cadmium,
- Le iniziali di ogni parola, separate da spazi per le risorse composte da più parole, es. `!search c d c` per Core Dynamic Composites.

Le risorse che dipendono dallo stato richiedono il molto impegno; si prega di controllare se le informazioni sono obsolete, osservando la data e lo stato tramite la mappa della galassia.

La ricerca di un sistema specifico può essere effettuata inviando un comando di questo tipo ("@nome_sistema" alla fine):

- `!search selenium @deciat`

## Materiali Raw

Quando ci si avvicina a un corpo Atterratile, EDR mostrerà la presenza di materiali raw rilevanti (di grado elevato) su un pianeta se la disponibilità supera la mediana galattica (più è alta, meglio è).

### Profili

Se siete alla ricerca di materiali raw di qualità inferiore o di qualcosa di specifico, potresti scoprire che le notifiche di materiali raw predefiniti non sono altrettanto utili. È possibile passare a un diverso insieme di materiali inviando il comando !materials .

Ad esempio, se si cercano materiali per potenziare il proprio FSD, inviare `!materials fsd`. Questo personalizza le notifiche per mostrare solo i materiali utilizzati per le iniezioni FSD di sintesi.

Altri comandi:

- `!materials` per vedere l'elenco dei profili disponibili.
- `!materials default` per tornare al profilo predefinito (ovvero materiali row di alta qualità)

#### _Profili dei materiali personalizzati_

È inoltre possibile aggiungere i propri profili di materiali raw:

1. Fare una copia del file `raw_profiles.json` (vedi nella la cartella dati di EDR)
2. Rinominalo `user_raw_profiles.json`
3. Modifica e rinomina i profili in base alle proprie esigenze.
4. Salva il file.

## Materiali Odyssey

### Valutazione

EDR mostrerà una rapida valutazione dei materiali Odyssey per i seguenti eventi:

- Prendere una missione con un oggetto specifico della missione.
- Indicare un materiale con il sistema di gesti del gioco (quanti blueprints/upgrades/synthesis/techbroker, rarità, luoghi tipici, richiesti dagli ingegneri e se ne avete ancora bisogno, ...). Questo funziona anche per i materiali Horizons.

<img alt="On-foot material analysis interface" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_14.png?raw=true">

- Inviando il comando `!eval backpack`, `!eval locker` o <tt>!eval _nome_materiale_</tt> (es. `!eval air quality reports`).
- Configurazione di un ordine di acquisto o di vendita di un materiale presso il Bar del trasportatore della flotta.

Inoltre, EDR mostrerà una valutazione dei materiali dell’odissea nello zaino o nello stoccaggio del giocatore sui seguenti eventi:

- Vendita di materiale ad un bar.
- Gettando via un po' di materiale.

Queste funzionalità sono utili perché ci sono **molti** materiali Odyssey inutili…

### Bar delle Fleet Carrier

Quando visitate un bar con materiali in vendita, EDR vi mostrerà un elenco dei materiali più utili che potreste considerare di acquistare. Ciascuna voce è seguita da una serie di lettere+numeri per fornire ulteriori indicazioni sul valore di ciascuna voce:

- B: numero di progetti che utilizzano tale elemento
- U: quantità per gli aggiornamenti che utilizzano quell'oggetto
- X: valore di scambio ai bar della stazione
- E: quantità per sbloccare l'ingegnere

Se un bar non ha nulla in vendita, o nulla di utile in vendita, EDR potrebbe mostrare un elenco dei materiali meno utili che possono essere venduti al bar. Usalo per fare spazio nel tuo inventario vendendo le cose meno utili.

È inoltre possibile attivare queste valutazioni per l'ultima barra portante della flotta che hai visitato con il seguente comando in chat di gioco:

- `!eval bar` o `!eval bar stock` per valutare gli articoli in vendita.
- `!eval bar demand` per valutare gli elementi richiesti dal proprietario della fleet carrier.

    <img alt="Example of the interface and materials for the bar" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_15.png?raw=true">

# Funzionalità Dedicate alla Ship

## Dove ho parcheggiato la mia nave?

EDR vi permette di trovare dove avete parcheggiato le vostre navi.

Comandi:

- <tt>!ship _tipo_nave_</tt> per trovare navi di un certo tipo (es. `!ship mamba`)
- <tt>!ship _nome_nave_</tt> per trovare navi con un determinato nome (es. `!ship Indistruttibile II`)
- <tt>!ship _id_nave_</tt> per trovare le navi con un certo ID nave (es. `!ship EDR-001`)

Nota: questa funzione dovrebbe indicare anche l'orario previsto di arrivo a destinazione di una nave se è stato avviato un trasferimento.

## Proprietà del Sistema di Alimentazione

EDR è in grado di valutare le priorità del sistema di alimentazione per la massimizzazione della sopravvivenza. Nota: questa funzione è un po' difettosa a causa di una serie di errori/cause nell'implementazione di Fdev.

Comando:

- `!eval power` per ottenere una valutazione delle priorità del sistema di alimentazione.
- Se non funziona, guarda il tuo pannello di lato destro, giocherellone con le priorità di potenza avanti e indietro e riprova.

## Trovare un parcheggio per la tua Fleet Carrier

Il comando `!parking` vi aiuterà a trovare un posto dove parcheggiare la tua fleet carrier.

- Invia `!parking` per ottenere informazioni sugli slot di parcheggio nella tua posizione attuale.
- Provare i sistemi vicini inviando `!parking #1`, `!parking #2`, ecc. per ottenere informazioni sugli slot di parcheggio del sistema #1, #2, ... vicino alla posizione attuale.
- Invia `!parking Deciat` o `!parking Deciat #3` per cercare i parcheggi in Deciat o nelle sue vicinanze (o in un sistema a scelta).

Come sempre, EDR copierà le informazioni sul sistema negli appunti, in modo da poterle cercare rapidamente nella mappa galattica.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_16_Black.png?raw=true">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_16_White.png?raw=true">
  <img alt="Explanation of the interface of where the Fleet Carrier is parked" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_16_White.png?raw=true">
</picture>

## Atterraggio

L'EDR mostrerà le informazioni chiave su una stazione al momento dell'attracco, così come la posizione della piattaforma di atterraggio per stazioni coriolis, orbis, fleet carrier e alcune specifiche posizioni planetarie.

<img alt="Example of a planetary station interface when requesting the dock" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_17.png?raw=true">

# Funzionalità Dedicate allo Squadron

## Nemici e alleati dello squadrone

Se fate parte di uno squadrone su Inara, potete usare EDR per taggare altri giocatori come nemici o alleati del vostro squadrone. È necessario essere un membro attivo di una squadrone su [Inara](https://inara.cz/) e avere un grado sufficientemente alto.

- Accesso alla lettura: Copilota o superiore.
- Accesso alla scrittura: wingman e superiore.
- Modifica/rimozione dei tag: stesso grado o grado superiore a quello della persona che ha taggato il giocatore

### Tag

Inviate i seguenti comandi per etichettare un altro giocatore ( es. `#ally David Braben`) o il vostro bersaglio (es. `#ally`) come nemico o alleato del tuo squadrone:

- `#ally` o `#s+` per taggare un comandante come alleato.
- `#enemy` o `#s!` per taggare un comandante come nemico.
- `-#ally` o `-#s+` per rimuovere il tag alleato da un comandante.
- `-#enemy` o `-#s!` per rimuovere il tag nemico da un comandante.

# Funzionalità Dedicate al Bounty Hunting

Inviate il seguente comando tramite la chat di gioco per ottenere informazioni sui fuorilegge:

- `!outlaws` per visualizzare un elenco degli ultimi fuorilegge avvistati e la loro posizione.
- <tt>!where _nome_cmdr_</tt> per visualizzare l'ultimo avvistamento di _nome_cmdr_ a condizione che EDR li consideri fuorilegge.

## Avvisi in tempo reale

Inviate il seguente comando tramite la chat di gioco per controllare gli avvisi in tempo reale sui fuorilegge:

- `?outlaws on` per attivare gli avvisi in tempo reale sui fuorilegge.
- `?outlaws off` per disattivare gli avvisi in tempo reale sui fuorilegge.
- `?outlaws cr 10000` per impostare una taglia minima di 10k crediti.
- `?outlaws ly 120` per impostare una distanza massima di 120 anni luce dalla vostra posizione.
- `?outlaws cr -` per rimuovere la condizione di taglia minima.
- `?outlaws ly -` per rimuovere la condizione di distanza massima.

## Statistiche e Grafici della Caccia alle Taglie

DA FARE

# Funzionalità Dedicate al Powerplay

## Caccia in powerplay

Se siete affiliati da abbastanza tempo a una potenza, potete usare i seguenti comandi per ottenere informazioni sui nemici del powerplay:

- `!enemies` per visualizzare l'elenco degli ultimi nemici avvistati e la loro posizione.
- <tt>!where _nome_cmdr_</tt> per visualizzare l'ultimo avvistamento di _nome_cmdr_, a condizione che EDR lo consideri un nemico del powerplay.

# Funzionalità Dedicate al Mining

EDR mostra varie statistiche e informazioni per aiutarvi a estrarre in modo più efficiente (vedere [questo video](https://www.youtube.com/watch?v=1bp_Q3JgW3o) per i dettagli):

<img alt="Example of mining assistance interface with explanation of parameters" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_18.png?raw=true">

Inoltre, EDR vi ricorderà di rifornirvi di limpet prima di lasciare la stazione.

# Funzionalità Dedicate all'Exobiology

## Informazioni sul bioma

### Info sul sistema

EDR indicherà se un sistema ha pianeti con le condizioni giuste per l'esobiologia. Le informazioni vengono visualizzate quando si entra in un sistema, dopo una scansione honk o inviando il comando `!biology` senza alcun parametro. Si noti che le informazioni sono un'ipotesi, si consiglia di ricontrollare la mappa del sistema per verificare la presenza di segnali biologici e di prendere in considerazione la scansione completa del sistema e/o di eseguire una scansione planetaria per una maggiore sicurezza.

### Info specifiche sul pianeta

EDR è in grado di stimare quali specie biologiche si possono trovare su un pianeta a seconda delle condizioni atmosferiche e del tipo di pianeta. Le informazioni sono mostrate nei seguenti scenari:

- Quando si punta a un pianeta (vedere le righe "Biologia prevista" e "Progressi"), o inviando il comando !biology per un determinato pianeta (es. `!biology A 1`):

  <img alt="Example of a planet's information interface with biological material" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_19.png?raw=true">

- Dopo aver mappato tutto il pianeta, EDR aggiornerà le informazioni “bioattese” per riflettere i generi reali che si possono trovare sul pianeta. Nota: le specie sono comunque ipotesi di EDR.

  <img alt="Example of interface of relevant information of a planet with biological material" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_20.png?raw=true">

## Navigazione e monitoraggio dei progressi

Per migliorare l'efficienza con le attività di esobiologia, EDR fornisce le seguenti caratteristiche:

- Informazioni chiave per le specie attualmente individuate:

  <img alt="Example of biological material information interface and how far to move for the next scan" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_21.png?raw=true">

  Dall'alto in basso:

  - Nome della specie.
  - Valore della specie in crediti.
  - Distanza minima richiesta per la diversità genetica.
  - Distanza e posizione rispetto ai campioni precedenti (se il cerchio è pieno, significa che la distanza da un determinato campione è sufficiente).

- Dopo aver campionato con successo una specie (3 campioni), EDR mostrerà i progressi fatti finora:

  <img alt="Example of an information interface on the scanning status of the biological forms available on the planet" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_22.png?raw=true">

  - Numero di specie analizzate rispetto al numero totale di generi conosciuti.
  - Nome delle genere analizzato.
  - Numero di specie analizzate.

- Se lungo il percorso si incontrano altre specie, è possibile registrare le loro posizioni per poterle poi ritrovare. Questo può essere fatto sia tramite lo scanner di composizione (nave, srv), sia utilizzando il gesto di "puntamento" mentre si è a piedi.
  - Questi POI personalizzati possono essere sfogliati/richiamati inviando i comandi `!nav next` o `!nav previous`.

  - È inoltre possibile cancellare il POI corrente inviando il comando `!nav clear` e cancellare tutti i POI personalizzati inviando il comando `!nav reset`.

  - Nota: questi POI personalizzati sono temporanei (vengono cancellati quando l'EDMC viene chiuso).

    <img alt="Example of a navigator interface that takes you to the next point" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_23.png?raw=true">

  - In alto: angolo della rotta a cui puntare per seguire il percorso.

  - Nome del waypoint, ora di registrazione del waypoint.

  - Distanza.

  - Latitudine e longitudine

  - Angolo della rotta al momento della registrazione del waypoint.

## Alla ricerca di un pianeta buono per l'esobiologia

Inviare `!search genere` per trovare un pianeta vicino con condizioni note per una dato genere (es. `!search stratum`). Si può anche usare il nome completo della specie (es. `!Search stratum tectonicas`), o alcuni tipi di pianeti (es. `!Search water` `!Search ammonia` o `!Search biology`). Suggerimento: inviare `!search` con le prime lettere di una specie, di un genere (o di una risorsa ingegneristica).

# HUD rotta

EDR mostrerà una panoramica di un percorso tracciato sulla mappa della galassia, purché non sia banale (meno di 3 salti) o troppo complesso (più di 50 salti). Questo "HUD del percorso" viene visualizzato anche quando si passa al waypoint successivo del percorso.

L’HUD fornisce le seguenti informazioni:

- Nomi dei sistemi correnti, successivi e ultimi nel percorso.

- Nomi non generici dei sistemi lungo il percorso (es. i sistemi con una serie di numeri vengono mostrati solo se sono tra i sistemi attuali, successivi o ultimi del percorso).

- Un simbolo visivo che indica se la stella primaria di un sistema è scoopabile (cerchio) o no (croce). Nota: il colore del simbolo rappresenta il tipo di stella primaria (il waypoint corrente è sempre in blu).

    <img alt="Example of interstellar navigation assistance interface, indicates different components for the various jumps to be made" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_24.png?raw=true">

- Le stelle uniche o pericolose sono annotate da un prefisso descrittivo dopo il nome del sistema (ad esempio Neutron, Nani bianchi, Black Hole, ecc.).

- Statistiche sul percorso e sui vostri progressi.
  - Nel sistema di partenza sono presenti le seguenti informazioni:
    - A quanti salti di distanza dalla partenza.
    - Distanza dal punto di partenza.
    - Tempo trascorso.

        <img alt="Example of interstellar navigation assistance interface, indicates route progress details (start system name, how many jumps you have made, distance from the start system and elapsed time)" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_25.png?raw=true">

  - Sul sistema successivo sono riportate le seguenti informazioni:
    - una media della durata tra ogni salto (es. 18 sec/j = 18 secondi per salto).
    - una stima della velocità di salto (es. 1780 LY/HR = 1780 anni luce all'ora).

       <img alt="Example of interstellar navigation assistance interface, indicates route progress details on current system (current system name, average time to jump, average speed per hour in Ly/Hr)" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_26.png?raw=true">

  - Sul sistema di destinazione sono riportate le seguenti informazioni:
    - Quanti salti rimangono per raggiungere la destinazione.
    - Distanza residua dalla destinazione.
    - Tempo residuo stimato per raggiungere la destinazione

        <img alt="Example of interstellar navigation assistance interface, indicates route progress details on the final system (current system name, remaining hops, remaining distance and remaining time to the arrival system)" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_27.png?raw=true">

# Spansh companion

EDR integra una serie di funzioni per sfruttare al meglio [Spansh](https://spansh.co.uk/), che è un sito web che offre vari strumenti di navigazione, per aiutarvi a capire quanti progressi state facendo, come mostrato di seguito:

<img alt="Example of interface for Spanish integration, indicates the jumps to be made, the time needed and other information" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_28.png?raw=true">

- Sistemi di partenza e di destinazione.
- Waypoint corrente e numero totale di waypoint.
- Numero di corpi da controllare (per un certo tipo di rotte Spansh).
- Tempo di arrivo previsto, distanza rimanente e salti.
- Stat: LY per ora, salti per ora, LY per salto, tempo trascorso tra un salto e l'altro, ecc.

Funzionalità chiave:

- Inviare `!journey new` per iniziare a creare un percorso Spansh con informazioni precompilate (es. la portata del salto, la posizione attuale). Si noti che è possibile specificare anche una destinazione (es. `!journey new colonia`).
- Inviando `!journey fetch` tenterà di scaricare una rotta Spansh dal suo indirizzo/URL. (**Si noti che l'indirizzo/URL deve essere prima copiato negli appunti!**).
- EDR fa avanzare automaticamente il percorso fino al waypoint corrente e inserisce il waypoint successivo negli appunti per comodità (cioè per facilitare la tracciatura del percorso fino al waypoint successivo).
- Per i percorsi Spansh più avanzati (es. road to riches, exomastery), EDR fornisce anche informazioni su quali corpi controllare a ogni waypoint. Inviare `!journey bodies` per ottenere l'elenco dettagliato.
  - EDR segnerà automaticamente un corpo come fatto (es. mappato per la road to riches, completamente esplorato o al momento della partenza dell'exomastery).
  - È anche possibile contrassegnare manualmente un elenco di corpi come fatto, inviando il comando `!journey check` (es. `!journey check 1 A`, oppure `!journey check 1 A, 1 B, 2 D`).
- Invia `!journey next` o `!journey previous` per regolare manualmente il waypoint corrente.
- Se si esce dal gioco a metà di un viaggio, EDR riprenderà il viaggio da dove lo si è lasciato alla sessione successiva.

Altri comandi:

- `!journey overview` per visualizzare le informazioni principali sul viaggio.
- `!journey waypoint` per visualizzare le informazioni chiave sul waypoint corrente.
- `!journey load` per caricare manualmente un viaggio da un file csv (journey.csv per impostazione predefinita se non viene fornito alcun parametro).
- `!clear` viaggio per dire a EDR di non seguire più il viaggio se c'è
- L'invio di `!journey` senza alcun parametro cercherà di fare la cosa giusta ogni volta che viene chiamato:
  - Se non c'è nessun viaggio: recuperare un viaggio Spansh dagli appunti, se esiste, o caricare un viaggio locale, se esiste, o altrimenti iniziare un nuovo viaggio Spansh.
  - Se c'è un viaggio, mostrate una panoramica.

# Insediamenti Odyssey

È possibile usare il comando `!search` per trovare insediamenti Odyssey specifici.
Ecco alcuni esempi:

- `!search anarchy` troverà l'insediamento anarchico più vicino alla vostra posizione attuale.
- `!search anarchy @ Lave` troverà l'insediamento anarchico più vicino al sistema Lave.
- Sono supportati tutti i tipi di governo conosciuti (es. `!search democracy`)
- Altre condizioni supportate:
  - Stati del BGS (es. `!search bust`)
  - Affiliazioni (es. `!search imperial`)
  - Economia (es. `!search tourism`)
- È possibile combinare più condizioni per limitare la ricerca (es. `!search anarchy, military`)
- Infine, è possibile escludere anche delle condizioni. Ad esempio, `!search anarchy, -military` troverà l'insediamento anarchico non militare più vicino. Nota: per impostazione predefinita, EDR esclude gli stati di guerra e di guerra civile, ma è possibile invertire questa tendenza aggiungendo queste condizioni al comando (es. `!search war, civil war` troverà l'insediamento più vicino il cui stato è considerato in guerra o in guerra civile).
- Sono previste anche due comode scorciatoie: `!Search cz` per trovare l'insediamento più vicino che probabilmente è in una zona di combattimento, e `!Search restore` per trovare l'insediamento più vicino che probabilmente è abbandonato.

**Importante:** a causa della natura dinamica del BGS di Elite Dangerous, non è garantito al 100% che la funzione di ricerca restituisca sempre risultati corretti. Utilizzare le informazioni mostrate da EDR quando ci si avvicina al regolamento per confermare che le condizioni effettive corrispondono a quanto ci si aspettava.

# Integrazione Discord

Funzionalità correnti d'integrazione con Discord:

- Inoltro dei messaggi della chat di gioco a un canale di Discord a tua scelta.
- Invio di Flotta Vettore piani di volo a un canale discordante di vostra scelta.
- Invio degli ordini di mercato della Fleet Carrier (acquisto/vendita) per commodities e materiali Odyssey.

## Inoltro dei messaggi della chat di gioco

È possibile impostare EDR per inoltrare direttamente i messaggi della chat di gioco a un server e ad'un canale Discord di propria scelta.
Si tenga presente che:

- Questo deve essere configurato dall'utente. Per impostazione predefinita EDR non inoltra nulla.
- Se lo si configura, il plugin EDR EDMC invierà direttamente i messaggi al proprio server/canale Discord.
- Il back-end di EDR (server) NON è coinvolto in alcun modo. **In altre parole, i vostri messaggi non vengono mai condivisi con EDR, né inviati ai server di EDR.**
- _Ho menzionato che i messaggi che ricevete e inviate rimangono privati? L'ho fatto? OK, bene!_

### Pre-requisiti

L'integrazione di Discord richiede quanto segue:

- Possedere un account [Discord](http://discord.com), e un server Discord personale (o un server che si può amministrare o si può chiedere a un amministratore di seguire le istruzioni).
- Consultate i [webhooks di Discord](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).

### Configurazione dei canali Discord (webhook)

Nella cartella config, cercate un file chiamato user\_config\_sample.ini e seguite le istruzioni.

### Funzionalità

L'integrazione di Discord offre le seguenti caratteristiche:

#### _Messaggi in arrivo_

- Possibilità di inoltrare i messaggi ricevuti su uno qualsiasi dei canali di gioco (es. local, system, team, squadron, squadron leaders, crew) a un server Discord e a un canale a scelta (configurabile per canale).
- Possibilità di configurare se e come i messaggi vengono inoltrati per ogni canale e per specifici comandanti. Vedi le [opzioni di personalizzazione di seguito](#opzioni-di-personalizzazione).
- Possibilità di inoltrare i messaggi diretti inviati mentre si è in AFK a un server e a un canale Discord di propria scelta.

#### _Messaggi in uscita_

- Possibilità di inviare messaggi specifici a un server e a un canale Discord di vostra scelta tramite il comando di chat in-game `!discord` (es. `!discord` sto per incassare una missione in team, qualcuno è interessato a qualche credito gratuito?)
- Possibilità di inoltrare i messaggi inviati su uno qualsiasi dei canali di gioco (es. system, team, squadron, squadron leaders, crew) a un server discord e a un canale a scelta (configurabile per canale).

#### _Opzioni di personalizzazione_

È possibile definire una serie di condizioni di base per l'inoltro da parte di EDR. Queste condizioni possono essere modificate per canali specifici e comandanti specifici.

- `blocked`: buleano. Se impostato su true, blocca l'inoltro.
- `matching`: elenco di espressioni regolari. Usa questo per limitare l'inoltro ai messaggi che corrispondono ad almeno una di queste espressioni regolari.
- `discordante`: elenco di espressioni regolari. Utilizzare questa opzione per limitare l'inoltro ai messaggi che non corrispondono a nessuna di queste espressioni regolari.
- `min_karma`: numero compreso tra -1000 e 1000. Utilizzare questa opzione per limitare l'inoltro ai messaggi il cui karma EDR dell'autore è superiore al valore impostato.
- `max_karma`: numero compreso tra -1000 e 1000. Utilizzare questa opzione per limitare l'inoltro ai messaggi il cui karma EDR dell'autore è inferiore al valore impostato.
- `name`: per sostituire il nome del cmdr con qualcosa a scelta.
- `color`: per sostituire il colore dell'embed che mostra le informazioni extra (RGB in decimale come 8421246; default: da rosso a verde a seconda del karma EDR del cmdr).
- `url`: per sostituire il link del incorporato (predefinito: profilo Inara se presente).
- `icon_url`: per sostituire l'icona nell'embed (default: immagine del profilo di Inara, se presente, o icona unica generata automaticamente; si aspetta un URL per un'immagine).
- `image`: si usa per forzare un'immagine nell'incorporamento (default: nessuna immagine; si aspetta un URL per un'immagine).
- `thumbnail`: usare questo parametro per forzare una miniatura nell'embed (default: nessuna miniatura; si aspetta un URL per un'immagine).
- `tts`: funzione text-to-speech di Discord (impostata su true se si vuole che Discord legga ad alta voce il messaggio di questo comandante; è necessario essere sul canale Discord giusto per sentirlo).
- `spoiler`: impostare su true se si desidera nascondere i messaggi di questo comandante dietro un tag spoiler ( è necessario cliccarci sopra per rivelare il contenuto).

Esempio di un [buon file di configurazione](https://imgur.com/a/2fflOo0). Spiegazione:

- il livello superiore viene utilizzato per impostare i valori predefiniti per ogni comandante (es. secondo):
  - i messaggi contenenti git gud non vengono mai inoltrati e il mittente deve avere un karma EDR superiore a -100.
- un comandante chiamato Cranky North Star i cui messaggi sono sempre bloccati.
- un comandante chiamato Chatty Plantain con una regola di ridenominazione per forzare "[PNG] Chatty Plantain" come nome del comandante, oltre a nascondere i messaggi dietro un tag spoiler.
- per canale (es. player, team, squadron, squad leaders, crew), che rimuove le restrizioni relative alla mancata corrispondenza e al karma.

Per ulteriori istruzioni, consultare il file `user_discord_players.txt` nella cartella config (il file personalizzato deve essere denominato `user_discord_players.json` e non deve contenere commenti, ossia nessuna riga che inizi con `;`).

## Invio del piano di volo della propria Fleet Carrier a Discord

Potete inviare i vostri piani di volo a fc-jumps di EDR o a un canale Discord di vostra scelta. Nel primo caso, selezionare Pubblico nelle opzioni di EDR (sezione: Trasmissioni). Per quest'ultimo, avete due opzioni:

- (Consigliato) Selezionare Direct nelle opzioni di EDR per far sì che il piano di volo venga inviato direttamente a Discord. Controlla il resto delle istruzioni nel file `user_config_sample.ini` trovato nella cartella di configurazione di EDR.
- Selezionare Privato nelle opzioni di EDR per far sì che il piano di volo venga inviato prima a EDR e poi a discord. Questo può essere utile nel caso in cui i proprietari del server non vogliano condividere direttamente l'URL del webhook per evitare abusi (es. chi abusa può essere escluso dalla logica di inoltro sul server EDR). Aprire [questo modulo](https://forms.gle/7pntJRpDgRBcbcfp8) e seguire i passaggi seguenti:

1. [Crea un webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks#:~:text=making%20a%20webhook) per il canale in cui vuoi vedere i piani di volo.
2. Copiare l'indirizzo di questo webhook e inviarlo tramite [il modulo](https://forms.gle/7pntJRpDgRBcbcfp8).
3. Aspettate qualche giorno o una settimana. Pinga _lekeno_ se non succede nulla dopo circa una settimana.

## Invio degli ordini di acquisto/vendita di materie prime e materiali Odyssey da parte della vostra Fleet Carrier

Puoi inviare i tuoi ordini di acquisto/vendita di materie prime e materiali Odyssey ad un canale Discord di tua scelta. Controlla il resto delle istruzioni nel file `user_config_sample.ini` trovato nella cartella di configurazione di EDR.

<img alt="Example of post on discord of requests to buy and sell materials in the bar" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_29.png?raw=true">

EDR invierà anche un riepilogo copiabile degli ordini di vendita/acquisto recenti alla vostra fleet carrier dopo che avrete apportato modifiche al vostro mercato e/o al vostro bar.

# Overlay

## Impostazioni multi monitor e VR

Se si dispone di una configurazione a più monitor o di un VR headset, si consiglia di impostare l'overlay come standalone (menu File, Impostazioni, scheda EDR, menu a discesa Overlay). L'overlay apparirà come una finestra separata con alcuni controlli:

<img alt="Example interface when the overlay is set as standalone" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_30.png?raw=true">

- **Angolo in alto a sinistra**: trascinare e rilasciare per spostare l'overlay, fare doppio clic per ingrandire/ripristinare.
- **Angolo inferiore sinistro**: passa il mouse per rendere trasparente l'overlay.
- **Angolo inferiore destro**: afferra per ridimensionare l'overlay.
- **Angolo in alto a destra**: passa il mouse per rendere l'overlay opaco.
- **Quadrato verde in alto al centro**: passa il mouse per far sì che l'overlay sia sempre in primo piano.
- **Quadrato rosso in basso al centro**: passa il mouse per far sì che l'overlay sia una finestra normale (non sempre in primo piano).

### Posizionamento VR con SteamVR

1. Avvio EDMC
2. Configurare le impostazioni EDR (menu File EDMC, Impostazioni, scheda EDR) con l'overlay impostato su "Standalone"
3. Avviare il gioco in VR
4. Avviare una sessione di gioco
5. L'overlay dovrebbe avviarsi automaticamente, regolando le dimensioni e la posizione come necessario (al di fuori della VR)
6. Avviare il menu dash di SteamVR, selezionare "Desktop" e quindi selezionare il desktop giusto, se ne esistono più di uno
7. Fare clic su +, selezionare `EDMCOverlay V1.1.0.0`
8. Regolare la posizione e le dimensioni nel VR
9. Chiudere il dash di SteamVR

    <img alt="Example of interface when the overlay is integrated into the VR headset" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_31.png?raw=true">

Per ulteriori dettagli, consultare anche [le note della patch SteamVR](https://steamcommunity.com/games/250820/announcements/detail/2969548216412141657).

## Personalizza overlay

Per personalizzare l'overlay, copia `igm_config.v7.ini` e `igm_config_spacelegs.v7.ini`, che si trovano nella cartella config, e rinominarli in `user_igm_config.v7.ini` e `user_igm_config_spacelegs.v7.ini` ( nota: se esistono versioni superiori alla v7, usa piuttosto quei numeri di versione).

Il primo file serve a configurare l'overlay quando si è a bordo di una nave o di un srv, mentre il secondo file serve a configurare l'overlay quando si è a piedi.

Segui le istruzioni contenute in ogni file per modificare i colori e le posizioni dei vari elementi/messaggi. È anche possibile disabilitare tipi specifici di messaggi. Quando si apportano modifiche al file di configurazione dell'overlay, inviare il comando `!overlay` per rileggere il layout, visualizzare le modifiche si stanno testando e apportare ulteriori modifiche.

# Segnalazione dei reati

Se non si desidera segnalare interazioni o combattimenti (es. PvP concordato), è possibile disattivare la segnalazione dei crimini. Nota che EDR continuerà a segnalare avvistamenti e scansioni.

- Per disattivare la segnalazione dei crimini, inviare `!crimes off`, oppure deselezionare l'opzione "Report crimini" nel pannello delle impostazioni di EDR.
- Per attivare la segnalazione dei crimini, inviare `!crimes on`, oppure selezionare l'opzione "Report crimini" nel pannello delle impostazioni di EDR.
- È possibile confermare la configurazione attuale inviando `!crimes`.

# Effetti audio

## Comandi e opzioni

Gli effetti sonori possono essere disattivati o attivati dalle opzioni EDR in EDMC (menu `File`, `Impostazioni`, scheda `EDR`, sezione `Feedback`, casella di controllo `Audio`)

## Personalizzazione

Per personalizzare gli effetti sonori, fare una copia del file `sfx_config.v1.ini`, che si trova nella cartella config, e rinominarlo `user_sfx_config.v1.ini`

Ci sono due sezioni, una chiamata `[SFX]` e un'altra chiamata `[SFX_SOFT]`. Il primo è per i suoni quando gli effetti sonori di EDR sono impostati su forte (tramite `!audiocue loud`), il secondo è per quando EDR è impostato su soft (tramite `!audiocue soft`)

- Ogni riga rappresenta un particolare tipo di evento EDR.
- Per disattivare un evento, lasciare il valore vuoto.

Inserire i suoni personalizzati (solo in formato wav) nella sottocartella custom della cartella sounds.

Quindi modificare la riga dell'evento correlato per specificare il suono personalizzato, includendo il prefisso `custom/`.

#### _Tipo di eventi_

- `startup`: quando l'EDR si avvia all'inizio di una sessione
- `intel`: quando EDR mostra il profilo di un giocatore neutrale/illegale
- `warning`: quando EDR mostra il profilo di un giocatore fuorilegge
- `sitrep`: quando EDR mostra un riepilogo delle attività di un sistema (o di tutti i sistemi)
- `notify`: quando EDR mostra alcune informazioni in risposta ad altri comandi (es. !eval, ecc.)
- `help`: quando EDR mostra l'interfaccia di aiuto tramite !help
- `navigation`: quando EDR mostra/aggiorna la UX di navigazione
- `docking`: quando l'EDR mostra le indicazioni per il docking
- `mining`: quando l'EDR mostra una guida per l'estrazione mineraria
- `bounty-hunting`: quando l'EDR mostra una guida per la caccia alle taglie
- `target`: quando EDR mostra informazioni su un target (es. scudo/scafo, punti ferita di un sottomodulo)
- `searching`: quando EDR avvia una ricerca di un servizio o di un materiale raro
- `failed`: quando EDR incontra un errore
- `jammed`: quando i server EDR sono troppo occupati per gestire le richieste
- `biology`: quando l'EDR mostra le informazioni di navigazione per le attività di Esobiologia

# Appendice

## Risoluzione dei problemi

### Non viene visualizzato nulla / L'overlay non funziona

#### _Controllare le impostazioni_

Assicuratevi di non aver disabilitato per errore l'overlay.

Passaggi:

1. Avvia EDMC.

2. Fare clic su File, poi su Impostazioni.

3. Fare clic sulla scheda EDR.

4. Nel menu a tendina dell'overlay, seleziona Attivato.

    <img alt="Setting menu, EDR tab, point where to activate the overlay" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_32.png?raw=true" height="450">

5. In Elite, torna al menu principale e avvia una nuova sessione.

Ancora nulla? Controllare la sezione successiva.

#### _Consentire l'esecuzione dell'overlay_

L'antivirus potrebbe impedire l'esecuzione dell'overlay per precauzione.

Raccomandazione: scansiona l'eseguibile e consentine l'esecuzione dopo aver confermato che non rappresenta una minaccia.

Passaggi:

1. Avvia EDMC.

2. Fare clic su File, poi su Impostazioni.

3. Clicca sulla scheda Plugin, quindi fare clic su Sfoglia.

4. Vai alla sottocartella `EDR` e poi alla cartella `EDMCOverlay`.

5. Fare clic con il tasto destro sul file `edmcoverlay.exe`, selezionare l'opzione di scansione antivirus.

    <img alt="Scan the overlay.exe file in the EDR/EDMCOverlay folder" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_33.png?raw=true">

6. Se il vostro antivirus non si lamenta, fare doppio clic sul file `edmcoverlay.exe` e permettergli di eseguire se il vostro antivirus richiede una conferma.

## La frequenza dei fotogrammi è diminuita in modo significativo

Prima di provare una delle opzioni riportate di seguito, assicurarsi che i driver grafici siano aggiornati e verificare se il problema persiste.

### Opzione 1: disattivare Vsync

1. Vai alle Opzioni di gioco di Elite:

    <img alt="Panel to open the game Settings" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_34.png?raw=true">

2. Selezionare le Graphics options:

    <img alt="Panel to open the game's graphic settings" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_35.png?raw=true">

3. Trova Vertical sync, nella sezione Display, e disattivalo:

    <img alt="Panel to open the game's graphic settings to deactivate Vertical sync in the Display section" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_36.png?raw=true">

4. Retest EDR

### Opzione 2: prova borderless / windowed / fullscreen

1. Vai alle Opzioni di gioco di Elite
2. Selezionare le Graphics options
3. Nella sezione Visualizzazione, provate le diverse modalità, ad es. Borderless / Windowed / Fullscreen, e vedete se ce n'è una che funziona meglio.

### Opzione 3: provare l'interfaccia utente alternativa di EDR

1. Sul bordo destro dello stato di EDR, spuntate la casella di controllo per visualizzare l'interfaccia utente alternativa di EDR:

    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_37_Black.png?raw=true">
      <source media="(prefers-color-scheme: light)" srcset="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_37_White.png?raw=true">
      <img alt="Interface to activate alternative/extended view of EDR in EDMC application" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_37_White.png?raw=true" height="450">
    </picture>

2. Le informazioni che sarebbero state visualizzate tramite l'overlay saranno visualizzate in quest'area

3. Accedere alle impostazioni di EDR dal menu File, poi vai nella scheda EDR

4. Disabilita l'overlay

5. Opzionale: se si desidera sovrapporre EDMC
   1. Accedere alla scheda Aspetto, selezionare Sempre in primo piano.
   2. Attivare il tema trasparente se si desidera
   3. Vai alle opzioni grafiche di Elite e seleziona senza bordi o finestra.

## Altri problemi non risolti?

Sentitevi liberi di unirvi a [EDR central](https://edrecon.com/discord), il server della comunità per EDR con accesso al bot, avvisi in tempo reale e supporto per la risoluzione dei problemi. Potresti anche condividere il tuo file di log EDMC con LeKeno su Discord, vedi sotto per le istruzioni.

Passaggi:

1. Premere contemporaneamente il tasto Windows e il tasto R.

    <img alt="Run interface to go to Temp folder" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_38.png?raw=true">

2. Digitare `%tmp%` (o `%temp%`) e premere il tasto Invio.

3. Trovare il file denominato `EDMarketConnector.log`

    <img alt="TEMP folder where the EDMC log files are present" src="https://github.com/GLWine/edr/blob/master/edr/docs/assets/IMG_39.png?raw=true">

4. Se necessario, rivedete e modificate il contenuto con il blocco note (facendo doppio clic si apre il blocco note).

5. Condividilo con LeKeno su discord.

## Informazioni sulla privacy

Se siete curiosi di sapere come funziona e cosa fa EDR, è possibile controllare il [codice sorgente](https://github.com/lekeno/edr/), e poiché è scritto in Python, e potete anche esaminare il codice in esecuzione e confermare che è identico al codice sorgente pubblicato su GitHub. Anche Frontier ha [revisionato ed elogiato EDR](https://forums.frontier.co.uk/threads/flying-in-open-last-night-edr-saved-my-life-it-could-save-yours-too.388696/page-15#post-6118053), confermando che l'uso dell'API del diario del giocatore è conforme alle loro regole e ai loro termini di servizio.

La prima volta che si esegue EDMC durante il gioco, si verrà reindirizzati al [sito web di autenticazione di Frontier](https://auth.frontierstore.net/) e verranno richiesti il nome utente e la password di Elite: Dangerous. Questo non ha **nulla a che fare con l'EDR** e **può essere completamente ignorato.** EDR NON utilizza l'API di autenticazione di Frontier, bensì quella del [diario del giocatore](https://forums.frontier.co.uk/threads/commanders-log-manual-and-data-sample.275151/) che contiene solo informazioni su ciò che accade nel gioco e NON contiene informazioni personali.

Detto questo, ecco perché potreste comunque autorizzare l'EDMC e non preoccuparvi:

- Lo scopo principale di EDMC è, come suggerisce il nome "Market Connector", quello di condividere le informazioni sul mercato di gioco in un [database centrale](https://github.com/EDSM-NET/EDDN/wiki) a beneficio di tutti. Lo fa accedendo ai dati di mercato delle stazioni in cui si è attraccati tramite l'API di autenticazione di Frontier. È così che diversi strumenti sono in grado di dirvi quali sistemi/stazioni stanno acquistando Low Temperature Diamonds a un prezzo elevato, di trovare rotte commerciali redditizie o persino quali stazioni hanno determinati moduli o navi disponibili.
- Alcune persone disinformate (o peggio) stanno diffondendo affermazioni prive di fondamento secondo cui questa API consente di accedere ai dati di fatturazione… Pensate a cosa significherebbe: una società quotata in borsa che espone informazioni sensibili dell'azienda a sviluppatori terzi?! Non ha assolutamente senso. L'API non rende disponibili tali informazioni.
- Consultare la [Politica sulla privacy di EDMC](https://github.com/Marginal/EDMarketConnector/wiki/Privacy-Policy) per capire come EDMC gestisce i vostri dati.
