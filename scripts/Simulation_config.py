# This file contains the configuration for an automated simulation run.
#

from collections import namedtuple

class DoPretraining():
    YES = True      # <= Baseline
    NO = False

class DoTransferLearning():
    YES = True      # <= Baseline
    NO = False

class ModelSize():
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"      # <= Baseline
    LARGE = "LARGE"

class Aggregation_Count():
    _1_HOUSEHOLD    = 'data/london_loadprofiles_1household_each.pkl'
    _10_HOUSEHOLDS  = 'data/london_loadprofiles_10households_each.pkl'
    _37_HOUSEHOLDS  = 'data/london_loadprofiles_37households_each.pkl'
    _74_HOUSEHOLDS  = 'data/london_loadprofiles_74households_each.pkl'  # <= Baseline

class NrOfComunities():
    _10 = 10
    _20 = 20      # <= Baseline

class TrainingHistory():
    _1_MONTH = 30
    _2_MONTH = 61
    _4_MONTH = 122
    _6_MONTH = 183
    _9_MONTH = 275
    _12_MONTH = 365
    _15_MONTH = 466      # <= Baseline

class ModelInputHistory():
    _1_DAY = 24     # <= Baseline
    _6_DAYS = 24*6
    _20_DAYS = 24*20

class UsedModels():
    ALL = ('SyntheticLoadProfile', 'KNN', 'PersistencePrediction', 'xLSTM', 'LSTM', 'Transformer', )

class Epochs():
    SMOKE_TEST = 1
    DEFAULT = 100     # <= Baseline

# Define all possible run settings
run_settings = ['modelSize', 'doPretraining', 'doTransferLearning', 'aggregation_Count', 'nrOfComunities', 
                'trainingHistory', 'modelInputHistory', 'usedModels', 'epochs']
Config_of_one_run = namedtuple('Config_of_one_run', run_settings)


#########################################################################################################################
# Create test config for all simulation runs
#########################################################################################################################
configs = [
    # Baseline
    Config_of_one_run(ModelSize.MEDIUM, DoPretraining.YES, DoTransferLearning.YES, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
            TrainingHistory._15_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    
#     # Vary the model sizes
#     Config_of_one_run(ModelSize.SMALL, DoPretraining.YES, DoTransferLearning.YES, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
#             TrainingHistory._15_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
#     Config_of_one_run(ModelSize.LARGE, DoPretraining.YES, DoTransferLearning.YES, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
#             TrainingHistory._15_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),

#     # Vary the community sizes
#     Config_of_one_run(ModelSize.MEDIUM, DoPretraining.YES, DoTransferLearning.YES, Aggregation_Count._1_HOUSEHOLD, NrOfComunities._20, 
#             TrainingHistory._15_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
#     Config_of_one_run(ModelSize.MEDIUM, DoPretraining.YES, DoTransferLearning.YES, Aggregation_Count._10_HOUSEHOLDS, NrOfComunities._20, 
#             TrainingHistory._15_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
#     Config_of_one_run(ModelSize.MEDIUM, DoPretraining.YES, DoTransferLearning.YES, Aggregation_Count._74_HOUSEHOLDS, NrOfComunities._20, 
#             TrainingHistory._15_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    
    # Vary the train set size
    Config_of_one_run(ModelSize.MEDIUM, DoPretraining.YES, DoTransferLearning.YES, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
            TrainingHistory._1_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    Config_of_one_run(ModelSize.MEDIUM, DoPretraining.YES, DoTransferLearning.YES, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
            TrainingHistory._2_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    Config_of_one_run(ModelSize.MEDIUM, DoPretraining.YES, DoTransferLearning.YES, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
            TrainingHistory._4_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    Config_of_one_run(ModelSize.MEDIUM, DoPretraining.YES, DoTransferLearning.YES, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
            TrainingHistory._6_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    Config_of_one_run(ModelSize.MEDIUM, DoPretraining.YES, DoTransferLearning.YES, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
            TrainingHistory._9_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    Config_of_one_run(ModelSize.MEDIUM, DoPretraining.YES, DoTransferLearning.YES, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
            TrainingHistory._12_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    
#     # Vary the input history size
#     Config_of_one_run(ModelSize.MEDIUM, DoPretraining.YES, DoTransferLearning.YES, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
#             TrainingHistory._15_MONTH, ModelInputHistory._6_DAYS, UsedModels.ALL, Epochs.DEFAULT),    
#     Config_of_one_run(ModelSize.MEDIUM, DoPretraining.YES, DoTransferLearning.YES, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
#             TrainingHistory._15_MONTH, ModelInputHistory._20_DAYS, UsedModels.ALL, Epochs.DEFAULT),    
    
    # Without transfer learning:
    #
    Config_of_one_run(ModelSize.MEDIUM, DoPretraining.NO, DoTransferLearning.NO, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
            TrainingHistory._15_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    
#     # Vary the model sizes
#     Config_of_one_run(ModelSize.SMALL, DoPretraining.NO, DoTransferLearning.NO, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
#             TrainingHistory._15_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
#     Config_of_one_run(ModelSize.LARGE, DoPretraining.NO, DoTransferLearning.NO, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
#             TrainingHistory._15_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),

#     # Vary the community sizes
#     Config_of_one_run(ModelSize.MEDIUM, DoPretraining.NO, DoTransferLearning.NO, Aggregation_Count._1_HOUSEHOLD, NrOfComunities._20, 
#             TrainingHistory._15_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
#     Config_of_one_run(ModelSize.MEDIUM, DoPretraining.NO, DoTransferLearning.NO, Aggregation_Count._10_HOUSEHOLDS, NrOfComunities._20, 
#             TrainingHistory._15_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
#     Config_of_one_run(ModelSize.MEDIUM, DoPretraining.NO, DoTransferLearning.NO, Aggregation_Count._74_HOUSEHOLDS, NrOfComunities._20, 
#             TrainingHistory._15_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    
    # Vary the train set size
    Config_of_one_run(ModelSize.MEDIUM, DoPretraining.NO, DoTransferLearning.NO, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
            TrainingHistory._1_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    Config_of_one_run(ModelSize.MEDIUM, DoPretraining.NO, DoTransferLearning.NO, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
            TrainingHistory._2_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    Config_of_one_run(ModelSize.MEDIUM, DoPretraining.NO, DoTransferLearning.NO, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
            TrainingHistory._4_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    Config_of_one_run(ModelSize.MEDIUM, DoPretraining.NO, DoTransferLearning.NO, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
            TrainingHistory._6_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    Config_of_one_run(ModelSize.MEDIUM, DoPretraining.NO, DoTransferLearning.NO, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
            TrainingHistory._9_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    Config_of_one_run(ModelSize.MEDIUM, DoPretraining.NO, DoTransferLearning.NO, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
            TrainingHistory._12_MONTH, ModelInputHistory._1_DAY, UsedModels.ALL, Epochs.DEFAULT),
    
#     # Vary the input history size
#     Config_of_one_run(ModelSize.MEDIUM, DoPretraining.NO, DoTransferLearning.NO, Aggregation_Count._37_HOUSEHOLDS, NrOfComunities._20, 
#             TrainingHistory._15_MONTH, ModelInputHistory._6_DAYS, UsedModels.ALL, Epochs.DEFAULT), 
]
#########################################################################################################################
