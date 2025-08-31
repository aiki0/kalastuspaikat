# kalastuspaikat

## Sovelluksen toiminnot

* ✓Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* ✓Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan omia kalastuspaikkoja.
* ✓Käyttäjä pystyy lisäämään luokat ja kuvia paikkoihin.
* ✓Käyttäjä näkee sovellukseen lisätyt paikat.
* ✓Käyttäjä pystyy kommentoimaan toisten käyttäjien paikkoja.
* ✓Käyttäjä pystyy etsimään paikkoja hakusanoilla (esim. otsikko, vesistö tms..)
* ✓Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät kohteet.
* ✓Käyttäjä pystyy valitsemaan paikkaan yhden tai useamman luokittelun (esim. vesistön tyyppi tai maakunta).

## Sovelluksen asennus

Ohje on macOS/Linux järjestelmille jossa on sqlite3 sekä python3 asennettuna.

Asenna `flask`-kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut ja lisää alkutiedot:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```

## Testaus suurilla tietomäärillä

Tietomäärät : Käyttäjiä tuhat, miljoona paikkaa ja kymmenen miljoonaa kommenttia

Ennen indeksointia ilmoituksen sivulle paikan sivulle menossa kesti 0.5s-0.6s
Syynä oli kaikkien kommenttien haku sillä lisäämällä skeemaan:
```
CREATE INDEX idx_place_comments ON comments (place_id);
```
Sivulle meno kestää vain 0.01s vaikka pyytää isolla id-numerolla olevaa paikkaa

Sama toistui kun lisäsin user sivulle käyttäjän kommenttien määrän, tämä nopeutui tällä:

```
CREATE INDEX idx_comments_user ON comments(user_id);
```