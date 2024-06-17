# -*- coding: utf-8 -*-
"""plant_disease_detection

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1toD1KNTUqyNS2bGLNddtZjUpZ5SLXW8Q

# *MOUNTING DRIVE AND INSTALLING KERAS*
"""

from google.colab import drive
drive.mount('/content/drive')

"""**INSTALLING KERAS**"""

!pip install -q keras

"""**IMPORTING NECCASSARY LIBs AND DEFINING TRAIN AND TEST DATA**"""

import keras
import tensorflow as tf
from keras.layers import Input, Lambda, Dense, Flatten
from keras.models import Model
from tensorflow.keras.applications.vgg19 import VGG19
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import Callback  # Correct import
import os
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt


IMAGE_SIZE =[224,224]

train_datagen = ImageDataGenerator(rescale=1./255, shear_range=0.2, zoom_range=0.2, horizontal_flip=True)
train_generator = train_datagen.flow_from_directory(
    '/content/drive/MyDrive/plant_disease/train',
    target_size=IMAGE_SIZE,
    batch_size=32,
    class_mode='categorical'  # Assuming multiple classes
)
test_data = "/content/drive/MyDrive/plant_disease/test"

"""**IMAGE PRE-PROCESSING**
**MODEL CREATION AND COMPILATION**
"""

# 1. Load VGG19 with pre-trained weights
vgg = VGG19(input_shape=IMAGE_SIZE + [3], weights="imagenet", include_top=False)

# 2. Freeze layers in the pre-trained model
for layer in vgg.layers:
  layer.trainable = False

# 3. Flatten the output of VGG19
x = Flatten()(vgg.output)

# 4. Add a Dense layer with softmax activation (modify num_classes if needed)
num_classes = len(os.listdir('/content/drive/MyDrive/plant_disease/train'))  # Assuming one subdirectory per class
prediction = Dense(num_classes, activation='softmax')(x)

# 5. Create the final model
model = Model(inputs=vgg.input, outputs=prediction)

# 6. Compile the model and its summary
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)
model.summary()

"""**TRAIN AND VALIDATION DATA GENERATOR**"""

# 7. Define data generators (modify paths and parameters as needed)
train_datagen = ImageDataGenerator(rescale=1./255, shear_range=0.2, zoom_range=0.2, horizontal_flip=True)
val_datagen = ImageDataGenerator(rescale=1./255)  # No data augmentation for validation

train_generator = train_datagen.flow_from_directory(
    '/content/drive/MyDrive/plant_disease/train',
    target_size=IMAGE_SIZE,
    batch_size=32,
    class_mode='categorical'
)

val_generator = val_datagen.flow_from_directory(
    '/content/drive/MyDrive/plant_disease/train',  # validation directory exists
    target_size=IMAGE_SIZE,
    batch_size=32,
    class_mode='categorical'
)

"""**TRAINING DATA USING EPOCHs WITH SAVE_FREQ TO SAVE PROGRESS**"""

class CustomModelCheckpoint(Callback):
    def __init__(self, checkpoint_path, save_freq):
        super(CustomModelCheckpoint, self).__init__()
        self.checkpoint_path = checkpoint_path
        self.save_freq = save_freq

    def on_epoch_end(self, epoch, logs=None):
        if epoch % self.save_freq == 0:
            # Save the model
            filepath = self.checkpoint_path.format(iteration=epoch)
            self.model.save(filepath)

checkpoint_path = '/content/drive/MyDrive/plant_disease/models/plant_disease_detector_{iteration:03d}.h5'
save_freq = 10 #NO. of iterations before save progress
checkpoint = CustomModelCheckpoint(checkpoint_path, save_freq)


model_path = '/content/drive/MyDrive/plant_disease/models/plant_disease_detector.h5'


# Training the model with restricted iterations
history = model.fit(
    train_generator,
    steps_per_epoch=10,  # Restrict number of iterations to 10 PER EPOCH
    epochs=1,  # Adjust number of epochs
    validation_data=val_generator,
    validation_steps=len(val_generator),
    callbacks=[checkpoint]
)

"""**SAVING MODEL TO DRIVE **"""

model.save(model_path)
print(f"Model saved at {model_path}")

# Test phase: Check if the model file exists
if os.path.exists(model_path):
    print(f"Loading model from {model_path}")
    model = load_model(model_path)
    print("Model loaded successfully")
else:
    print(f"Error: Model file not found at {model_path}")

"""**TESTING SAVED MODEL ON RANDOM IMAGES**"""

import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image  # For image loading
import matplotlib.pyplot as plt

# Model path (assuming the model file exists)
model_path = '/content/drive/MyDrive/plant_disease/models/plant_disease_detector.h5'

# Test phase: Check if the model file exists
if os.path.exists(model_path):
    print(f"Loading model from {model_path}")
    model = load_model(model_path)
    print("Model loaded successfully")
else:
    print(f"Error: Model file not found at {model_path}")

# Function to preprocess an image
def preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(224, 224))  # Assuming VGG19 input size

    # Convert the image to a NumPy array
    x = image.img_to_array(img)

    # Add a batch dimension for prediction
    x = np.expand_dims(x, axis=0)

    # Rescale the pixel values (assuming values are in range 0-255)
    x = x / 255.0  # Normalize pixel values between 0 and 1

    # You can add further preprocessing steps here (e.g., data augmentation)

    return x

# Example usage: predict on a single image
# Replace with the actual path to your test image
image_path = '/content/drive/MyDrive/plant_disease/test/AppleCedarRust1.JPG'

# Preprocess the image
processed_image = preprocess_image(image_path)

# Make prediction on the single image
prediction = model.predict(processed_image)

# Process and display the prediction result
predicted_class = np.argmax(prediction, axis=1)
print(f"Predicted Class for {image_path}: {predicted_class}")