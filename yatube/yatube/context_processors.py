import datetime as dt


def yatube(request):
    return {
        'year': dt.datetime.today().year
    }