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
 
6.	Estrai il contenuto del file Zip scaricato al passaggio 2 in questa sotto cartella EDR.
 
7.	Riavviare EDMC.
8.	Dovresti vedere una riga di stato EDR (es. EDR: autenticato (ospite)) nella parte inferiore di EDMC:
 
9.	Avvia Elite, avvia una nuova sessione.
10.	Dovresti vedere un messaggio introduttivo (es. EDR V0.9.5 […]) sovrapposto a Elite.
●	Su Windows 10: l'overlay dovrebbe funzionare per tutte le modalità (Fullscreen, Borderless, Windowed).
●	Su Windows 7: l'overlay NON funziona in Fullscreen, utilizza invece il Borderless o il Windowed.
●	Se l'overlay non funziona, consultare la sezione sulla risoluzione dei problemi.

