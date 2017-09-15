from urllib.request import urlopen


def GetWebpage(url, output="s"):
    response = urlopen('http://python.org/')
    if (output == "s"):
        # response.read() returns a bytes-like object so use .decode() to
        # convert to a unicode string
        html = response.read().decode("utf-8")
    if (output == "b"):
        # default return of bytes-like object
        html = response.read()

    return html
