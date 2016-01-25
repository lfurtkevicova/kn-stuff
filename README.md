Ide o nástroj na konverziu a import grafických a popisných katastrálnych dát Slovenskej republiky do GIS.

### Nasadenie
Vytvorenie Python *virtualenv* (virtuálne prostredie v podobe fyzického adresára, ktorý obsahuje unix-ovú štruktúru s binárkami, atď.)

```
$ virtualenv --system-site-packages $HOME/venvs/kataster-import
$ source $HOME/venvs/kataster-import/bin/activate
```

Inštalácia pomocou *setup.py*

```
$ git clone https://github.com/imincik/kataster-import.git
$ cd kataster-import
$ python ./setup.py install
$ pip install -r requirements.txt
````

bez inštalácie

```
$ git clone https://github.com/imincik/kataster-import.git
$ cd kataster-import
$ pip install -r requirements.txt
$ source ./env-setup.sh
```

### Požiadavky

Uloženie vstupných dát
 
 * hlavný adresár
   * adresár `vgi`                    - grafické dáta KN
   * adresár `dbf`, `fpu` alebo `fpt` - popisné dáta KN

### Použitie

#### Konverzia všetkých dát

*kt-sql* - skript slúži ako wrapper nad ostatnými špecializovanými nástrojmi a umožňuje vykonať konverziu SGI a SPI v jednom kroku. 

```
$ kt-sql <hlavny-adresar>
```

#### Import dát do PostGIS
Dáta získané konverziou je možné importovať do PostGIS z vytvorených SQL súborov - adresár *<hlavny-adresar>/sql*. Predpokladá sa, že už existuje **user**, napr. *ludka*, t.j. rovnako ako názov PC.

* prihlásenie do databázy *postgres*, výpis zoznamu databáz a vytvorenie databázy *kataster*, prepnutie sa do novej databázy

```
$ psql postgres
$ \l
$ createdb kataster;
$ \connect kataster;
```

* vytvorenie geodatabázy z databázy *kataster*, rozšírenie pre topologické vektorové dáta, upgrade na vyššiu verziu PostGIS, pridanie vlastného súradnicového systému do tabuľky *spatial_ref_sys*, napr. 5514

```
$ CREATE EXTENSION postgis;
$ CREATE EXTENSION postgis_topology;
$ \q
$ wget http://epsg.io/5514.sql
$ psql -f 5514.sql kataster
```

* spustenie skriptu *kt-vytvor_db*, ktorý vytvorí schému *kataster*; pridanie dát z `*.sql` súborov `popisne_udaje.sql` a `graficke_udaje.sql`

```
$ psql kataster;
$ kt-vytvor_db | psql kataster
$ PGOPTIONS="-c search_path=kataster,public" psql kataster -f <hlavny-adresar>/sql/popisne_udaje.sql
$ PGOPTIONS="-c search_path=kataster,public" psql kataster -f <hlavny-adresar>/sql/graficke_udaje.sql
```

* testovanie importu z hľadiska vzájomného prepojenia grafických a popisných údajov pomocou SQL skriptu `katastertools/sql/test-import.sql`
```
$ PGOPTIONS="-c search_path=kataster,public" psql kataster -f katastertools/sql/test-import.sql
```

* ukončenie, vymazanie schémy *kataster*

```
psql kataster
drop schema kataster cascade;
\q
```

### Popis dát

* grafické dáta: 
* popisné dáta: 
