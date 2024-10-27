from datetime import datetime
from .base_field import VALID_DATA_TYPES
import pdb


class BaseModel:
    _db = None

    @classmethod
    def set_db(cls, db):
        cls._db = db

    @classmethod
    def get_properties(cls):
         class_properties = vars(cls)
         properties = {key: value for key, value in class_properties.items() if not key.startswith('__') and type(value) in VALID_DATA_TYPES}
         return properties

    @classmethod
    def create_table(cls):
        db = cls._db  # Assume `_db` is a reference to the database connection
        table_name = cls.__table__

        # Use get_properties to retrieve model fields and their configurations
        fields = cls.get_properties()

        # Build the CREATE TABLE statement
        field_definitions = []

        for field_name, field in fields.items():
            field_type = field.field_type
            constraints = []

            # Collect constraints
            if field.primary_key:
                constraints.append("PRIMARY KEY")
            if not field.null:
                constraints.append("NOT NULL")
            if field.unique:
                constraints.append("UNIQUE")
            if getattr(field, 'auto_increment', False):
                constraints.append("AUTO_INCREMENT")

            # Combine field type and constraints
            constraints_clause = " ".join(constraints).strip()
            field_definition = f"{field_name} {field_type} {constraints_clause}".strip()
            field_definitions.append(field_definition)


        # Combine field definitions to form the final SQL statement
        create_table_statement = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    "
        create_table_statement += ",\n    ".join(field_definitions)
        create_table_statement += "\n);"

        # Execute the SQL statement to create the table
        try:
            db.execute(create_table_statement)
            cls.log_changes(create_table_statement)
            print(f"Table '{table_name}' created successfully.")
        except Exception as ex:
            print(f"Error creating table '{table_name}': {ex}")


    @classmethod
    def alter_table(cls):
        db = cls._db
        table_name = cls.__table__
        
        # Step 1: Retrieve existing schema information for fields and constraints
        existing_fields_query = f"DESCRIBE {table_name};"
        existing_fields = db.execute_query(existing_fields_query)
        
        existing_fields_dict = {}
        unique_constraints = set()
        primary_key_field = None

        for row in existing_fields:
            field_name, field_type, nullability, key_info, default_value, extra_info = row
            existing_constraints = {
                'type': field_type.upper(),
                'null': nullability == "YES",
                'primary_key': key_info == "PRI",
                'unique': key_info == "UNI",
                'default': default_value,
                'extra': extra_info.upper() if extra_info else ''
            }
            
            if key_info == "PRI":
                primary_key_field = field_name
            if key_info == "UNI":
                unique_constraints.add(field_name)

            existing_fields_dict[field_name] = existing_constraints

        # Step 2: Prepare new field definitions from the model
        model_fields = cls.get_properties()
        new_fields_dict = {}
        for name, field in model_fields.items():
            new_constraints = {
                'type': field.field_type,
                'null': field.null,
                'primary_key': field.primary_key,
                'unique': field.unique,
                'default': getattr(field, 'default', None),
                'extra': 'AUTO_INCREMENT' if getattr(field, 'auto_increment', False) else ''
            }
            new_fields_dict[name] = new_constraints

        # Step 3: Compare existing and new field definitions to generate ALTER commands
        add_commands = []
        modify_commands = []
        drop_commands = []
        index_commands = []
        
        # Identify fields to drop or modify based on model definitions
        for field_name, existing in existing_fields_dict.items():
            if field_name not in new_fields_dict:
                drop_commands.append(f"DROP COLUMN {field_name}")
            else:
                new = new_fields_dict[field_name]
                if existing != new:
                    modify_commands.append(f"MODIFY {field_name} {new['type']}")

                    # Apply additional constraint changes if needed
                    if new['primary_key'] and not existing['primary_key']:
                        index_commands.append(f"ADD PRIMARY KEY ({field_name})")
                    elif existing['primary_key'] and not new['primary_key']:
                        index_commands.append("DROP PRIMARY KEY")
                    
                    if new['unique'] and field_name not in unique_constraints:
                        index_commands.append(f"ADD UNIQUE INDEX {field_name} ({field_name})")
                    elif field_name in unique_constraints and not new['unique']:
                        index_commands.append(f"DROP INDEX {field_name}")

        # Identify new fields to add
        for field_name, new in new_fields_dict.items():
            if field_name not in existing_fields_dict:
                add_definition = f"{new['type']}"
                if new['primary_key']:
                    add_definition += " PRIMARY KEY"
                if new['unique']:
                    add_definition += " UNIQUE"
                if not new['null']:
                    add_definition += " NOT NULL"
                if new['default'] is not None:
                    add_definition += f" DEFAULT {new['default']}"
                if new['extra']:
                    add_definition += f" {new['extra']}"
                add_commands.append(f"ADD COLUMN {field_name} {add_definition}")

        # Step 4: Execute ALTER TABLE commands if needed
        alter_commands = add_commands + modify_commands + drop_commands + index_commands
        if alter_commands:
            alter_statement = f"ALTER TABLE {table_name} " + ", ".join(alter_commands)
            try:
                db.execute(alter_statement)
                cls.log_changes(alter_statement, drop_commands, modify_commands, add_commands)
                print(f"Altered table '{table_name}' successfully.")
            except Exception as ex:
                print(f"Error executing alter command: {ex}")
        else:
            print("No changes needed for the table.")


    @classmethod
    def log_changes(cls, alter_statement, drop_commands, modify_commands, add_commands):
        """Logs the changes to a history file."""
        log_file_path = 'alter_table_history.log'  # Specify your log file path
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create a log entry
        log_entry = f"[{timestamp}] ALTER TABLE Command: {alter_statement}\n"
        if drop_commands:
            log_entry += f"  Dropped Columns: {', '.join(drop_commands)}\n"
        if modify_commands:
            log_entry += f"  Modified Columns: {', '.join(modify_commands)}\n"
        if add_commands:
            log_entry += f"  Added Columns: {', '.join(add_commands)}\n"
        log_entry += "\n"  # Add a newline for readability
        
        # Write to log file
        with open(log_file_path, 'a') as log_file:
            log_file.write(log_entry)

        print(f"Changes logged to {log_file_path}.")



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
        result = cls._db.execute_query(query, (id_,))
        # result = cursor.fetchone()

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
