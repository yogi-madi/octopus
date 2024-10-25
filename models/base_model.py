class BaseModel:
    _db = None

    @classmethod
    def set_db(cls, db):
        cls._db = db

    @classmethod
    def create_table(cls):
        fields = ', '.join([f"{name} {type_}" for name, type_ in cls._fields.items()])
        query = f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()} ({fields})"
        cls._db.execute(query)

    @classmethod
    def alter_table(cls):
        """
        Alters a table by modifying the data types of specified columns
        and dropping fields that are not present in the provided dictionary.

        :param db: Database instance
        :param table_name: Name of the table to alter
        :param fields: Dictionary where keys are column names and values are new data types
        """
        db = cls._db
        table_name = cls.__name__.lower()
        fields = cls._fields#', '.join([f"{name} {type_}" for name, type_ in cls._fields.items()])
        # Step 1: Get the existing fields in the table
        existing_fields_query = f"SHOW COLUMNS FROM {table_name};"
        existing_fields = db.execute_query(existing_fields_query)

        import pdb
        pdb.set_trace()

        # existing_fields = {row[0]: row[1] for row in cursor.fetchall()}  # Dictionary of existing fields

        # Step 2: Determine which fields to drop
        fields_to_drop = set(existing_fields.keys()) - set(fields.keys())  # Fields not in the dictionary

        # Step 3: Prepare ALTER TABLE commands
        alter_commands = []
        
        # Modify fields
        for column, new_type in fields.items():
            if column in existing_fields:
                if existing_fields[column] != new_type:  # Change type only if different
                    alter_commands.append(f"MODIFY {column} {new_type}")
            else:
                alter_commands.append(f"ADD {column} {new_type}")  # Add new columns if they don't exist

        # Drop missing fields
        for field in fields_to_drop:
            alter_commands.append(f"DROP COLUMN {field}")

        # Step 4: Construct the final ALTER TABLE command
        if alter_commands:
            alter_statement = f"ALTER TABLE {table_name} " + ", ".join(alter_commands)
            
            # Step 5: Execute the command
            try:
                db.execute(alter_statement)
                print(f"Altered table '{table_name}' successfully.")
            except Exception as ex:
                print(f"Error executing alter command: {ex}")
        else:
            print("No changes needed for the table.")


    @classmethod
    def insert(cls, **kwargs):
        keys = ', '.join(kwargs.keys())
        values = tuple(kwargs.values())
        placeholders = ', '.join(['%s'] * len(values))  # For MySQL
        query = f"INSERT INTO {cls.__name__.lower()} ({keys}) VALUES ({placeholders})"
        cls._db.execute(query, values)


    @classmethod
    def all(cls):
        query = f"SELECT * FROM {cls.__name__.lower()}"
        results = cls._db.execute_query(query)
        # results = cursor.fetchall()
        return results
        return [cls(**dict(zip(cls._fields.keys(), result))) for result in results]

    @classmethod
    def find_by_id(cls, id_):
        query = f"SELECT * FROM {cls.__name__.lower()} WHERE id = ?"
        cursor = cls._db.execute(query, (id_,))
        result = cursor.fetchone()
        return cls(**dict(zip(cls._fields.keys(), result))) if result else None

    def save(self):
        self.insert(**self.__dict__)
    
    def update(self, **kwargs):
        updates = ', '.join([f"{k} = ?" for k in kwargs])
        values = tuple(kwargs.values()) + (self.id,)
        query = f"UPDATE {self.__class__.__name__.lower()} SET {updates} WHERE id = ?"
        self._db.execute(query, values)
    
    def delete(self):
        query = f"DELETE FROM {self.__class__.__name__.lower()} WHERE id = ?"
        self._db.execute(query, (self.id,))
