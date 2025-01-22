from strings_with_arrow import *
import sys
import Shell
from errors import KeyboardInterruptError
from func.builtin_func import *




def run_file(filename):
    try:
        with open(filename, "r") as file:
            script = file.read()
        
        result, error = run(filename, script)
        if error:
            print(error.as_string())
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except KeyboardInterrupt:
        raise KeyboardInterruptError(details="Operation terminated by the user.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            Shell.shell()

        else:
            run_file(sys.argv[1])
            sys.exit(1)
    except KeyboardInterrupt:
        error = KeyboardInterruptError()
        print(error.as_string())
        sys.exit(1)

