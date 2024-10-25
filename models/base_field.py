class Field:
    def __init__(self, null=False, unique=False, primary_key=False):
        self.null = null
        self.unique = unique
        self.primary_key = primary_key

    def create_db_format(self):
        constraints = []
        if self.primary_key:
            constraints.append("PRIMARY KEY")
        if not self.null:
            constraints.append("NOT NULL")
        if self.unique:
            constraints.append("UNIQUE")
        return " ".join(constraints)


class Integer(Field):
    _py_data_type = int

    def __init__(self, null=False, unique=False, primary_key=False, auto_increment=False):
        self.auto_increment = auto_increment
        super().__init__(null, unique, primary_key)

    def create_db_format(self):
        field_type = "INT"
        constraints = super().create_db_format()
        if self.auto_increment:
            constraints += " AUTO_INCREMENT"
        return f"{field_type} {constraints}".strip()


class Float(Field):
    _py_data_type = float

    def __init__(self, null=False, unique=False, precision=None):
        self.precision = precision
        super().__init__(null, unique)

    def create_db_format(self):
        field_type = f"FLOAT({self.precision})" if self.precision else "FLOAT"
        constraints = super().create_db_format()
        return f"{field_type} {constraints}".strip()


class String(Field):
    def __init__(self, null=False, unique=False, primary_key=False, max_len=255, possible_values=None):
        self.max_len = max_len
        self.possible_values = possible_values or []
        super().__init__(null, unique, primary_key)

    def create_db_format(self):
        field_type = f"VARCHAR({self.max_len})"
        constraints = super().create_db_format()
        if self.possible_values:
            enum_values = ', '.join([f"'{v}'" for v in self.possible_values])
            field_type = f"ENUM({enum_values})"
        return f"{field_type} {constraints}".strip()


class Text(Field):
    def create_db_format(self):
        field_type = "TEXT"
        constraints = super().create_db_format()
        return f"{field_type} {constraints}".strip()


class Boolean(Field):
    def create_db_format(self):
        field_type = "BOOLEAN"
        constraints = super().create_db_format()
        return f"{field_type} {constraints}".strip()


class Date(Field):
    def create_db_format(self):
        field_type = "DATE"
        constraints = super().create_db_format()
        return f"{field_type} {constraints}".strip()


class DateTime(Field):
    def create_db_format(self):
        field_type = "DATETIME"
        constraints = super().create_db_format()
        return f"{field_type} {constraints}".strip()


class Time(Field):
    def create_db_format(self):
        field_type = "TIME"
        constraints = super().create_db_format()
        return f"{field_type} {constraints}".strip()


class UUID(Field):
    def create_db_format(self, max_len=255,null=False, unique=False, primary_key=False):
        field_type = "CHAR(36)"
        constraints = super().create_db_format()
        return f"{field_type} {constraints}".strip()


class JSON(Field):
    def create_db_format(self):
        field_type = "JSON"
        constraints = super().create_db_format()
        return f"{field_type} {constraints}".strip()


VALID_DATA_TYPES = [
    Integer,
    Float,
    String,
    Text,
    Boolean,
    Date,
    DateTime,
    Time,
    UUID,
    JSON
]