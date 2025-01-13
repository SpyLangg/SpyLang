import SpyLang
def shell():
    while True:
        try:
            text = input("SpyLang > ")
            if text.strip() == "":
                continue

            result, error = SpyLang.run("<program>", text)
            shell = False

            if text[:6] == "launch":
                shell = True
            if text == "depart()":
                shell = False

            if error:
                print(error.as_string())
            elif result and not shell:
                if isinstance(result, list): 
                    print(result[0])
                    if result[0] != "None":
                        print("hello")
                        print(repr(result[0]))
                if hasattr(result, "elements"):
                    for element in result.elements:
                        if element !=None:
                            print(element)
                else: 
                    print(result)

        except KeyboardInterrupt:
            print("\nMission aborted by user.")
            break
