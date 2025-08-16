from urllib.parse import quote_plus

SGBD = 'mysql+mysqlconnector'
USUARIO = 'root'
SENHA = quote_plus('r3n@N47943911')
SERVIDOR = 'localhost'
DATABASE = 'FestoChallenge'

SQLALCHEMY_DATABASE_URI = f'{SGBD}://{USUARIO}:{SENHA}@{SERVIDOR}/{DATABASE}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'sousa'
