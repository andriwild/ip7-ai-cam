from observer.Subject import Subject, Observer

class Configuration(Subject):
    def __init__(self):
        self._camera = None
        self._observers = []

    def get_camera(self):
        return self._camera

    def set_camera(self, value):
        print("Configuration: set_camera")
        self._camera = value
        self.notify()

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        print("Configuration: notify")
        for observer in self._observers:
            observer.update(self)


