from getpass import getpass

if input("Do you want to create a new config? (Y/n) ").lower().count("n"):
    exit()

with open("configtemplate.json") as f:
    with open("config.json", "w") as g:
        length: int = len(f.readlines())
        f.seek(0)
        for i, line in enumerate(f.readlines()):
            if line.count("{") or line.count("}"):
                g.write(line)
            else:
                one, _ = line.split(": ")
                if one == '    "password"':
                    two: str = '"' + getpass(line + " <= ")
                else:
                    two: str = '"' + input(line + " <= ")
                if i != length - 2:
                    two += '",\n'
                else:
                    two += '"\n'
                g.write(one + ": " + two)
