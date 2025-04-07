import subprocess

def run_command(command):
    """Runs a shell command and prints output."""
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"Command '{command}' executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running '{command}': {e}")

if __name__ == "__main__":
    # Collect static files
    run_command("python manage.py collectstatic --noinput")

    # Run migrations
    run_command("gunicorn --bind 0.0.0.0:8000 jruconnect.wsgi:application")
