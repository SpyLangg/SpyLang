
import SpyLang
def shell():
    while True:
        text=input("SpyLang > ")#name of lang
        if text.strip() == "":continue
        result,error=SpyLang.run("<program>",text)
        shell=False
        if text[:6]=="launch":
            shell=True
        if text=="depart()":
            break
        # print(shell)

        if error:print(error.as_string())

        elif result and shell ==False:     
            print(repr(result[0]))

shell()