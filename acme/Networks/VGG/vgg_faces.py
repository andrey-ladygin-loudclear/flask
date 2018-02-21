from urllib.request import urlretrieve
from os.path import isfile, isdir
from tqdm import tqdm

from acme.Networks.VGG.fr_utils import list_dir, get_batch_from_peoples, triplet_loss
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

#dir = '/home/srivoknovskiy/deepnets/lfw'
dir = 'E:\dataset\lfw/'
peoples = list_dir(dir, count_of_images=None, count_of_peoples=None)


# Set the batch size higher if you can fit in in your GPU memory
batch_size = 10
codes_list = []
labels = []
batch = []

codes = None
c=0
if not isfile(faces_codes_file):
    with tf.Session() as sess:
        vgg = vgg16.Vgg16()
        input_ = tf.placeholder(tf.float32, [None, 224, 224, 3])
        with tf.name_scope("content_vgg"):
            vgg.build(input_)

        for somebody_name in peoples:
            c+=1
            if c == 3: break
            print("Starting {} images".format(somebody_name))
            class_path = dir + somebody_name
            files = os.listdir(class_path)
            for ii, file in enumerate(files, 1):
                # Add images to the current batch
                # utils.load_image crops the input images for us, from the center
                img = utils.load_image(os.path.join(class_path, file))
                batch.append(img.reshape((1, 224, 224, 3)))
                labels.append(somebody_name)

                # Running the batch through the network to get the codes
                if ii % batch_size == 0 or ii == len(files):
                    images = np.concatenate(batch)

                    feed_dict = {input_: images}
                    codes_batch = sess.run(vgg.relu6, feed_dict=feed_dict)

                    # Here I'm building an array of the codes
                    if codes is None:
                        codes = codes_batch
                    else:
                        codes = np.concatenate((codes, codes_batch))

                    # Reset to start building the next batch
                    batch = []
                    print('{} images processed'.format(ii))
    print(codes, codes.shape)

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

print('labels', labels.shape)
print('codes', codes.shape)

raise EnvironmentError





from sklearn.preprocessing import LabelBinarizer

lb = LabelBinarizer()
lb.fit(labels)

labels_vecs = lb.transform(labels)




from sklearn.model_selection import StratifiedShuffleSplit

ss = StratifiedShuffleSplit(n_splits=1, test_size=0.2)

train_idx, val_idx = next(ss.split(codes, labels_vecs))

half_val_len = int(len(val_idx)/2)
val_idx, test_idx = val_idx[:half_val_len], val_idx[half_val_len:]

train_x, train_y = codes[train_idx], labels_vecs[train_idx]
val_x, val_y = codes[val_idx], labels_vecs[val_idx]
test_x, test_y = codes[test_idx], labels_vecs[test_idx]
print("Train shapes (x, y):", train_x.shape, train_y.shape)
print("Validation shapes (x, y):", val_x.shape, val_y.shape)
print("Test shapes (x, y):", test_x.shape, test_y.shape)



#https://stackoverflow.com/questions/43158606/how-to-get-weights-from-tensorflow-fully-connected
learning_rate = 0.001
anchor_codes = tf.placeholder(tf.float32, shape=[None, codes.shape[1]])
positive_codes = tf.placeholder(tf.float32, shape=[None, codes.shape[1]])
negative_codes = tf.placeholder(tf.float32, shape=[None, codes.shape[1]])
#labels_ = tf.placeholder(tf.int64, shape=[None, labels_vecs.shape[1]])

anchor_fc = tf.contrib.layers.fully_connected(anchor_codes, 256)
positive_fc = tf.contrib.layers.fully_connected(positive_codes, 256)
negative_fc = tf.contrib.layers.fully_connected(negative_codes, 256)

anchor_logits = tf.contrib.layers.fully_connected(anchor_fc, 256, activation_fn=None)
positive_logits = tf.contrib.layers.fully_connected(positive_fc, 256, activation_fn=None)
negative_logits = tf.contrib.layers.fully_connected(negative_fc, 256, activation_fn=None)


loss, positives, negatives = triplet_loss([anchor, positive, negative])
# cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=labels_, logits=logits)
# cost = tf.reduce_mean(cross_entropy)

#optimizer = tf.train.AdamOptimizer().minimize(cost)
optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(loss)

# predicted = tf.nn.softmax(logits)
# correct_pred = tf.equal(tf.argmax(predicted, 1), tf.argmax(labels_, 1))
# accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))




epochs = 10
iteration = 0
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())

    for e in range(epochs):
        for x, y in get_batches(train_x, train_y):
            feed = {inputs_: x, labels_: y}
            loss, _ = sess.run([cost, optimizer], feed_dict=feed)
            print("Epoch: {}/{}".format(e+1, epochs), "Iteration: {}".format(iteration), "Training loss: {:.5f}".format(loss))
            iteration += 1

            if iteration % 5 == 0:
                feed = {inputs_: val_x,
                        labels_: val_y}
                val_acc = sess.run(accuracy, feed_dict=feed)
                print("Epoch: {}/{}".format(e, epochs), "Iteration: {}".format(iteration), "Validation Acc: {:.4f}".format(val_acc))
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