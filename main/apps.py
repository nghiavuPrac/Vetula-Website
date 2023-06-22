from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'main'

    def ready(self):
        # import signal handlers
        import main.hooks

# MainConfig.get_model()
