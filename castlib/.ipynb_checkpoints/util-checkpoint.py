def format_currency(num):
    return "${:,.0f}".format(num)

def format_percent(num):
    return "{:,.2f}%".format(num*100)

def format_number(num):
    return "{:,.2f}".format(num)