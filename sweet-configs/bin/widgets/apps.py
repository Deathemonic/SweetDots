from gi.repository import Gio, GObject


class App(GObject.Object):
    def __init__(self) -> None:
        super().__init__()

    def fetch_data(self):
        app_data = list(Gio.AppInfo.get_all())

        return {
            (
                'name': app.get_name(),
                'desc': app.get_description(),
                'exec': app.get_id(),
            )
            for app in app_data
        }


print(App().fetch_data())
