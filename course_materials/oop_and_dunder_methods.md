OOP & Dunder Methods
=====================

This text file explains the basic concepts of **Object-Oriented Programming (OOP)** in Python and introduces the most common **dunder (double underscore)** methods: `__init__` and `__str__`. It also covers basic **inheritance** with examples.

------------------------------------------------------------

1. OBJECT-ORIENTED PROGRAMMING (OOP)
------------------------------------

OOP is a programming paradigm that organizes code into **classes** and **objects**.

- **Class**: A blueprint for creating objects.
- **Object**: An instance of a class.
- **Attributes**: Variables that belong to an object.
- **Methods**: Functions defined inside a class that operate on its data.

Example:

```python
class Car:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def start_engine(self):
        print(f"{self.brand} {self.model}'s engine started!")

# Creating an object
car1 = Car("Toyota", "Fortuner")
car1.start_engine()
```

Output:
```
Toyota Fortuner's engine started!
```

------------------------------------------------------------

2. THE `__init__` METHOD
------------------------

`__init__` is a **constructor** method — it runs automatically when a new object is created.
It is used to initialize object attributes.

Syntax:
```python
def __init__(self, parameters):
    # initialization code
```

Example:
```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

s1 = Student("Aviral", 21)
print(s1.name, s1.age)
```

Output:
```
Aviral 21
```

------------------------------------------------------------

3. THE `__str__` METHOD
-----------------------

`__str__` defines how an object is represented as a **string** when printed.

If you print an object without defining `__str__`, you get something like `<__main__.Car object at 0x00000123>`.

By overriding `__str__`, you can customize this.

Example:
```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"Student(Name: {self.name}, Age: {self.age})"

s1 = Student("Aviral", 21)
print(s1)
```

Output:
```
Student(Name: Aviral, Age: 21)
```

------------------------------------------------------------

4. BASIC INHERITANCE
--------------------

**Inheritance** allows one class to use the properties and methods of another.

- The class being inherited from is called the **Parent (Base)** class.
- The class that inherits is called the **Child (Derived)** class.

Example:
```python
class Animal:
    def __init__(self, species):
        self.species = species

    def speak(self):
        print(f"A {self.species} makes a sound.")

class Dog(Animal):
    def __init__(self, species, name):
        super().__init__(species)  # Call parent class constructor
        self.name = name

    def speak(self):
        print(f"{self.name} barks!")

# Create objects
animal1 = Animal("Generic Animal")
animal1.speak()

dog1 = Dog("Dog", "Buddy")
dog1.speak()
```

Output:
```
A Generic Animal makes a sound.
Buddy barks!
```

------------------------------------------------------------

5. KEY POINTS SUMMARY
---------------------

- `__init__`: Initializes object attributes when created.
- `__str__`: Defines how the object is displayed as a string.
- `super()`: Calls the parent class constructor or methods.
- Inheritance allows **code reuse** and **extension** of classes.

------------------------------------------------------------

6. QUICK RECAP EXAMPLE
----------------------

```python
class Vehicle:
    def __init__(self, brand):
        self.brand = brand

    def __str__(self):
        return f"Vehicle brand: {self.brand}"

class Car(Vehicle):
    def __init__(self, brand, model):
        super().__init__(brand)
        self.model = model

    def __str__(self):
        return f"Car: {self.brand} {self.model}"

# Test
car = Car("Honda", "Civic")
print(car)
```

Output:
```
Car: Honda Civic
```

------------------------------------------------------------

7. ADDITIONAL DUNDER METHODS (for later learning)
-------------------------------------------------

- `__len__(self)` → defines behavior for `len(obj)`.
- `__add__(self, other)` → defines `obj1 + obj2`.
- `__eq__(self, other)` → defines equality `==`.
- `__repr__(self)` → formal string representation (for developers).

These special methods let you make your objects behave like built-in types.

------------------------------------------------------------

End of file.

