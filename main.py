from datetime import datetime, timedelta
import subprocess
import os

# Import venv dependencies
import yaml
from notion_client import Client

# Path to the log file for script execution
script_log_file = "birthday_script_log.txt"


def log_message(message):
    with open(script_log_file, 'a') as f:
        f.write(f"{datetime.now()}: {message}\n")


try:
    log_message("Script started")

    # Load the configuration from config.yaml
    with open("config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)

    # Initialize the Notion client with the integration token from config.yaml
    notion = Client(auth=config["notion_token"])

    # Get today's date
    today = datetime.now()

    # Path to the log file
    date_file = "birthday_date_log.txt"


    # Function to get the filtered rows from the database
    def get_filtered_rows(database_id, filter_column, filter_value):
        # Define the filter
        filter_criteria = {
            "property": filter_column,
            "date": {
                "equals": filter_value
            }
        }

        # Query the database with the filter
        results = notion.databases.query(
            **{
                "database_id": database_id,
                "filter": filter_criteria
            }
        )

        return results["results"]


    # Function to call the x-callback-url
    def call_x_callback_url(date_iso, names):
        # Format the checklist items
        checklist_items = "%0A".join(names)

        # Construct the URL
        url = f"things:///add?title=Make%20birthday%20wishes%20{date_iso}&checklist-items={checklist_items}&when={date_iso}"

        # Open the URL using the default handler
        subprocess.run(["open", url], check=True)


    # Function to log the run
    def log_run(date_iso):
        with open(date_file, 'a') as f:
            f.write(f"{date_iso}\n")


    # Function to check if the date is already logged
    def is_logged(date_iso):
        if not os.path.exists(date_file):
            return False
        with open(date_file, 'r') as f:
            logs = f.readlines()
        return f"{date_iso}\n" in logs


    # Main function
    if __name__ == "__main__":
        for i in range(1, 8):  # Loop from Tuesday to Monday
            future_date = today + timedelta(days=i)
            future_date_iso = future_date.date().isoformat()

            # Check if the date is already logged
            if is_logged(future_date_iso):
                print(f"Already processed birthdays for {future_date_iso}")
                continue

            # Get the filtered rows
            rows = get_filtered_rows(config["database_id"], filter_column="Birthday Reminder",
                                     filter_value=future_date_iso)

            # Collect names
            names = [row['properties']['Name']['title'][0]['plain_text'] for row in rows]

            # Replace spaces with %20
            names = [name.replace(' ', '%20') for name in names]

            try:
                if names:
                    # Call x-callback-url with the collected names and the date
                    call_x_callback_url(future_date_iso, names)
                    print(f"Called x-callback-url for {future_date_iso}")
                else:
                    print(f"No birthdays on {future_date_iso}")
                # Log the run only if the above steps succeed
                log_run(future_date_iso)
            except Exception as e:
                print(f"Failed to process {future_date_iso}: {e}")

    log_message("Script completed")

except Exception as e:
    log_message(f"Script failed with error: {e}")
