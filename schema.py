import sqlite3 as sql
from paths import DB_PATH

conn = sql.connect(DB_PATH)
cur = conn.cursor()




cur.execute("""CREATE TABLE IF NOT EXISTS pointe_shoes (
                shoe_pk INTEGER PRIMARY KEY,
                bag INTEGER,
                style TEXT,
                us_size INTEGER,
                width TEXT,
                shank TEXT,
                vamp TEXT,
                shape TEXT,
                sole TEXT,
                availability TEXT,
                student TEXT,
                comments TEXT)""")


# when selling, it will need to go from available to reserved to sold, 
# or reserved to sold to satisfy this trigger and be able to list who it was sold to
# That will need to be hardcoded.
# When setting to null, it will need to be marked available
cur.execute("""CREATE TRIGGER IF NOT EXISTS reserve_trigger
AFTER UPDATE OF student ON pointe_shoes WHEN NEW.student IS NOT NULL
BEGIN UPDATE pointe_shoes SET availability = 'Reserved' WHERE shoe_pk = NEW.shoe_pk; END;""")

cur.execute("""CREATE TRIGGER IF NOT EXISTS imported_reserved 
AFTER INSERT ON pointe_shoes WHEN NEW.student IS NOT NULL AND NEW.availability IS NOT 'Sold'
BEGIN UPDATE pointe_shoes SET availability = 'Reserved' WHERE shoe_pk = NEW.shoe_pk; END;""")


conn.commit()



