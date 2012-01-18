from django.dispatch import Signal

class_prepared = Signal(providing_args=["class"])

pre_init = Signal(providing_args=["instance", "kwargs"])
post_init = Signal(providing_args=["instance"])

pre_save = Signal(providing_args=["instance"])
post_save = Signal(providing_args=["instance"])

pre_delete = Signal(providing_args=["instance"])
post_delete = Signal(providing_args=["instance"])

