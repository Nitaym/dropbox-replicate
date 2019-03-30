
def good_units(number):
    units = 'B'
    if number > 1000:
        number /= 1000
        units = 'KB'
    if number > 1000:
        number /= 1000
        units = 'MB'

    return number, units
