"""
Generates database/seed_data.sql containing all 55 stations, 48 trains, 206 train stops,
84 routes, 192 coaches, and 3072 seats, plus baseline demo users.
"""
import os
import mysql.connector

def export_seed_data():
    conn = mysql.connector.connect(host='127.0.0.1', user='root', database='railsync_db')
    cur = conn.cursor(dictionary=True)
    
    out_path = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'seed_data.sql')
    out_path = os.path.abspath(out_path)
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("-- RailSync Complete Seed Dataset\n")
        f.write("-- Auto-generated from active database schema and expansion\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
        
        tables_to_dump = ['users', 'stations', 'trains', 'train_stops', 'routes', 'coaches', 'seats']
        
        for table in tables_to_dump:
            cur.execute(f"SELECT * FROM {table}")
            rows = cur.fetchall()
            if not rows:
                continue
                
            f.write(f"-- Table: {table} ({len(rows)} rows)\n")
            f.write(f"DELETE FROM {table};\n")
            
            columns = list(rows[0].keys())
            cols_str = ", ".join([f"`{c}`" for c in columns])
            
            batch_size = 100
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                values_clauses = []
                for r in batch:
                    vals = []
                    for c in columns:
                        v = r[c]
                        if v is None:
                            vals.append("NULL")
                        elif isinstance(v, (int, float)):
                            vals.append(str(v))
                        else:
                            # String or date/time
                            escaped = str(v).replace("\\", "\\\\").replace("'", "\\'")
                            vals.append(f"'{escaped}'")
                    values_clauses.append(f"({', '.join(vals)})")
                
                insert_stmt = f"INSERT INTO `{table}` ({cols_str}) VALUES\n  " + ",\n  ".join(values_clauses) + ";\n"
                f.write(insert_stmt)
            f.write("\n")
            
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
        
    print(f"Successfully generated {out_path} with {len(tables_to_dump)} tables.")

if __name__ == '__main__':
    export_seed_data()
