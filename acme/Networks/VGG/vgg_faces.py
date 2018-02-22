import random
from urllib.request import urlretrieve
from os.path import isfile, isdir
from tqdm import tqdm

from acme.Networks.VGG.fr_utils import list_dir, get_batch_from_peoples, triplet_loss, get_shuffled_training_set, \
    batch_data, triplet_loss2, compute_triplet_loss
from acme.Networks.VGG.tensorflow_vgg import vgg16
from acme.Networks.VGG.tensorflow_vgg import utils

vgg_dir = 'tensorflow_vgg/'
faces_codes_file = 'faces_codes'
faces_labels_file = 'faces_labels'

import os

import numpy as np
import tensorflow as tf

imw = 96
imh = 96

dir = '/home/srivoknovskiy/deepnets/lfw/'
# dir = 'E:\dataset\lfw/'
peoples = list_dir(dir, count_of_images=None, count_of_peoples=None)


# Set the batch size higher if you can fit in in your GPU memory
batch_size = 16
codes_list = []
labels = []
batch = []

codes = []
c=0
if not isfile(faces_codes_file):
    with tf.Session() as sess:
        vgg = vgg16.Vgg16()
        input_ = tf.placeholder(tf.float32, [None, 224, 224, 3])
        with tf.name_scope("content_vgg"):
            vgg.build(input_)

        for somebody_name in peoples:
            # c+=1
            # if c == 10: break

            print("Starting {} images".format(somebody_name))
            class_path = dir + somebody_name
            files = os.listdir(class_path)
            for ii, file in enumerate(files, 1):
                # Add images to the current batch
                # utils.load_image crops the input images for us, from the center
                img = utils.load_image(os.path.join(class_path, file))
                batch.append(img.reshape((1, 224, 224, 3)))
                feed_dict = {input_: [img]}
                codes_batch = sess.run(vgg.relu6, feed_dict=feed_dict)

                codes.append(codes_batch[0])
                labels.append(somebody_name)
                print(ii, 'of', len(files))

    codes = np.array(codes)
    print('codes', codes.shape)
    print('labels', len(labels))

    # write codes to file
    with open(faces_codes_file, 'w') as f:
        codes.tofile(f)

    # write labels to file
    import csv
    with open(faces_labels_file, 'w') as f:
        writer = csv.writer(f, delimiter='\n')
        writer.writerow(labels)

# read codes and labels from file
import csv

with open(faces_labels_file) as f:
    reader = csv.reader(f, delimiter='\n')
    labels = np.array([each for each in reader if len(each) > 0]).squeeze()
with open(faces_codes_file) as f:
    codes = np.fromfile(f, dtype=np.float32)
    codes = codes.reshape((len(labels), -1))

print('labels', labels.shape, len(set(labels)))
print('codes', codes.shape)


X_train = get_shuffled_training_set(codes, labels)

print('X_train', X_train.shape)

tf.reset_default_graph()
learning_rate = 0.001

def build_fully_connected_layers(tensor, reuse=False):
    with tf.variable_scope('fc_layers', reuse=reuse) as scope:
        # tensor = tf.contrib.layers.fully_connected(tensor, 2048, scope = 'fc1')
        # tensor = tf.contrib.layers.fully_connected(tensor, 1024, scope = 'fc2')
        tensor = tf.contrib.layers.fully_connected(tensor, 512, scope = 'fc2', reuse=reuse)
        tensor = tf.contrib.layers.fully_connected(tensor, 4, activation_fn=None, scope = 'fc3', reuse=reuse)
    return tensor
#https://stackoverflow.com/questions/43158606/how-to-get-weights-from-tensorflow-fully-connected

anchor_codes = tf.placeholder(tf.float32, shape=[None, codes.shape[1]], name='anchor')
positive_codes = tf.placeholder(tf.float32, shape=[None, codes.shape[1]], name='positive')
negative_codes = tf.placeholder(tf.float32, shape=[None, codes.shape[1]], name='negative')

anchor = build_fully_connected_layers(anchor_codes)
positive = build_fully_connected_layers(anchor_codes, reuse=True)
negative = build_fully_connected_layers(anchor_codes, reuse=True)

#loss, positive_dist, negative_dist = compute_triplet_loss([anchor, positive, negative])
loss, positive_dist, negative_dist = triplet_loss([anchor, positive, negative], alpha=20)
#optimizer = tf.train.AdamOptimizer().minimize(cost)
optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(loss)



epochs = 10
iteration = 0
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())

    for e in range(epochs):
        for row in batch_data(X_train, batch_size):
            anc_codes = row[:, 0]
            pos_codes = row[:, 1]
            neg_codes = row[:, 2]

            feed = {anchor_codes: anc_codes, positive_codes: pos_codes, negative_codes: neg_codes}
            cost, _, p_dist, n_dist = sess.run([loss, optimizer, positive_dist, negative_dist], feed_dict=feed)
            print(
                "Epoch: {}/{}".format(e+1, epochs),
                "Iteration: {}".format(iteration),
                "Training loss: {:.5f}".format(cost),
                "Positive dist: {:.5f}".format(p_dist),
                "Negative dist: {:.5f}".format(n_dist)
            )
            iteration += 1

            # if iteration % 5 == 0:
            #     feed = {inputs_: val_x,
            #             labels_: val_y}
            #     val_acc = sess.run(accuracy, feed_dict=feed)
            #     print("Epoch: {}/{}".format(e, epochs), "Iteration: {}".format(iteration), "Validation Acc: {:.4f}".format(val_acc))
    # saver.save(sess, "checkpoints/flowers.ckpt")



raise EnvironmentError




def get_batches(x, y, n_batches=10):
    """ Return a generator that yields batches from arrays x and y. """
    batch_size = len(x)//n_batches

    for ii in range(0, n_batches*batch_size, batch_size):
        # If we're not on the last batch, grab data with size batch_size
        if ii != (n_batches-1)*batch_size:
            X, Y = x[ii: ii+batch_size], y[ii: ii+batch_size]
            # On the last batch, grab the rest of the data
        else:
            X, Y = x[ii:], y[ii:]
        # I love generators
        yield X, Y





saver = tf.train.Saver()

if not isdir('checkpoints'):
    epochs = 10
    iteration = 0
    with tf.Session() as sess:

        sess.run(tf.global_variables_initializer())
        for e in range(epochs):
            for x, y in get_batches(train_x, train_y):
                feed = {inputs_: x,
                        labels_: y}
                loss, _ = sess.run([cost, optimizer], feed_dict=feed)
                print("Epoch: {}/{}".format(e+1, epochs),
                      "Iteration: {}".format(iteration),
                      "Training loss: {:.5f}".format(loss))
                iteration += 1

                if iteration % 5 == 0:
                    feed = {inputs_: val_x,
                            labels_: val_y}
                    val_acc = sess.run(accuracy, feed_dict=feed)
                    print("Epoch: {}/{}".format(e, epochs),
                          "Iteration: {}".format(iteration),
                          "Validation Acc: {:.4f}".format(val_acc))
        saver.save(sess, "checkpoints/flowers.ckpt")






with tf.Session() as sess:
    saver.restore(sess, tf.train.latest_checkpoint('checkpoints'))

    feed = {inputs_: test_x,
            labels_: test_y}
    test_acc = sess.run(accuracy, feed_dict=feed)
    print("Test accuracy: {:.4f}".format(test_acc))



#Testing

import matplotlib.pyplot as plt
from scipy.ndimage import imread


test_img_path = 'flower_photos/roses/10894627425_ec76bbc757_n.jpg'
test_img = imread(test_img_path)
plt.imshow(test_img)


# Run this cell if you don't have a vgg graph built
with tf.Session() as sess:
    input_ = tf.placeholder(tf.float32, [None, 224, 224, 3])
    vgg = vgg16.Vgg16()
    vgg.build(input_)


with tf.Session() as sess:
    img = utils.load_image(test_img_path)
    img = img.reshape((1, 224, 224, 3))

    feed_dict = {input_: img}
    code = sess.run(vgg.relu6, feed_dict=feed_dict)

saver = tf.train.Saver()
with tf.Session() as sess:
    saver.restore(sess, tf.train.latest_checkpoint('checkpoints'))

    feed = {inputs_: code}
    prediction = sess.run(predicted, feed_dict=feed).squeeze()




plt.imshow(test_img)

plt.barh(np.arange(5), prediction)
_ = plt.yticks(np.arange(5), lb.classes_)