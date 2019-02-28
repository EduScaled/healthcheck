import os


class Settings:
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    SENTRY_ENVIRONMENT = os.getenv('SENTRY_ENVIRONMENT')

    UNTI_ID = os.getenv('UNTI_ID')
    LRS_SERVER_URL = os.getenv('LRS_SERVER_URL')
    LRS_AUTH = os.getenv('LRS_AUTH')
    LRS_CULTURE_VALUE = os.getenv('LRS_CULTURE_VALUE')

    KAFKA_SERVER = os.getenv('KAFKA_SERVER')

    FS_SERVER_URL = os.getenv('FS_SERVER_URL')
    FS_SERVER_TOKEN = os.getenv('FS_SERVER_TOKEN')

    DP_SERVER_URL = os.getenv('DP_SERVER_URL')
    DP_SERVER_TOKEN = os.getenv('DP_SERVER_TOKEN')


settings = Settings()

