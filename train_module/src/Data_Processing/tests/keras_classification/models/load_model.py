from .base_model import BaseModel


class LoadModel(BaseModel):

    def __init__(self, *args, **kwargs):
        super(LoadModel, self).__init__(*args, **kwargs)

    def _create(self):
        print("loading model...")


def inst_class(*args, **kwargs):
    return LoadModel(*args, **kwargs)
