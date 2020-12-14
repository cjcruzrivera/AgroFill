[![Python](https://img.shields.io/badge/python-3.5%2C%203.6%2C%203.7-blue.svg)]()

# AgroFill

La siguiente aplicación se desarrollo para el proyecto final del curso `Diseño de Interfaces de Usuarios` de la `Universidad del Valle`

Sistema de apoyo en el diseño de estructuras hidraulicas. 

## Instalación

Instalar [virtualenv](hhttps://docs.python.org/3/library/venv.html) y ejecutarlo:

```shell
$ python3 -m venv venv_name
$ source venv_name/bin/activate

#deactivate para apagar el ambiente
```

A continuación, instalar los requerimientos:

```shell
(venv_name)$ pip install -r requirements.txt
```

Posteriormente configurar los valores FLASK_APP y FLASK_DEBUG:

```shell
(venv_name)$ export FLASK_APP=project
(venv_name)$ export FLASK_DEBUG=1
```
y por último ejecutar la aplicación:

```shell
(venv_name)$ flask run
```

Ir a [http://localhost:5000](http://localhost:5000)

