informatics_name_convert = {
    'Ilya Gorokhov': 'Илья Горохов',
}

def InfromaticsNameConvert(name):
    global informatics_name_convert
    return informatics_name_convert.get(name, name)
