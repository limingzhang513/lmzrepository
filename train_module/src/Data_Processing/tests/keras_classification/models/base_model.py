import time
import cv2
import glob
from keras.callbacks import EarlyStopping, ModelCheckpoint, LearningRateScheduler, ReduceLROnPlateau
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
from keras.preprocessing.image import ImageDataGenerator
from keras.layers import Input
from keras.optimizers import Adam, SGD
from keras.models import load_model
import numpy as np
from sklearn.externals import joblib

from .. import config
from .. import util
import math


class BaseModel(object):
    def __init__(self,
                 model_path=None,
                 class_weight=None,
                 nb_epoch=1000,
                 batch_size=32,
                 freeze_layers_number=None):
        self.model = None
        self.model_path = model_path
        self.class_weight = class_weight
        self.nb_epoch = nb_epoch
        self.fine_tuning_patience = 20
        self.batch_size = batch_size
        self.freeze_layers_number = freeze_layers_number
        # self.img_size = (50, 50)
        self.img_size = config.img_size

    def _create(self):
        raise NotImplementedError('subclasses must override _create()')

    def _fine_tuning(self):
        if self.model_path is not None:
            self.model = load_model(self.model_path)
        self.freeze_top_layers()
        self.model.compile(
            loss='categorical_crossentropy',
            optimizer=[SGD(lr=1e-2) if config.optimizer == 0 else Adam(lr=1e-2)][0],
            metrics=['accuracy'])
        self.model.summary()

        train_data = self.get_train_datagen(rotation_range=30., shear_range=0.2, zoom_range=0.2)
        callbacks = self.get_callbacks(weights_path=config.get_fine_tuned_weights_path(), patience=self.fine_tuning_patience)

        if util.is_keras2():
            while not config.nb_validation_samples:
                print('waiting test data...')
                util.set_samples_info()
                time.sleep(3)
            _history = self.model.fit_generator(
                            train_data,
                            steps_per_epoch=config.nb_train_samples / float(self.batch_size),
                            epochs=self.nb_epoch,
                            validation_steps=config.nb_validation_samples / float(self.batch_size),
                            validation_data=self.get_validation_datagen(),
                            callbacks=callbacks,
                            class_weight=self.class_weight)
        else:
            _history = self.model.fit_generator(
                            train_data,
                            samples_per_epoch=config.nb_train_samples,
                            nb_epoch=self.nb_epoch,
                            validation_data=self.get_validation_datagen(),
                            nb_val_samples=config.nb_validation_samples,
                            callbacks=callbacks,
                            class_weight=self.class_weight)

        self.model.save(config.get_model_path())
        util.save_history(_history, '{}_log'.format(self.model))

    def train(self):
        import os
        pid = os.getpid()
        print('**pid: %s **' % pid)
        print("Creating model...")
        self._create()
        print("Model is created")
        print("Fine tuning...")
        self._fine_tuning()
        self.save_classes()
        print("Classes are saved")

    def load(self):
        print("Creating model")
        self.load_classes()
        self._create()
        self.model.load_weights(config.get_fine_tuned_weights_path())
        return self.model

    @staticmethod
    def save_classes():
        joblib.dump(config.classes, config.get_classes_path())

    def get_input_tensor(self):
        if util.get_keras_backend_name() == 'theano':
            return Input(shape=(3,) + self.img_size)
        else:
            return Input(shape=self.img_size + (3,))

    @staticmethod
    def make_net_layers_non_trainable(model):
        for layer in model.layers:
            layer.trainable = False

    def freeze_top_layers(self):
        if self.freeze_layers_number:
            print("Freezing {} layers".format(self.freeze_layers_number))
            for layer in self.model.layers[:self.freeze_layers_number]:
                layer.trainable = False
            for layer in self.model.layers[self.freeze_layers_number:]:
                layer.trainable = True


    @staticmethod
    def get_callbacks(weights_path, patience=5, monitor='val_loss'):
        early_stopping = EarlyStopping(verbose=1, patience=patience, monitor=monitor)
        model_checkpoint = ModelCheckpoint(weights_path, save_best_only=True, save_weights_only=True, monitor=monitor)
        if config.lr_policy == 0:
            reduce_lr = LearningRateScheduler(BaseModel.step_decay)
        else:
            reduce_lr = ReduceLROnPlateau(monitor=monitor, patience=patience, mode='auto')
        return [early_stopping, model_checkpoint, reduce_lr]

    @staticmethod
    def apply_mean(image_data_generator):
        """Subtracts the dataset mean"""
        # image_data_generator.mean = np.array([103.939, 116.779, 123.68], dtype=np.float32).reshape((3, 1, 1))
        if config.img_mean is None:
            image_data_generator.mean = np.array(BaseModel.get_image_mean(config.train_dir), dtype=np.float32).reshape((3, 1, 1))
        else:
            image_data_generator.mean = np.array(config.img_mean, dtype=np.float32).reshape((3, 1, 1))


    @staticmethod
    def load_classes():
        config.classes = joblib.load(config.get_classes_path())

    def load_img(self, img_path):
        img = image.load_img(img_path, target_size=self.img_size)
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        return preprocess_input(x)[0]

    def get_train_datagen(self, *args, **kwargs):
        idg = ImageDataGenerator(horizontal_flip=config.horizontal_flip, vertical_flip=config.vertical_flip,
                                 rescale=config.rescale, *args, **kwargs)
        self.apply_mean(idg)
        return idg.flow_from_directory(config.train_dir, target_size=self.img_size, classes=config.classes)

    def get_validation_datagen(self, *args, **kwargs):
        idg = ImageDataGenerator(*args, **kwargs)
        self.apply_mean(idg)
        return idg.flow_from_directory(config.validation_dir, target_size=self.img_size, classes=config.classes)

    @staticmethod
    def step_decay(epoch):
        initial_lrate = 0.01
        drop = 0.5
        epochs_drop = 10.0
        lrate = initial_lrate * math.pow(drop, math.floor((1 + epoch) / epochs_drop))
        return lrate

    @staticmethod
    def get_image_mean(train_data_path):
        images = glob.glob(train_data_path + '/**/*.jpg')
        r_channel = 0
        g_channel = 0
        b_channel = 0
        for image in images:
            img = cv2.imread(image)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (224, 224))
            r_channel = r_channel + np.sum(img[:, :, 0])
            g_channel = g_channel + np.sum(img[:, :, 1])
            b_channel = b_channel + np.sum(img[:, :, 2])
            # r_channel = r_channel + img[:, :, 0].mean()
            # g_channel = g_channel + img[:, :, 1].mean()
            # b_channel = b_channel + img[:, :, 2].mean()
        num = len(images) * 224 * 224
        r_mean = r_channel / num
        g_mean = g_channel / num
        b_mean = b_channel / num
        return [r_mean, g_mean, b_mean]

