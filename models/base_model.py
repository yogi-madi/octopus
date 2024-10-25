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
        fields = ', '.join([f"{name} {type_}" for name, type_ in cls._fields.items()])
        query = f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()} ({fields})"
        cls._db.execute(query)

    @classmethod
    def alter_table(cls):
        """Alters the table structure based on the current model's fields."""
        db = cls._db
        table_name = cls.__name__.lower()
        
        # Step 1: Get existing fields using DESCRIBE command
        existing_fields_query = f"DESCRIBE {table_name};"
        existing_fields = db.execute_query(existing_fields_query)
        
        # Convert existing fields to a dictionary
        existing_fields_dict = {}
        primary_key_exists = False
        existing_primary_key_field = None
        unique_keys = set()  # To track existing unique keys

        for row in existing_fields:
            field_name, field_type, nullability, key_info, default_value, extra_info = row
            field_type = field_type.upper()
            extra_info = extra_info.upper() if type(extra_info) == str else extra_info
            # Track if a primary key or unique key is already defined
            if key_info == "PRI":
                primary_key_exists = True
                existing_primary_key_field = field_name
            if key_info == "UNI":
                unique_keys.add(field_name)

            # Build constraints for the existing field
            constraints = []
            if key_info == "PRI":
                constraints.append("PRIMARY KEY")
            if nullability == "NO":
                constraints.append("NOT NULL")
            if key_info == "UNI":
                constraints.append("UNIQUE")
            
            # Combine type and constraints
            existing_definition = f"{field_type} {' '.join(constraints)}"
            if default_value:
                existing_definition += f" DEFAULT {default_value}"
            if extra_info:
                existing_definition += f" {extra_info}"
            
            existing_fields_dict[field_name] = existing_definition.strip()

        # Step 2: Prepare fields defined in the model
        model_fields = cls.get_properties()
        model_fields_dict = {}
        keys_to_drop = []
        drop_commands = []
        for name, field in model_fields.items():
            constraints = []
            if field.primary_key:
                if primary_key_exists and name != existing_primary_key_field:
                    keys_to_drop.append(f"DROP PRIMARY KEY")
                if not primary_key_exists:  # Add primary key if not exists
                    constraints.append("PRIMARY KEY")
                primary_key_exists = True  # Prevent additional primary keys
            if not field.null:
                constraints.append("NOT NULL")
            if field.unique:
                constraints.append("UNIQUE")

            field_definition = field.create_db_format()
            model_fields_dict[name] = field_definition.strip()

        # Step 3: Determine which fields to drop
        fields_to_drop = set(existing_fields_dict.keys()) - set(model_fields_dict.keys())

        # Step 4: Prepare ALTER TABLE commands
        add_commands = []
        modify_commands = []

        # Drop columns that are not in the model
        for field in fields_to_drop:
            drop_commands.append(f"DROP COLUMN {field}")

        # Handle unique keys that are not defined in the model
        for existing_unique in unique_keys:
            if existing_unique not in model_fields_dict:
                keys_to_drop.append(f"DROP INDEX {existing_unique} ON {table_name}")

        for column, new_definition in model_fields_dict.items():
            if column in existing_fields_dict:
                if existing_fields_dict[column] != new_definition:
                    modify_commands.append(f"MODIFY {column} {new_definition}")
            else:
                add_commands.append(f"ADD {column} {new_definition}")

        alter_commands = drop_commands + modify_commands + add_commands + keys_to_drop

        # Step 5: Execute the ALTER TABLE command if there are changes
        if alter_commands:
            alter_statement = f"ALTER TABLE {table_name} " + ", ".join(alter_commands)
            try:
                pdb.set_trace()
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
