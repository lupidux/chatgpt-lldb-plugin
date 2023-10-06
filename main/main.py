from os import path

def main():
    lldbinit_path = path.expanduser("~/.lldbinit")
    plugin_commands_path = path.join(path.dirname(path.abspath(path.realpath(__file__))),"commands.py")
    print(plugin_commands_path)

    import_line = f"command script import {plugin_commands_path}"

    if path.exists(lldbinit_path):
        with open(lldbinit_path, "r") as f:
            contenuto = f.read()
            already_present = import_line in contenuto
        if not already_present:
            with open(lldbinit_path, "a") as f:
                f.write(import_line + "\n")

    elif not path.exists(lldbinit_path):
        with open(lldbinit_path, "w") as file:
            file.write(import_line + "\n")
