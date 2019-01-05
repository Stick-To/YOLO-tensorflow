import tensorflow as tf
import numpy as np
import os
import utils.tfrecord_voc_utils as voc_utils
import YOLOv2 as yolov2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from skimage import io, transform
from utils.voc_classname_encoder import classname_to_ids

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
device_name = tf.test.gpu_device_name()
if device_name is not '':
    print('Found GPU Device!')
else:
    print('Found GPU Device Failed!')

lr = 0.01
batch_size = 24
buffer_size = 256
epochs = 280
input_shape = [480, 480 ,3]
reduce_lr_epoch = [120, 250]
config = {
    'mode': 'train',     # 'train', 'test'
    'is_pretraining': False,
    'data_shape': input_shape,
    'num_classes': 20,
    'weight_decay': 1e-4,
    'keep_prob': 0.5,
    'data_format': 'channels_last',
    'batch_size': batch_size,
    'coord_scale': 1,
    'noobj_scale': 1,
    'obj_scale': 5.,
    'class_scale': 1.,

    'nms_score_threshold': 0.2,
    'nms_max_boxes': 10,
    'nms_iou_threshold': 0.5,

    'rescore_confidence': False,
    'priors': [[1.08, 1.19], [3.42, 4.41], [6.63, 11.38], [9.42, 5.11], [16.62, 10.52]]
}
#


data = ['./data/test_00000-of-00010.tfrecord',
        './data/test_00001-of-00010.tfrecord',
        './data/test_00002-of-00010.tfrecord',
        './data/test_00003-of-00010.tfrecord',
        './data/test_00004-of-00010.tfrecord',
        './data/test_00005-of-00010.tfrecord',
        './data/test_00006-of-00010.tfrecord',
        './data/test_00007-of-00010.tfrecord',
        './data/test_00008-of-00010.tfrecord',
        './data/test_00009-of-00010.tfrecord']

def get_datagen(input_shape, data, batch_size, buffer_size):
    image_preprocess_config = {
        'data_format': 'channels_last',
        'target_size': [input_shape[0], input_shape[1]],
        'shorter_side': 480,
        'is_random_crop': False,
        'random_horizontal_flip': 0.5,
        'random_vertical_flip': 0.,
        'pad_truth_to': 60
    }
    train_gen = voc_utils.get_generator(data,
                                    batch_size, buffer_size, image_preprocess_config)
    trainset_provider = {
        'data_shape': input_shape,
        'num_train': 22136,
        'num_val': 0,
        'train_generator': train_gen,
        'val_generator': None
    }
    return trainset_provider


trainset_provider = get_datagen(input_shape, data, batch_size, buffer_size)
testnet = yolov2.YOLOv2(config, trainset_provider)
# testnet.load_weight()
for i in range(epochs):
    print('-'*25, 'epoch', i, '-'*25)
    if i in reduce_lr_epoch:
        lr = lr/10.
        print('reduce lr, lr=', lr, 'now')
    print('>> shape', [416, 416, 3])
    trainset_provider = get_datagen([416, 416, 3], data, batch_size, buffer_size)
    mean_loss = testnet.train_one_epoch(lr, data_provider=trainset_provider)
    print('>> mean loss', mean_loss)
    print('>> shape', [448, 448, 3])
    trainset_provider = get_datagen([448, 448, 3], data, batch_size, buffer_size)
    mean_loss = testnet.train_one_epoch(lr, data_provider=trainset_provider)
    print('>> mean loss', mean_loss)
    print('>> shape', [480, 480, 3])
    trainset_provider = get_datagen([480, 480, 3], data, batch_size, buffer_size)
    mean_loss = testnet.train_one_epoch(lr, data_provider=trainset_provider)
    print('>> mean loss', mean_loss)

    testnet.save_weight('latest', './weight/test')
# img = io.imread('/home/test/Desktop/YOLO-TF-master/VOC/JPEGImages/000012.jpg')
# img = transform.resize(img, [448,448])
# img = np.expand_dims(img, 0)
# result = testnet.test_one_image(img)


# id_to_clasname = {k:v  for (v,k) in classname_to_ids.items()}
# scores = result[0]
# bbox = result[1]
# class_id = result[2]
# print(scores, bbox, class_id)
# plt.figure(1)
# plt.imshow(np.squeeze(img))
# axis = plt.gca()
# for i in range(len(scores)):
#     rect = patches.Rectangle((bbox[i][1],bbox[i][0]), bbox[i][3]-bbox[i][1],bbox[i][2]-bbox[i][0],linewidth=2,edgecolor='b',facecolor='none')
#     axis.add_patch(rect)
#     plt.text(bbox[i][1],bbox[i][0], id_to_clasname[class_id[0]]+str(' ')+str(scores[0]), color='red')
# plt.show()
