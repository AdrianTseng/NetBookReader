import os

__SECRET_FILENAME = "secret.txt"

secret_content = open(__SECRET_FILENAME).readlines() if os.path.exists(__SECRET_FILENAME) else None

# CSRF
CSRF_ENABLED = True
SECRET_KEY = os.urandom(24)

# DataBase
SQLALCHEMY_DATABASE_URI = secret_content[0] if secret_content is not None \
    else 'postgres://user:password@localhost/Database'
SQLALCHEMY_TRACK_MODIFICATIONS = False


# 安全相关配置，token-authorization 的周期与 bcryption 加密密码的迭代次数
SECURITY = {
    'expiration': 24, # 一天的过期时间 24 * 60 * 60
    'iterations': 10
}
