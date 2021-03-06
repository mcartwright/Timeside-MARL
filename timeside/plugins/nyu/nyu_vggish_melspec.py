# -*- coding: utf-8 -*-

from timeside.core import implements, interfacedoc
from timeside.core.preprocessors import downmix_to_mono, frames_adapter
from timeside.core.tools.parameters import store_parameters
from timeside.core.analyzer import Analyzer
from timeside.core.api import IAnalyzer
import numpy as np

from features import vggish_melspec, vggish_params


class NYUVGGishMelSpectrogam(Analyzer):

    """Mel spectrogram"""
    implements(IAnalyzer)

    @store_parameters
    def __init__(self,
                 input_blocksize=int(round(22050 * vggish_params.STFT_WINDOW_LENGTH_SECONDS)),
                 input_stepsize=int(round(22050 * vggish_params.STFT_HOP_LENGTH_SECONDS)),
                 input_samplerate=22050):
        super(NYUVGGishMelSpectrogam, self).__init__()
        self.input_blocksize = input_blocksize
        self.input_stepsize = input_stepsize
        self.input_samplerate = input_samplerate
        self.frame_idx = 0
        self.values = None


    @interfacedoc
    def setup(self, channels=None,
              samplerate=None,
              blocksize=None,
              totalframes=None):
        super(NYUVGGishMelSpectrogam, self).setup(channels, samplerate, blocksize, totalframes)
        totalblocks = (self.totalframes() - self.input_blocksize) / self.input_stepsize + 2
        self.values = np.empty([totalblocks, 64])


    @staticmethod
    @interfacedoc
    def id():
        return "nyu_vggish_melspec"

    @staticmethod
    @interfacedoc
    def name():
        return "NYU VGGish Mel Spectrogram"

    @staticmethod
    @interfacedoc
    def unit():
        return ""

    @staticmethod
    @interfacedoc
    def version():
        return '1.0'

    @property
    def force_samplerate(self):
        return self.input_samplerate

    @downmix_to_mono
    @frames_adapter
    def process(self, frames, eod=False):
        self.values[self.frame_idx, :] = vggish_melspec(None, frames=[frames,], sr=self.input_samplerate, do_resample=False).flatten()
        self.frame_idx += 1
        return frames, eod

    def post_process(self):
        result = self.new_result(data_mode='value', time_mode='framewise')
        result.data_object.value = self.values
        self.add_result(result)
