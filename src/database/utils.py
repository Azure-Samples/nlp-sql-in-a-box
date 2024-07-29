import pyodbc
from faker import Faker


def table_exists(cursor: pyodbc.Cursor) -> int:
    """
    Check whether the ExplorationProduction table exists in the database.
    """
    query = '''
IF (EXISTS (SELECT * 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'ExplorationProduction'))
    SELECT 1 AS res 
ELSE SELECT 0 AS res;
'''

    cursor.execute(query)

    return cursor.fetchone()[0] == 1


def create_table(cursor: pyodbc.Cursor) -> None:
    """
    Create the ExplorationProduction table in the database.
    """
    query = '''
CREATE TABLE ExplorationProduction (
    WellID INT PRIMARY KEY,
    WellName VARCHAR(50),
    Location VARCHAR(100),
    ProductionDate DATE,
    ProductionVolume DECIMAL(10, 2),
    Operator VARCHAR(50),
    FieldName VARCHAR(50),
    Reservoir VARCHAR(50),
    Depth DECIMAL(10, 2),
    APIGravity DECIMAL(5, 2),
    WaterCut DECIMAL(5, 2),
    GasOilRatio DECIMAL(10, 2)
);
'''

    cursor.execute(query)


def insert_record(cursor: pyodbc.Cursor, i: int, fake: Faker) -> None:
    """
    Insert a fake record into the ExplorationProduction table.g
    """
    well_id = i + 1
    well_name = fake.word() + ' Well'
    location = fake.city() + ', ' + fake.country()
    production_date = fake.date_between(start_date='-1y', end_date='today')
    production_volume = fake.pydecimal(left_digits=6, right_digits=2, positive=True)
    operator = fake.company()
    field_name = fake.word() + ' Field'
    reservoir = fake.word() + ' Reservoir'
    depth = fake.pydecimal(left_digits=5, right_digits=2, positive=True)
    api_gravity = fake.pydecimal(left_digits=2, right_digits=2, positive=True)
    water_cut = fake.pydecimal(left_digits=2, right_digits=2)
    gas_oil_ratio = fake.pydecimal(left_digits=4, right_digits=2)

    query = '''
INSERT INTO ExplorationProduction (WellID, WellName, Location, ProductionDate, ProductionVolume, Operator, FieldName, Reservoir, Depth, APIGravity, WaterCut, GasOilRatio) 
VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

    # Insert record into the ExplorationProduction table
    cursor.execute(query, well_id,well_name, location, production_date, production_volume, operator, field_name, reservoir, depth, api_gravity, water_cut, gas_oil_ratio)
