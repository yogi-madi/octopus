class Field:
    def __init__(self, null=True, unique=False, primary_key=False):
        self.primary_key = primary_key
        if primary_key:
            self.null = False
        else:
            self.null = null
        self.unique = unique

class Integer(Field):
    _py_data_type = int

    def __init__(self, null=True, unique=False, primary_key=False, auto_increment=False):
        self.auto_increment = auto_increment
        self.field_type = "INT"
        super().__init__(null, unique, primary_key)


class Float(Field):
    _py_data_type = float

    def __init__(self, null=True, unique=False, precision=None):
        self.precision = precision
        self.field_type = f"FLOAT({self.precision})" if self.precision else "FLOAT"
        super().__init__(null, unique)


class String(Field):
    def __init__(self, null=True, unique=False, primary_key=False, max_len=255, possible_values=None):
        self.max_len = max_len
        self.possible_values = possible_values or []
        self.field_type = f"VARCHAR({self.max_len})"
        if self.possible_values:
            enum_values = ','.join([f"'{v}'".upper() for v in self.possible_values])
            self.field_type = f"ENUM({enum_values})"
        super().__init__(null, unique, primary_key)



class Text(Field):
    
    def __init__(self, null=True, unique=False):
        self.field_type = "TEXT"
        super().__init__(null, unique)



class Boolean(Field):
    def __init__(self):
        self.field_type = "TINYINT(1)"
        super().__init__(null=True, unique=False, primary_key=False)


class Date(Field):
    def __init__(self,null=True):
        self.field_type = "DATE"
        super().__init__(null)


class DateTime(Field):
    def __init__(self,null=True):
        self.field_type = "DATETIME"
        super().__init__(null)


class Time(Field):
    def __init__(self,null=True):
        self.field_type = "TIME"
        super().__init__(null)


class UUID(Field):
    def __init__(self, max_len=36,null=True, unique=False, primary_key=False):
        self.field_type = f"CHAR({max_len})"
        super().__init__(null, unique, primary_key)


class JSON(Field):

    def __init__(self,null=True):
        self.field_type = "JSON"
        super().__init__(null)


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