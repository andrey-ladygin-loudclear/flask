import random
import os
import tensorflow as tf

from acme.Networks.FRNN import cnn
from acme.Networks.FRNN.fr_utils import load_weights_from_FaceNet, img_to_encoding, list_dir, get_batch_from_peoples, \
    preprocess_image, shuffle, batch_data
from acme.Networks.FRNN.inception_blocks_v2 import faceRecoModel, faceRecoModel2
from acme.Networks.FRNN.triplet_loss import triplet_loss
from acme.Networks.FRNN.verify import verify
import numpy as np
import h5py

from acme.Networks.FRNN.vgg import vgg_face
dir = '/home/srivoknovskiy/deepnets/lfw'
peoples = list_dir(dir)

dataset = []

imw = 96
imh = 96

for i,p,n in get_batch_from_peoples(peoples):
    anchor = preprocess_image(os.path.join(dir, i), size=(imw,imh))
    positive = preprocess_image(os.path.join(dir, p), size=(imw,imh))
    negative = preprocess_image(os.path.join(dir, n), size=(imw,imh))
    dataset.append([anchor, positive, negative])

dataset = shuffle(np.array(dataset))


config = tf.ConfigProto()
config.gpu_options.allocator_type = 'BFC'

n_classes = 1
epochs = 100
batch_size = 2
keep_probability = 0.5

tf.reset_default_graph()


anchor_image = cnn.neural_net_image_input((imw, imh, 3), name='anchor_image')
positive_image = cnn.neural_net_image_input((imw, imh, 3), name='positive_image')
negative_image = cnn.neural_net_image_input((imw, imh, 3), name='negative_image')
keep_prob = cnn.neural_net_keep_prob_input()

anchor = cnn.make_logits(anchor_image, keep_prob)
positive = cnn.make_logits(positive_image, keep_prob)
negative = cnn.make_logits(negative_image, keep_prob)

loss = triplet_loss([anchor, positive, negative], alpha=.5)
optimizer = tf.train.AdamOptimizer().minimize(loss)

print('Total count of dataset', len(dataset))
print('Training...')

with tf.Session() as sess:
    # Initializing the variables
    sess.run(tf.global_variables_initializer())

    # Training cycle
    for epoch in range(epochs):
        batches_count = 0
        cost_sum = 0

        for row in batch_data(dataset, batch_size):
            anc_im = row[:, 0]
            pos_im = row[:, 1]
            neg_im = row[:, 2]
            _, cost = sess.run([optimizer, loss], feed_dict={
                anchor_image: anc_im,
                positive_image: pos_im,
                negative_image: neg_im,
                keep_prob: keep_probability})
            batches_count +=1
            cost_sum += cost
            print('CUR COST', cost)

        print('Epoch {:>2}, Batch:  '.format(epoch + 1), end='')
        print('Cost: ', (cost_sum / batches_count), end=' ')

        if cost_sum == 0:
            print('Cost is minimized. Break')
            break