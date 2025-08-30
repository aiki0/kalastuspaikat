# kalastuspaikat


* ✓Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* ✓Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan omia kalastuspaikkoja.
* ✓Käyttäjä pystyy lisäämään luokat ja mahdollisesti kuvia paikkoihin.
* ✓Käyttäjä näkee sovellukseen lisätyt kalapaikat.
* ✓Käyttäjä pystyy etsimään paikkoja hakusanoilla (esim kalalaji, vesistö tms..)
* ✓Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät kohteet.
* ✓Käyttäjä pystyy valitsemaan paikkaan yhden tai useamman luokittelun (esim. vesistön tyyppi, kalalajit, luvallinen/ei).
* ✓Käyttäjä pystyy luomaan uusia paikkoja.

# Ohjelman testaaminen
Ohje koskee macOS/Linux järjestelmiä. Käytä terminaalia ja syötä siihen alla olevia komentoja järjestyksessä.
 * Kloonaa Github-repo -> "git clone https://github.com/aiki0/kalastuspaikat"
 * Siirry kansioon -> "cd kalastuspaikat"
 * Luo pythonin virtuaaliympäristö -> "python3 -m venv venv"
 * Aktivoi virtuaali ympäristö -> "source venv/bin/activate"
 * Asenna tarvittava python kirjasto "pip install flask"
 * Luo tietokanta schema.sql tiedoston kautta -> "sqlite3 database.db < schema.sql"
 * Käynnistä flask serveri -> "flask run"
 * Nettisivut toimivat ip osoitteessa joka syntyy terminaaliin (käytä esim chrome)
 * Nettisivut ovat toistaiseksi hyvin pelkistetyt ja toimivat yksinkertaisesti


# Testaus suurilla tietomäärillä

Tietomäärät : Käyttäjiä tuhat, miljoona paikkaa ja kymmenen miljoonaa viestiä

Ennen indeksointia ilmoituksen sivulle paikan sivulle menossa kesti 0.5s-0.6s
Syynä oli kaikkien kommenttien haku sillä lisäämällä:
CREATE INDEX idx_item_comments ON comments (item_id);
Sivulle meno kestää vain 0.01s vaikka pyytää isolla id-numerolla olevaa paikkaa
