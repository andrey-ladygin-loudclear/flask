import os
import random
import tensorflow as tf


def list_dir(path, count_of_images=10, count_of_peoples=10):
    dict = {}

    for folder in os.listdir(path):
        images = os.listdir(os.path.join(path, folder))

        if len(images) > 10:
            if count_of_peoples:
                count_of_peoples -= 1

            if count_of_images:
                dict[folder] = images[:count_of_images]
            else:
                dict[folder] = images

        if count_of_peoples == 0: break

    return dict


def get_batch_from_peoples(peoples):
    def get_negative_sample(name):
        key = random.choice(list(peoples.keys()))
        while name == key:
            key = random.choice(list(peoples.keys()))
        return os.path.join(key, random.choice(peoples[key]))

    def get_positive_sample(key, curr_image):
        image = random.choice(peoples[key])
        while image == curr_image:
            image = random.choice(peoples[key])
        return os.path.join(key, image)

    for somebody in peoples:
        for image in peoples[somebody]:
            negative = get_negative_sample(somebody)
            positive = get_positive_sample(somebody, image)
            yield os.path.join(somebody, image), positive, negative



def triplet_loss(y_pred, alpha = 0.2):
    anchor, positive, negative = y_pred[0], y_pred[1], y_pred[2]

    pos_dist = tf.reduce_sum(tf.square(tf.subtract(anchor, positive)))
    neg_dist = tf.reduce_sum(tf.square(tf.subtract(anchor, negative)))
    basic_loss = tf.add(tf.subtract(pos_dist, neg_dist), alpha)
    loss = tf.maximum(tf.reduce_mean(basic_loss), 0.0), pos_dist, neg_dist

    return loss, pos_dist, neg_dist