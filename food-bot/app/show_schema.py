from sqlalchemy import inspect
from app.database import engine

def print_schema():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    print("=" * 80)
    print("FOOD BOT DATABASE SCHEMA (DATABASE STRUCTURE)")
    print("=" * 80)

    for table_name in table_names:
        print(f"\nTABLE: {table_name.upper()}")
        print("-" * 80)
        print(f"  {'Column Name':<20} | {'Data Type':<15} | {'Primary Key':<12} | {'Nullable':<10}")
        print("  " + "-" * 70)
        columns = inspector.get_columns(table_name)
        pk_cols = inspector.get_pk_constraint(table_name).get("constrained_columns", [])
        for col in columns:
            c_name = col["name"]
            c_type = str(col["type"])
            is_pk = "Yes" if c_name in pk_cols else "No"
            is_null = "Yes" if col["nullable"] else "No"
            print(f"  {c_name:<20} | {c_type:<15} | {is_pk:<12} | {is_null:<10}")

        fks = inspector.get_foreign_keys(table_name)
        if fks:
            print("  Foreign Keys:")
            for fk in fks:
                print(f"   - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

if __name__ == "__main__":
    print_schema()
