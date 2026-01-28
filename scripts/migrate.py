import os
import sys
import subprocess

def run_shell(command):
    print(f">> Running: {command}")
    process = subprocess.run(command, shell=True)
    if process.returncode != 0:
        print(f"!! Error occurred while executing: {command}")
        sys.exit(1)

def main():
    if not os.path.exists("migrations"):
        print("Creating migrations directory...")
        run_shell("alembic init migrations")
        print("!!! PLEASE CONFIGURE migrations/env.py BEFORE CONTINUING !!!")
        return

    message = sys.argv[1] if len(sys.argv) > 1 else "Auto-generated migration"
    print("--- Starting Migration Process ---")
    run_shell(f'alembic revision --autogenerate -m "{message}"')
    run_shell("alembic upgrade head")
    print("--- Migration successfully applied! ---")

if __name__ == "__main__":
    main()