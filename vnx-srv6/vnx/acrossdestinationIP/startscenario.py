import os

def main():
    # Create scenario
    os.system('sudo vnx -f escenario-across-vnx.xml -t')

    while True:
        # Ask the user if they want to stop the scenario and delete the JSON files
        action = input("Enter 'q' to stop and delete JSON files: ").strip().lower()

        if action == 'q':
            os.system('sudo vnx -f escenario-across-vnx.xml -P')
            # Delete the JSON files
            for file in os.listdir('.'):
                if file.endswith('.json'):
                    os.remove(file)
            break
        else:
            print("Unrecognized action. Please try again.")

    # Clear the contents of the script.sh files
    directories = ['./conf/r11', './conf/r12', './conf/r13']
    for directory in directories:
        script_path = os.path.join(directory, 'script.sh')
        if os.path.exists(script_path):
            with open(script_path, 'w') as script_file:
                script_file.write('')

if __name__ == "__main__":
    main()