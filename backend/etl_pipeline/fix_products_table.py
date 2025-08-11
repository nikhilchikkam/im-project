#!/usr/bin/env python3
"""
Script to fix the products table schema by adding missing columns
"""

import os
import sys
import subprocess
from pathlib import Path

def run_sql_script(sql_file_path, database_url):
    """Run a SQL script using psql command line tool"""
    try:
        # Extract connection details from DATABASE_URL
        # Format: postgresql://username:password@host:port/database
        if database_url.startswith('postgresql://'):
            # Remove postgresql:// prefix
            connection_string = database_url[12:]
            
            # Split into user_pass and host_port_db
            if '@' in connection_string:
                user_pass, host_port_db = connection_string.split('@', 1)
                username, password = user_pass.split(':', 1)
                host_port, database = host_port_db.rsplit('/', 1)
                
                if ':' in host_port:
                    host, port = host_port.split(':', 1)
                else:
                    host = host_port
                    port = '5432'
                
                # Build psql command
                psql_cmd = [
                    'psql',
                    '-h', host,
                    '-p', port,
                    '-U', username,
                    '-d', database,
                    '-f', sql_file_path
                ]
                
                # Set password environment variable
                env = os.environ.copy()
                env['PGPASSWORD'] = password
                
                print(f"Running SQL script: {sql_file_path}")
                print(f"Host: {host}, Port: {port}, Database: {database}")
                
                result = subprocess.run(
                    psql_cmd,
                    env=env,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print("✅ SQL script executed successfully!")
                    if result.stdout:
                        print("Output:")
                        print(result.stdout)
                else:
                    print("❌ SQL script failed!")
                    if result.stderr:
                        print("Error:")
                        print(result.stderr)
                    if result.stdout:
                        print("Output:")
                        print(result.stdout)
                        
            else:
                print("❌ Invalid DATABASE_URL format")
                return False
                
        else:
            print("❌ DATABASE_URL must start with 'postgresql://'")
            return False
            
    except Exception as e:
        print(f"❌ Error running SQL script: {e}")
        return False
    
    return result.returncode == 0

def main():
    """Main function"""
    # Load environment variables
    env_file = Path("../.env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        print("Please check your .env file")
        return False
    
    sql_file = Path("fix_products_table.sql")
    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        return False
    
    print("🔧 Fixing products table schema...")
    success = run_sql_script(str(sql_file), database_url)
    
    if success:
        print("\n🎉 Products table schema has been fixed!")
        print("You can now run the ETL pipeline again.")
    else:
        print("\n❌ Failed to fix products table schema.")
        print("Please check the error messages above.")
    
    return success

if __name__ == "__main__":
    main() 