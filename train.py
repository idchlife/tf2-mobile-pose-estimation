# Copyright 2019 Doyoung Gwak (tucan.dev@gmail.com)
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ======================
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import os
import numpy as np
import datetime

import tensorflow as tf

from config.model_config import ModelConfig
from config.train_config import PreprocessingConfig
from config.train_config import TrainConfig
from config.paths_config import (DATASETS_PATH,
                                 OUTPUT_PATH,
                                 TRAIN_IMAGES_DIR_PATH,
                                 TRAIN_ANNOTATIONS_JSON_FILEPATH,
                                 VALID_IMAGES_DIR_PATH,
                                 VALID_ANNOTATIONS_JSON_FILEPATH)

from common import get_time_and_step_interval



print("tensorflow version   :", tf.__version__) # 2.1.0
print("keras version        :", tf.keras.__version__) # 2.2.4-tf

train_config = TrainConfig()
model_config = ModelConfig()
preproc_config = PreprocessingConfig()

train_config.input_size = 256
train_config.output_size = 64
train_config.batch_size = 32

dataset_path = DATASETS_PATH # "/Volumes/tucan-SSD/datasets/ai_challenger"
dataset_name = dataset_path.split("/")[-1]
current_time = datetime.datetime.now().strftime("%m%d%H%M")
output_model_name = "_sp-" + dataset_name
output_path = OUTPUT_PATH
output_name = current_time + output_model_name


# ================================================
# ================= load dataset =================
# ================================================

from data_loader.data_loader import DataLoader

# dataloader instance gen
train_images_dir_path = TRAIN_IMAGES_DIR_PATH
train_annotation_json_filepath = TRAIN_ANNOTATIONS_JSON_FILEPATH
print(">> LOAD TRAIN DATASET FORM:", train_annotation_json_filepath)
dataloader_train = DataLoader(
    images_dir_path=train_images_dir_path,
    annotation_json_path=train_annotation_json_filepath,
    train_config=train_config,
    model_config=model_config,
    preproc_config=preproc_config)

valid_images_dir_path = VALID_IMAGES_DIR_PATH
valid_annotation_json_filepath = VALID_ANNOTATIONS_JSON_FILEPATH
print(">> LOAD VALID DATASET FORM:", valid_annotation_json_filepath)
dataloader_valid = DataLoader(
    images_dir_path=valid_images_dir_path,
    annotation_json_path=valid_annotation_json_filepath,
    train_config=train_config,
    model_config=model_config,
    preproc_config=preproc_config)

number_of_keypoints = dataloader_train.number_of_keypoints # 17

# train dataset
dataset_train = dataloader_train.input_fn()

# validation images
val_images, val_heatmaps = dataloader_valid.get_images(0, batch_size=25) # from 22 index 6 images and 6 labels

# ================================================
# ============== configure model =================
# ================================================
# from models.simpleposemobile_coco import simplepose_mobile_mobilenetv3_small_w1_coco as simpleposemodel
# from models.simpleposemobile_coco import simplepose_mobile_mobilenetv2b_w1_coco as simpleposemodel
# from models.simplepose_coco import simplepose_resneta152b_coco as simpleposemodel
from models.simplepose_coco import simplepose_resnet50b_coco as simpleposemodel

# SimplePoseMobile
model = simpleposemodel(keypoints=number_of_keypoints)

# model configuration
model.return_heatmap = True

loss_object = tf.keras.losses.MeanSquaredError()
optimizer = tf.keras.optimizers.Adam(0.001, epsilon=1e-8)
train_loss = tf.keras.metrics.Mean(name="train_loss")
valid_loss = tf.keras.metrics.Mean(name="valid_loss")
valid_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name="valid_accuracy")

@tf.function
def train_step(images, labels):
    with tf.GradientTape() as tape:
        predictions = model(images)
        loss = loss_object(labels, predictions)
    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    train_loss(loss)
    return loss

from save_result_as_image import save_result_image

def val_step(step, images, heamaps):
    predictions = model(images)
    predictions = np.array(predictions)
    save_image_results(step, images, heamaps, predictions)

@tf.function
def valid_step(images, labels):
    predictions = model(images)
    v_loss = loss_object(labels, predictions)
    valid_loss(v_loss)
    # valid_accuracy(labels, predictions)
    return v_loss

def save_image_results(step, images, true_heatmaps, predicted_heatmaps):
    val_image_results_directory = "val_image_results"

    if not os.path.exists(output_path):
        os.mkdir(output_path)
    if not os.path.exists(os.path.join(output_path, output_name)):
        os.mkdir(os.path.join(output_path, output_name))
    if not os.path.exists(os.path.join(output_path, output_name, val_image_results_directory)):
        os.mkdir(os.path.join(output_path, output_name, val_image_results_directory))

    for i in range(images.shape[0]):
        image = images[i, :, :, :]
        heamap = true_heatmaps[i, :, :, :]
        prediction = predicted_heatmaps[i, :, :, :]

        # result_image = display(i, image, heamap, prediction)
        result_image_path = os.path.join(output_path, output_name, val_image_results_directory, "result%d-%d.jpg" % (i, step))
        save_result_image(result_image_path, image, heamap, prediction, title="step:%dk" % (step/1000))
        # print("val_step: save result image on \"" + result_image_path + "\"")

def save_model(step=None, label=None):
    saved_model_directory = "saved_model"
    if step is not None:
        saved_model_directory = saved_model_directory + "-%d" % step
    if label is not None:
        saved_model_directory = saved_model_directory + "-" + label

    if not os.path.exists(output_path):
        os.mkdir(output_path)
    if not os.path.exists(os.path.join(output_path, output_name)):
        os.mkdir(os.path.join(output_path, output_name))
    if not os.path.exists(os.path.join(output_path, output_name, saved_model_directory)):
        os.mkdir(os.path.join(output_path, output_name, saved_model_directory))

    saved_model_path = os.path.join(output_path, output_name, saved_model_directory)

    print("-"*20 + " MODEL SAVE!! " + "-"*20)
    print("saved model path: " + saved_model_path)
    model.save(saved_model_path)
    print("-"*18 + " MODEL SAVE DONE!! " + "-"*18)




num_epochs = 1000
step = 1
number_of_echo_period = 100
number_of_validimage_period = 1000
number_of_modelsave_period = 2000
valid_check = False



if __name__ == '__main__':

    # TRAIN!!
    get_time_and_step_interval(step, is_init=True)

    for epoch in range(num_epochs):
        print("-" * 10 + " " + str(epoch + 1) + " EPOCH " + "-" * 10)
        for images, heatmaps in dataset_train:

            # print(images.shape)  # (32, 128, 128, 3)
            # print(heatmaps.shape)  # (32, 32, 32, 17)
            loss = train_step(images, heatmaps)

            step += 1

            if step % number_of_echo_period == 0:
                total_interval, per_step_interval = get_time_and_step_interval(step)
                print(">> step: %d, total: %s, per_step: %s, loss: %.5f" % (step, total_interval, per_step_interval, loss))

            # validation phase
            if step % number_of_validimage_period == 0:
                val_step(step, val_images, val_heatmaps)

            if step % number_of_modelsave_period == 0:
                save_model(step=step)

        # if not valid_check:
        #     continue

        # for v_images, v_heatmaps in dataloader_valid:
        #     v_loss = valid_step(v_images, v_heatmaps)




    save_model(step=step, label="final")
