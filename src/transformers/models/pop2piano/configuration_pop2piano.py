# coding=utf-8
# Copyright 2023 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Pop2Piano model configuration"""

from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Mapping, Optional, Union

from ...configuration_utils import PretrainedConfig
from ...onnx import OnnxConfig, OnnxSeq2SeqConfigWithPast
from ...utils import logging


if TYPE_CHECKING:
    from ...feature_extraction_utils import FeatureExtractionMixin
    from ...tokenization_utils_base import PreTrainedTokenizerBase
    from ...utils import TensorType

logger = logging.get_logger(__name__)

POP2PIANO_PRETRAINED_CONFIG_ARCHIVE_MAP = {
    "sweetcocoa/pop2piano": "https://huggingface.co/sweetcocoa/pop2piano/blob/main/config.json"
}

COMPOSER_TO_FEATURE_TOKEN = {'composer1': 2052,
                             'composer2': 2053,
                             'composer3': 2054,
                             'composer4': 2055,
                             'composer5': 2056,
                             'composer6': 2057,
                             'composer7': 2058,
                             'composer8': 2059,
                             'composer9': 2060,
                             'composer10': 2061,
                             'composer11': 2062,
                             'composer12': 2063,
                             'composer13': 2064,
                             'composer14': 2065,
                             'composer15': 2066,
                             'composer16': 2067,
                             'composer17': 2068,
                             'composer18': 2069,
                             'composer19': 2070,
                             'composer20': 2071,
                             'composer21': 2072
}

# Copied from transformers.models.t5.configuration_t5.T5Config with T5->Pop2Piano,T5Model->Pop2PianoModel,t5->pop2piano,T5Block->Pop2PianoBlock
class Pop2PianoConfig(PretrainedConfig):
    r"""
    This is the configuration class to store the configuration of a [`Pop2PianoModel`]. It is used to instantiate a
    Pop2Piano model according to the specified arguments, defining the model architecture. Instantiating a configuration
    with the defaults will yield a similar configuration to that of the Pop2Piano
    [sweetcocoa/pop2piano](https://huggingface.co/sweetcocoa/pop2piano) architecture.
    Configuration objects inherit from [`PretrainedConfig`] and can be used to control the model outputs. Read the
    documentation from [`PretrainedConfig`] for more information.
    Arguments:
        vocab_size (`int`, *optional*, defaults to 32128):
            Vocabulary size of the Pop2Piano model. Defines the number of different tokens that can be represented by the
            `inputs_ids` passed when calling [`Pop2PianoModel`].
        d_model (`int`, *optional*, defaults to 512):
            Size of the encoder layers and the pooler layer.
        d_kv (`int`, *optional*, defaults to 64):
            Size of the key, query, value projections per attention head. `d_kv` has to be equal to `d_model //
            num_heads`.
        d_ff (`int`, *optional*, defaults to 2048):
            Size of the intermediate feed forward layer in each `Pop2PianoBlock`.
        num_layers (`int`, *optional*, defaults to 6):
            Number of hidden layers in the Transformer encoder.
        num_decoder_layers (`int`, *optional*):
            Number of hidden layers in the Transformer decoder. Will use the same value as `num_layers` if not set.
        num_heads (`int`, *optional*, defaults to 8):
            Number of attention heads for each attention layer in the Transformer encoder.
        relative_attention_num_buckets (`int`, *optional*, defaults to 32):
            The number of buckets to use for each attention layer.
        relative_attention_max_distance (`int`, *optional*, defaults to 128):
            The maximum distance of the longer sequences for the bucket separation.
        dropout_rate (`float`, *optional*, defaults to 0.1):
            The ratio for all dropout layers.
        layer_norm_eps (`float`, *optional*, defaults to 1e-6):
            The epsilon used by the layer normalization layers.
        initializer_factor (`float`, *optional*, defaults to 1):
            A factor for initializing all weight matrices (should be kept to 1, used internally for initialization
            testing).
        feed_forward_proj (`string`, *optional*, defaults to `"relu"`):
            Type of feed forward layer to be used. Should be one of `"relu"` or `"gated-gelu"`. Pop2Piano uses the
            `"gated-gelu"` feed forward projection. Original Pop2Piano uses `"relu"`.
        use_cache (`bool`, *optional*, defaults to `True`):
            Whether or not the model should return the last key/values attentions (not used by all models).
    """
    model_type = "pop2piano"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {"hidden_size": "d_model", "num_attention_heads": "num_heads", "num_hidden_layers": "num_layers"}

    def __init__(
        self,
        vocab_size=32128,
        d_model=512,
        d_kv=64,
        d_ff=2048,
        num_layers=6,
        num_decoder_layers=None,
        num_heads=8,
        relative_attention_num_buckets=32,
        relative_attention_max_distance=128,
        dropout_rate=0.1,
        layer_norm_epsilon=1e-6,
        initializer_factor=1.0,
        feed_forward_proj="relu",
        is_encoder_decoder=True,
        use_cache=True,
        pad_token_id=0,
        eos_token_id=1,
        **kwargs,
    ):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.d_kv = d_kv
        self.d_ff = d_ff
        self.num_layers = num_layers
        self.num_decoder_layers = (
            num_decoder_layers if num_decoder_layers is not None else self.num_layers
        )  # default = symmetry
        self.num_heads = num_heads
        self.relative_attention_num_buckets = relative_attention_num_buckets
        self.relative_attention_max_distance = relative_attention_max_distance
        self.dropout_rate = dropout_rate
        self.layer_norm_epsilon = layer_norm_epsilon
        self.initializer_factor = initializer_factor
        self.feed_forward_proj = feed_forward_proj
        self.use_cache = use_cache

        act_info = self.feed_forward_proj.split("-")
        self.dense_act_fn = act_info[-1]
        self.is_gated_act = act_info[0] == "gated"

        if len(act_info) > 1 and act_info[0] != "gated" or len(act_info) > 2:
            raise ValueError(
                f"`feed_forward_proj`: {feed_forward_proj} is not a valid activation function of the dense layer."
                "Please make sure `feed_forward_proj` is of the format `gated-{ACT_FN}` or `{ACT_FN}`, e.g. "
                "'gated-gelu' or 'relu'"
            )

        # for backwards compatibility
        if feed_forward_proj == "gated-gelu":
            self.dense_act_fn = "gelu_new"

        super().__init__(
            pad_token_id=pad_token_id,
            eos_token_id=eos_token_id,
            is_encoder_decoder=is_encoder_decoder,
            **kwargs,
        )

class Pop2PianoProcessorConfig(PretrainedConfig):
    """
    This is the configuration class to store the configuration of a [`Pop2PianoProcessor`]
    """
    def __init__(self,
                 vocab_size_special:int = 4,
                 vocab_size_note:int = 128,
                 vocab_size_velocity:int = 2,
                 vocab_size_time: int = 100,
                 dataset_target_length:int = 256,
                 dataset_input_length:int = 1024,
                 dataset_n_bars:int = 2,
                 dataset_sample_rate:int = 22050,
                 dataset_use_mel:bool = True,
                 dataset_mel_is_conditioned:bool = True,
                 **kwargs):
        self.composer_to_feature_token = COMPOSER_TO_FEATURE_TOKEN
        self.dataset = {'target_length': dataset_target_length,
                        'input_length': dataset_input_length,
                        'n_bars': dataset_n_bars,
                        'sample_rate': dataset_sample_rate,
                        'use_mel': dataset_use_mel,
                        'mel_is_conditioned': dataset_mel_is_conditioned
                        }
        self.tokenizer = {'vocab_size':
                                    {'special': vocab_size_special,
                                     'note': vocab_size_note,
                                     'velocity': vocab_size_velocity,
                                     'time': vocab_size_time
                                     }
                         }

