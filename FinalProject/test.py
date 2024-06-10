d = dict()
def f1():
    d["x"] = 1
    ori = d["x"]
    f2(d)
    if ori != d["x"]:
        print("check")
    print(ori, d["x"])

def f2(d):
    d["x"] = 2


f1()