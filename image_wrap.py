import imgkit

#Pasar como argumento imageName: str nombre de la imagen
def setup(imageName: str):
    # Escribe en 'data_base.txt' la imagen en formato HTML  
    toDataBase = '<img src="' + imageName + '">'
    with open('images/data_base.txt', 'a') as x: 
        x.write(toDataBase)

def wrap():
    # Guarda en read_data todo la informacion de 'data_base'
    with open('images/data_base.txt') as r:
        read_data = r.read()

    # Escribe en 'wrapper.html' las imagenes
    with open('images/wrapper.html', 'w') as f:
        f.write('<meta content="text/html; charset=utf-8" http-equiv="Content-type"><meta content="jpg" name="imgkit-format"><body>\n'+ read_data + '</body>')

    # Escribir direccion de las imagenes
    options = {
        'allow': 'images/champion/'
    }
    # Convierte el HTML en JPG
    imgkit.from_file('images/wrapper.html', 'images/wrapped.jpg', options)

    #Limpia 'data_base.txt' y 'wrapper.html'
    with open('images/wrapper.html','w') as file: file.write('')
    with open('images/data_base.txt','w') as file: file.write('')