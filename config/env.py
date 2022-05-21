import environ

BASE_DIR = environ.Path(__file__) - 2

env = environ.Env()
env_file = str(BASE_DIR.path(".env"))
env.read_env(env_file)
