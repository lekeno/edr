<div align="center">
    <img Alt="Logo_ED_Recon" src="https://edrecon.com/img/icon-192x192.8422df55.png">
    <h1>
        ED Recon</span>
        <br>
        Il Manuale Mancante
    </h1>
    Stesura a cura del <a href="https://github.com/lekeno">CMDR Lekeno</a>
    <br>
    Traduzione a cura del <a href="https://github.com/GLWine">CMDR FrostBit</a>
</div>

## Installazione

Se rimani bloccato o hai domande, non esitare a unirti a [EDR central](https://discord.gg/meZFZPj), il server della community per EDR con accesso al bot, avvisi in tempo reale e supporto per la risoluzione dei problemi.

### Pre-requisiti
- Windows
- Elite: Dangerous
- Elite Dangerous Market Connector (vedi sezione A)
- Leggere e comprendere [l'informativa sulla privacy](https://edrecon.com/privacy-policy) e i [termini di servizio](https://edrecon.com/tos) di EDR. **Procedere ulteriormente implica comprendere e accettare l'informativa sulla privacy e i termini di servizio.**

### Elite Dangerous Market Connector
**Se hai già installato Elite Dangerous Market Connector (EDMC), passa alla sezione successiva.**

ED Recon è offerto come plug-in per Elite Dangerous Market Connector, un ottimo strumento di terze parti per Elite: Dangerous. Controlla le [istruzioni ufficiali](https://github.com/EDCD/EDMarketConnector/wiki/Installation-&-Setup) se le spiegazioni seguenti non sono sufficienti.

Passaggi:
1.	Leggi [l'informativa sulla privacy di EDMC](https://github.com/EDCD/EDMarketConnector/wiki/Privacy-Policy). Se non sei d'accordo con qualcosa o non capisci tutto, NON procedere oltre.
2.	[Scarica l'ultima versione di EDMC](https://github.com/EDCD/EDMarketConnector/releases/tag/Release/latest) (il file .exe)
3.	Fare doppio clic sul file scaricato per installarlo.
○	Windows potrebbe darti un avviso sul file. Clicca su *`maggiori informazioni`* poi su *`Esegui comunque`*. Se sei preoccupato, sentiti libero di eseguire prima una scansione antivirus sul file scaricato.
4.	Esegui Elite Dangerous Market Connector dal menu Start o dalla schermata Start.
5.	Facoltativo: consenti a EDMC di accedere all'API di Frontier per tuo conto (**EDR NON utilizza l'API di Frontier, quindi sentiti libero di ignorare questa richiesta di autenticazione**).

### ED RECON (AKA EDR)
Passaggi:
1.	[Scarica l'ultima versione di EDR](https://github.com/lekeno/EDR/releases/latest) (il file EDR.v#.#.#.zip dove #.#.# è il numero di versione, es. 2.7.5 nello screenshot seguente)

    <picture>
        <source media="(prefers-color-scheme: dark)" srcset="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/EDR_2.7.5_Black.png?raw=true">
        <source media="(prefers-color-scheme: light)" srcset="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/EDR_2.7.5_White.png?raw=true">
        <img alt="Screenshot sito edr, pagina rilascio 2.7.5" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/EDR_2.7.5_White.png?raw=true">
    </picture>

2.	Avvia EDMC.
3.	Fare clic su File, poi su Impostazioni.

    <img alt="Immgaine pagina iniziale EDMC" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_01-02_it.png?raw=true">

4.	Clicca sulla scheda Plugin, quindi fare clic su Sfoglia.

    <img alt="Immgaine pagina iniziale EDMC" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_03-04_it.png?raw=true">
  
5.	Crea una sotto cartella denominata EDR nella cartella dei plugins.

    <img alt="Immgaine pagina iniziale EDMC" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_05_it.png?raw=true">

6.	Estrai il contenuto del file Zip scaricato al passaggio 2 in questa sotto cartella EDR.

    <img alt="Immgaine pagina iniziale EDMC" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_06.png?raw=true">

7.	Riavviare EDMC.
8.	Dovresti vedere una riga di stato EDR (es. EDR: autenticato (ospite)) nella parte inferiore di EDMC:
    
    <img alt="Immgaine pagina iniziale EDMC" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_07.png?raw=true">

9.	Avvia Elite, avvia una nuova sessione.
10.	Dovresti vedere un messaggio introduttivo (es. `EDR V2.7.5 […]`) sovrapposto a Elite.
●	Su Windows 10: l'overlay dovrebbe funzionare per tutte le modalità (Fullscreen, Borderless, Windowed).
●	Su Windows 7: l'overlay NON funziona in Fullscreen, utilizza invece il Borderless o il Windowed.
●	Se l'overlay non funziona, consultare la sezione sulla [risoluzione dei problemi]().
### ACCOUNT EDR
EDR funziona subito senza alcun account. Tuttavia, se desideri fornire informazioni a EDR e ai suoi utenti, ad es. inviando avvistamenti di fuorilegge, dovrai [richiedere un account](https://edrecon.com/account).

Osservazioni importanti:
- Le domande vengono valutate manualmente per garantire un servizio di alta qualità. Questo potrebbe richiedere alcune settimane.
- Se hai chiesto di essere contattato su Discord: controlla un'eventuale richiesta di amicizia da LeKeno.
- Se hai richiesto di essere contattato via email: assicurati che l'email da edrecon.com non sia finita nella tua cartella spam.

Dopo aver ottenuto le credenziali, apri le impostazioni EDR (`File` menu, `Impostazioni`, scheda EDR) compila di conseguenza i campi e-mail e password e fai clic su OK.

<img alt="Immgaine pagina iniziale EDMC" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_08_it.png?raw=true">

Se tutto procede secondo i piani, dovresti vedere "autenticato" nella riga di stato EDR.

<img alt="Immgaine pagina iniziale EDMC" src="https://dummyimage.com/900x400/ced4da/6c757d.jpg">

## EDR in breve
L'EDR offre una vasta gamma di funzionalità progettate per facilitare e migliorare la tua esperienza in Elite Dangerous: profili dei giocatori basati su segnalazioni in gioco, ricerca di materiali rari, valutazione del valore dei materiali di Odyssey, ecc. 
Queste funzionalità si attivano automaticamente in base a ciò che accade nel gioco, oppure possono essere attivate inviando comandi EDR (es. !who lekeno) tramite la chat in gioco (qualsiasi canale), o tramite il campo di input EDR nella finestra di EDMC:
 
#### Output
L'EDR mostra varie informazioni utili tramite un overlay grafico e un'interfaccia utente testuale nella finestra di EDMC. 
- L'overlay può anche essere configurato come una finestra indipendente per monitor multipli o VR setups (nel menu File, seleziona Impostazioni, quindi vai alla scheda EDR, e imposta Overlay su standalone).
- L'interfaccia utente testuale può essere espansa o compressa con la casella di controllo sul lato destro della riga di stato EDR in EDMC.
#### Aiuto e Suggerimenti
Quando si avvia una nuova sessione di gioco, EDR mostrerà un suggerimento casuale riguardante il gioco o EDR stesso. 
- Inviando !help otterrai una guida breve e chiara sui vari comandi EDR.
- Puoi anche richiedere un suggerimento casuale inviando il comando !tip, oppure !tip edr per suggerimenti su EDR, e !tip open per suggerimenti sul giocare in modalità Open.

## Funzionalità Dedicate ai Commander
### Profilazione Automatica dei Comandanti
Se EDR rileva la presenza di un comandante potenzialmente pericoloso (es. un fuorilegge), mostrerà automaticamente il profilo di quel comandante. 
Esempi: 
- Quando si riceve un messaggio (direct, local, system, ecc.) da un fuorilegge. 
- Essere interdetti da un fuorilegge.
- Unirsi / formare un team con un fuorilegge. 
- Avere un fuorilegge che si unisce a una sessione multicrew.

### PROFILAZIONE MANUALE DEI COMANDANTI
Traghettare un altro giocatore svelerà il loro profilo EDR. Per gli utenti con un account, completare una scansione comporterà l'invio delle informazioni al server EDR a beneficio degli altri utenti EDR. In alternativa, puoi attivare una ricerca del profilo del comandante EDR + Inara tramite:

- Invio di **`o7`** al cmdr che ti interessa (come direct message).
- Inviando **`!who nome_cmdr`** o **`!w nome_cmdr`** tramite la chat in gioco (qualsiasi canale: locale, squadrone, team, sistema, ecc.), oppure tramite il campo di input EDR nella finestra di EDMC. Esempio: **`!w lekeno`**

EDR mostrerà anche informazioni chiave (HP, dimensione/classe, tendenze) sulla nave/veicolo del tuo bersaglio e sul sottomodulo selezionato, se presente:

<img alt="Immgaine pagina iniziale EDMC" src="https://dummyimage.com/900x400/ced4da/6c757d.jpg">