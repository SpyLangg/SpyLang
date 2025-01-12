
import SpyLang
def shell():
    while True:
        try:
            text = input("SpyLang > ")
            if text.strip() == "":
                continue
            result, error = SpyLang.run("<program>", text)

            if error:
                print(error.as_string())
            elif result is not None:
                if isinstance(result, SpyLang.List):
                    for element in result.elements:
                        print(element)
                else:
                    print(result)
        except KeyboardInterrupt:
            print("\nMission aborted by user.")
            break
