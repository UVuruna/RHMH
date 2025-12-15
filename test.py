import sqlite3

def obrisi_sve_podatke(baza):
    conn = sqlite3.connect(baza)
    cursor = conn.cursor()

    # Dobijanje svih tabela iz baze
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabele = cursor.fetchall()

    for tabela in tabele:
        print(tabela)
        ime_tabele = tabela[0]
        if ime_tabele != "sqlite_sequence":  # Ova tabela čuva AUTO_INCREMENT vrednosti
            cursor.execute(f"DELETE FROM {ime_tabele};")

    conn.commit()
    conn.close()

# Pozivanje funkcije
obrisi_sve_podatke("LOGS.db")

def optimizuj_bazu(baza):
    conn = sqlite3.connect(baza)
    cursor = conn.cursor()
    cursor.execute("VACUUM;")
    conn.commit()
    conn.close()

# Pozivanje funkcije
optimizuj_bazu("LOGS.db")

