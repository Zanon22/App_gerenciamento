import random


def teste():
    valores = '1,2,3,4'
    lista_ids = valores
    while True:
        id_compra = random.randrange(5)
        id_formatado = '{:01d}'.format(id_compra)
        print(id_formatado)
        if id_formatado in lista_ids:
            pass
        else:
            break
    print(id_formatado)
    return id_formatado


def teste2():
    print(id_formatado)
