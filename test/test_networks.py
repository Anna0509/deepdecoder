# Copyright 2015 Leon Sixt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from conftest import on_gpu
from keras.models import Sequential
from keras.layers.core import Dense, Flatten, Reshape
from keras.optimizers import Adam
from beesgrid import TAG_SIZE
from deepdecoder.networks import gan_with_z_rot90_grid_idx, dcgan_generator, \
    mogan_learn_bw_grid, dcgan_discriminator, \
    dcgan_small_generator, dcgan_pyramid_mse_generator
import pytest
import keras.backend as K


def test_networks_gan_with_z_rot90_grid_idx():
    n = TAG_SIZE*TAG_SIZE
    nb_z = 20
    generator = Sequential()
    generator.add(Dense(n, input_dim=nb_z+NB_GAN_GRID_PARAMS))
    generator.add(Reshape((1, TAG_SIZE, TAG_SIZE)))

    discriminator = Sequential()
    discriminator.add(Flatten(input_shape=(1, TAG_SIZE, TAG_SIZE)))
    discriminator.add(Dense(1, input_dim=n))

    gan = gan_with_z_rot90_grid_idx(generator, discriminator, nb_z=nb_z,
                                    reconstruct_fn=add_diff_rot90)
    gan.compile(Adam(), Adam())
    batch = next(gen_diff_gan(gan.batch_size * 10))
    gan.fit(batch.grid_bw, {'grid_idx': batch.grid_idx,
                            'z_rot90': batch.z_bins,
                            'grid_params': batch.params},
            nb_epoch=1, verbose=1)


@pytest.mark.skipif(not on_gpu(), reason="only works with cuda")
def test_mogan_learn_bw_grid():
    gan, _ = mogan_learn_bw_grid(dcgan_generator, dcgan_discriminator)
    gan.compile()


def test_autoencoder_mask_generator_loading(tmpdir):
    nb_input = 21
    g = dcgan_small_generator(input_dim=nb_input, nb_output_channels=2)
    fname = str(tmpdir) + "/g.hdf5"
    g.save_weights(fname)

    g_load = dcgan_small_generator(input_dim=nb_input, nb_output_channels=2)
    g_load.load_weights(fname)
    for a, b in zip(g.trainable_weights, g_load.trainable_weights):
        assert (K.get_value(a) == K.get_value(b)).all()
