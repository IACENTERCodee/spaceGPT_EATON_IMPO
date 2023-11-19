import sqlite3

# Conectar a la base de datos SQLite (esto creará el archivo de base de datos si no existe)
conn = sqlite3.connect('data.db')

# Crear un objeto cursor para ejecutar comandos SQL
cursor = conn.cursor()

# Crear tabla Invoice
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Invoice (
        InvoiceNumber VARCHAR(255) PRIMARY KEY,
        InvoiceDate VARCHAR(255),
        CountryOfOrigin VARCHAR(255),
        Supplier VARCHAR(255)
    )
''')

# Crear tabla Item
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Item (
        ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
        InvoiceNumber VARCHAR(255),
        PartNumber VARCHAR(255),
        Description TEXT,
        Quantity INTEGER,
        UnitOfMeasure VARCHAR(100),
        Cost DECIMAL(10, 2),
        Weight DECIMAL(10, 2),
        FOREIGN KEY (InvoiceNumber) REFERENCES Invoice(InvoiceNumber)
    )
''')

# Guardar (commit) los cambios y cerrar la conexión a la base de datos
conn.commit()
conn.close()
