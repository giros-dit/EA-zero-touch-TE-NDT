import os
def main():
    os.system('kubectl delete -f ./converted')
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