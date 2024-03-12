class Vector():
    def __init__(self, *args) -> None:
        self.values = list(args)
    @property
    def x(self):
        return self.values[0]
    @x.setter
    def x(self, value:float):
        self.values[0] = value
    @property
    def y(self):
        return self.values[1]
    @y.setter
    def y(self, value:float):
        self.values[1] = value
    @property
    def z(self):
        return self.values[2]
    @z.setter
    def z(self, value:float):
        self.values[2] = value
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return self.__class__(*tuple(value*other for value in self.values))
        else:
            return self.__class__(*tuple(value*other_value for value, other_value in zip(self.values, other.values)))
        
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return self.__class__(*tuple(value/other for value in self.values))
        else:
            return self.__class__(*tuple(value/other_value for value, other_value in zip(self.values, other.values)))
            
    def __floordiv__(self, other):
        if isinstance(other, (int, float)):
            return self.__class__(*tuple(value//other for value in self.values))
        else:
            return self.__class__(*tuple(value//other_value for value, other_value in zip(self.values, other.values)))

    def __add__(self, other):
        return self.__class__(*tuple(value+other_value for value, other_value in zip(self.values, other.values)))
    def __sub__(self, other):
        return self.__class__(*tuple(value-other_value for value, other_value in zip(self.values, other.values)))

class Queue():
    def __init__(self, *args) -> None:
        self.__values = dict(enumerate(args))
        self.__head = 0
        self.__tail = 0
    @property
    def has_values(self):
        return bool(self.__values)
    
    def pop(self):
        self.__head += 1
        return self.__values.pop(self.__head-1)
    
    def push(self, value):
        self.__values[self.__tail] = value
        self.__tail += 1