## Kataster nástroj pre GIS

Ide o nástroj na konverziu a import grafických a popisných katastrálnych dát Slovenskej republiky do GIS (Ivanov a spol). Popis dát KN je [TU](https://github.com/lfurtkevicova/hn-stuff/wiki).

<p> :+1: :pray: :e-mail: :hear_no_evil: :speak_no_evil: :see_no_evil: :blush:  

### Nasadenie
* vytvorenie Python *virtualenv* (virtuálne prostredie v podobe fyzického adresára, ktorý obsahuje unix-ovú štruktúru s binárkami, atď.)

```{r, engine='sh', count_lines}
$ virtualenv --system-site-packages $HOME/venvs/kataster-import
$ source $HOME/venvs/kataster-import/bin/activate
```

* inštalácia pomocou *setup.py*

```{r, engine='sh', count_lines}
$ git clone https://github.com/imincik/kataster-import.git
$ cd kataster-import
$ python ./setup.py install
$ pip install -r requirements.txt
````

* bez inštalácie

```{r, engine='sh', count_lines}
$ git clone https://github.com/imincik/kataster-import.git
$ cd kataster-import
$ pip install -r requirements.txt
$ source ./env-setup.sh
```

### Uloženie vstupných dát

* hlavný adresár
  * adresár `vgi`                    - grafické dáta KN
  * adresár `dbf`, `fpu` alebo `fpt` - popisné dáta KN

### Použitie

#### Konverzia všetkých dát

*kt-sql* - skript slúži ako wrapper nad ostatnými špecializovanými nástrojmi a umožňuje vykonať konverziu SGI a SPI v jednom kroku. 

```{r, engine='sh', count_lines}
$ kt-sql <hlavny-adresar>
```

#### Import dát do PostGIS
Dáta získané konverziou je možné importovať do PostGIS z vytvorených SQL súborov - adresár *<hlavny-adresar>/sql*. Predpokladá sa, že už existuje **user**, napr. *ludka*, t.j. rovnako ako názov PC.

* prihlásenie do databázy *postgres*, výpis zoznamu databáz a vytvorenie databázy *kataster*, prepnutie sa do novej databázy

```{r, engine='sql', count_lines}
$ psql postgres
\l
createdb kataster;
\connect kataster;
```

* vytvorenie geodatabázy z databázy *kataster*, rozšírenie pre topologické vektorové dáta, upgrade na vyššiu verziu PostGIS, pridanie vlastného súradnicového systému do tabuľky *spatial_ref_sys*, napr. 5514

```{r, engine='sql', count_lines}
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
\q
```
```{r, engine='sh', count_lines}
$ wget http://epsg.io/5514.sql
$ psql -f 5514.sql kataster
```

* spustenie skriptu *kt-vytvor_db*, ktorý vytvorí schému *kataster*; pridanie dát z `*.sql` súborov `popisne_udaje.sql` a `graficke_udaje.sql`

```{r, engine='sh', count_lines}
$ psql kataster;
$ kt-vytvor_db | psql kataster
$ PGOPTIONS="-c search_path=kataster,public" psql kataster -f <hlavny-adresar>/sql/popisne_udaje.sql
$ PGOPTIONS="-c search_path=kataster,public" psql kataster -f <hlavny-adresar>/sql/graficke_udaje.sql
```

* testovanie importu z hľadiska vzájomného prepojenia grafických a popisných údajov pomocou SQL skriptu `katastertools/sql/test-import.sql`
```{r, engine='sh', count_lines}
$ PGOPTIONS="-c search_path=kataster,public" psql kataster -f katastertools/sql/test-import.sql
```

* ukončenie, vymazanie schémy *kataster*

```{r, engine='sql', count_lines}
$ psql kataster
drop schema kataster cascade;
\q
```
