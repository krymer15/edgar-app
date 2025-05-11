# models/adapters

Conversion utilities to translate between dataclass instances and ORM models:

- **dataclass_to_orm.py**  
  Functions that take dataclass objects (e.g. `ParsedDocument`) and return ORM instances ready to write.
- **orm_to_dataclass.py**  
  Functions that load ORM rows and produce pure dataclass objects for use in business logic.