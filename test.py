# __author: Lambert
# __date: 2017/11/13 18:18
setting = {
    "k1": "v1",
    "k2": "v2",
    "k3": "v3"
}


def test(**setting):
    print(setting)


test(**setting)
