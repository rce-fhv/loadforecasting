import pandas as pd
import numpy as np
import datetime
import torch

# Bring the data into the data format needed by the model
#
class ModelAdapter:

    def __init__(self,
                 public_holidays,
                 train_size,
                 test_size,
                 prediction_history,
                 dev_size = 0,
                 addLaggedPower=True,
                 shuffle_data=False,
                 seed=None,
                 measurement_delay = pd.Timedelta(days=1),
                 sampling_time = pd.Timedelta(hours=1, minutes=0),
                 prediction_rate = pd.Timedelta(days=1),
                 prediction_horizon = pd.Timedelta(days=0, hours=23, minutes=0),
                 ):

        self.prediction_rate = prediction_rate
        self.prediction_horizon = prediction_horizon
        self.sampling_time = sampling_time
        self.prediction_history = pd.Timedelta(hours=prediction_history)
        self.measurement_delay = measurement_delay
        self.public_holidays = public_holidays
        self.addLaggedPower = addLaggedPower
        self.shuffle_data = shuffle_data
        self.train_size = train_size
        self.test_size = test_size
        self.dev_size = dev_size

        # Optionally: Fix the random-seed for reproducibility
        if seed != None:
            np.random.seed(seed)

    def transformData(self, 
                      powerProfiles, 
                      weatherData, 
                      first_prediction_clocktime = datetime.time(0, 0),
                      ):

        # Downsample the profiles (e.g. to a frequency of 1/1h)
        powerProfiles = powerProfiles.resample(self.sampling_time).mean()

        # Get the first and last available timestamps
        self.first_prediction_date = self.getFirstPredictionTimestamp(powerProfiles, first_prediction_clocktime)
        self.last_available_datetime = powerProfiles.index[-1]

        # Convert the power timeseries to a nd-array with format (nr_of_batches, timesteps, outputs)
        Y_all = self.formattingY(powerProfiles)

        # Convert the input features to a nd-array with format (nr_of_batches, timesteps, features)
        X_all = self.formattingX(weatherData, powerProfiles)

        # Split up the data into train, dev, test and modeldata
        X_all, Y_all = self.splitUpData(X_all, Y_all)

        # Normalize all input data and target value
        X_all, Y_all = self.normalizeAll(X_all, Y_all)
        
        # Convert from ndarray to torch tensor
        X_all, Y_all = self.convertToTorchTensor(X_all, Y_all)        
        
        return X_all, Y_all

    def getFirstPredictionTimestamp(self, powerProfiles, first_prediction_clocktime):

        # Calculate the first possible prediction timestamp
        first_timestamp = powerProfiles.index[0] + self.prediction_history + self.prediction_horizon + self.measurement_delay

        # Choose a prediction datetime, which is on the same day as the 'first_timestamp'.
        target_timestamp = pd.Timestamp.combine(first_timestamp.date(), first_prediction_clocktime) \
                    .tz_localize(first_timestamp.tzinfo)

        # Check if the calculated timestamp is before or after the target time
        if target_timestamp < first_timestamp:
            first_prediction_timestamp = target_timestamp + pd.Timedelta(days=1)
        else:
            first_prediction_timestamp = target_timestamp

        return first_prediction_timestamp

    # Convert the input data to the model format.
    # For more informations regarding the shape see model design for this project.
    #
    def formattingX(self, weatherData, powerProfiles=None):

        batch_id = 0
        next_prediction_date = self.first_prediction_date

        # Calculate/define the number of features of X
        nr_of_features = 11
        if self.addLaggedPower == True:
            nr_of_features += 1
        if weatherData is None:
            num_of_weather_features = 6 # Default weather features
        else:
            num_of_weather_features = weatherData.shape[1]
        nr_of_features += num_of_weather_features

        seq_start_time = self.first_prediction_date - self.prediction_history
        seq_end_time = self.first_prediction_date + self.prediction_horizon
        nr_of_timesteps = len(pd.date_range(start=seq_start_time, end=seq_end_time, freq=self.sampling_time))
        X_all = np.zeros(shape=(0, nr_of_timesteps, nr_of_features))

        while next_prediction_date + self.prediction_horizon <= self.last_available_datetime:

            # Add a new batch to the X array
            new_values = np.zeros(shape=(1, nr_of_timesteps, nr_of_features))
            X_all = np.concatenate((X_all, new_values), axis=0)

            # Define the current time range
            start_datetime = next_prediction_date - self.prediction_history
            end_of_prediction = next_prediction_date + self.prediction_horizon
            total_input_range = pd.date_range(start=start_datetime, end=end_of_prediction, freq=self.sampling_time)

            # Get the current weekday indices [0 ... 6] of all nr_of_timesteps.
            # The shape of the following variable is (nr_of_timesteps, 1).
            weekday_numbers = total_input_range.weekday.values
            
            # Identify public holidays and replace that day with Sunday
            public_holiday_indices = total_input_range.floor("D").isin(self.public_holidays)
            weekday_numbers[public_holiday_indices] = 6

            # Create a one-hot encoding array with shape (nr_of_timesteps, 7).
            one_hot_encoding = np.eye(7)[weekday_numbers]
            index = 7
            X_all[batch_id, :, :index] = one_hot_encoding

            # Convert clock_time to cyclical features
            hour_sin = np.sin(2 * np.pi * total_input_range.hour / 24.0)
            hour_cos = np.cos(2 * np.pi * total_input_range.hour / 24.0)
            X_all[batch_id, :, index]  = hour_sin
            index += 1
            X_all[batch_id, :, index]  = hour_cos
            index += 1

            # Convert day-of-year to cyclical features
            day_of_year_sin = np.sin(2 * np.pi * total_input_range.day_of_year / 366)
            day_of_year_cos = np.cos(2 * np.pi * total_input_range.day_of_year / 366)
            X_all[batch_id, :, index]  = day_of_year_sin
            index += 1
            X_all[batch_id, :, index]  = day_of_year_cos
            index += 1

            # Optionally add lagged profiles
            if self.addLaggedPower == True:                
                start = next_prediction_date - self.prediction_history - self.prediction_horizon - self.measurement_delay
                end = next_prediction_date - self.measurement_delay
                lagged_power = powerProfiles.loc[start:end]
                X_all[batch_id, :, index]  = np.array(lagged_power.values)
                index += 1

            # If available: Add past weather measurmenents to the model input
            if weatherData is not None:
                weatherData_slice = weatherData.loc[start_datetime:next_prediction_date]
                weather_seq_len = weatherData_slice.shape[0]
                for feature in weatherData_slice.columns:
                    X_all[batch_id, :weather_seq_len, index]  = weatherData_slice[feature][:]
                    index += 1
            else:
                X_all[batch_id, :, index:num_of_weather_features]  = 0.0
                index += num_of_weather_features

            # Go to the next prediction (= batch)
            next_prediction_date += self.prediction_rate
            batch_id += 1

        return X_all
    
    # Convert the given power profiles to the model format.
    # For more informations regarding the shape see model design for this project.
    #
    def formattingY(self, df):
        
        batch_id = 0
        next_prediction_date = self.first_prediction_date

        # Calculate/define the shape of Y
        seq_end_time = self.first_prediction_date + self.prediction_horizon
        nr_of_timesteps = len(pd.date_range(start=self.first_prediction_date, end=seq_end_time, freq=self.sampling_time))
        Y_all = np.zeros(shape=(0, nr_of_timesteps, 1))

        while next_prediction_date + self.prediction_horizon <= self.last_available_datetime:
            
            # Add a new batch to the Y array
            new_values = np.zeros(shape=(1, nr_of_timesteps, 1))
            Y_all = np.concatenate((Y_all, new_values), axis=0)

            # Get values within the specified time range
            end_prediction_horizon = next_prediction_date + self.prediction_horizon
            demandprofile_slice = df.loc[next_prediction_date:end_prediction_horizon]
            
            # Set all target power values
            Y_all[batch_id, :, 0] = demandprofile_slice

            # Go to the next prediction (= batch)
            next_prediction_date += self.prediction_rate
            batch_id += 1

        return Y_all

    # Convert from nd-array to torch tensor
    #
    def convertToTorchTensor(self, X_all, Y_all):        
        
        for dataset in X_all:
            X_all[dataset] = torch.tensor(X_all[dataset])       
             
        for dataset in Y_all:
            Y_all[dataset] = torch.tensor(Y_all[dataset])
            
        return X_all, Y_all
        
    # Normalize all the inputs and targets of the model.
    #
    def normalizeAll(self, X_all, Y_all):
        
        X_all['train'] = self.normalizeX(X_all['train'], training=True)
        Y_all['train'] = self.normalizeY(Y_all['train'], training=True)
        X_all['dev'] = self.normalizeX(X_all['dev'], training=False)
        Y_all['dev'] = self.normalizeY(Y_all['dev'], training=False)
        X_all['test'] = self.normalizeX(X_all['test'], training=False)
        Y_all['test'] = self.normalizeY(Y_all['test'], training=False)
        X_all['all'] = self.normalizeX(X_all['all'], training=False)
        Y_all['all'] = self.normalizeY(Y_all['all'], training=False)
        
        return X_all, Y_all
        
    # Z-Normalize the input data of the model.
    #
    def normalizeX(self, X, training=False):

        if training:
            # Estimate the mean and standard deviation of the data during training
            self.meanX = np.mean(X, axis=(0, 1))
            self.stdX = np.std(X, axis=(0, 1))
        
            if np.isclose(self.stdX, 0).any():
                # Avoid a division by zero (which can occur for constant features)
                self.stdX = np.where(np.isclose(self.stdX, 0), 1e-8, self.stdX)

        X_normalized = (X - self.meanX) / self.stdX

        return X_normalized

    # Undo z-normalization
    #
    def deNormalizeX(self, X):

        X_denormalized = (X * self.stdX) + self.meanX

        return X_denormalized

    # Normalize the output data of the model.    
    #
    def normalizeY(self, Y, training=False):

        if training:
            # Estimate the standard deviation of the data during training
            self.stdY = np.std(Y)
        
        if np.isclose(self.stdY, 0):
            assert False, "Normalization leads to division by zero."

        Y_normalized = Y / self.stdY

        return Y_normalized

    # Undo normalization
    #
    def deNormalizeY(self, Y):

        Y_denormalized = Y * self.stdY

        return Y_denormalized
    
    # Split up the data into train-, dev- and test-set
    #
    def splitUpData(self, X_all, Y_all):

        # Optionally shuffle all indices
        total_samples = X_all.shape[0]
        self.shuffeled_indices = np.arange(total_samples)
        if self.shuffle_data == True:
            np.random.shuffle(self.shuffeled_indices)

        # Do train-dev-test data split
        #
        # --------------> time axis
        #
        #  -------------------------------------------------
        # | un-used |      train  |   dev   |    test       |
        # |-----------------------|---------|---------------|
        # |         |  X['train'] | X['dev']|  X['test']    |
        # |         |  Y['train'] | Y['dev']|  Y['test']    |
        # ---------------------------------------------------
        # |       X['all'] (entire timeseries)              |
        # |       Y['all'] (entire timeseries)              |
        # -------------------------------------------------- 
        X, Y = {}, {}
        self.total_set_size = X_all.shape[0]
        self.test_set_start = self.total_set_size - self.test_size
        self.dev_set_start = self.test_set_start - self.dev_size
        if self.train_size != -1:
            self.train_set_start = self.dev_set_start - self.train_size
        else:
            self.train_set_start = None # Set train length to max
        
        X['test'] = X_all[self.shuffeled_indices[self.test_set_start:]]
        X['dev'] = X_all[self.shuffeled_indices[self.dev_set_start:self.test_set_start]]
        X['train'] = X_all[self.shuffeled_indices[self.train_set_start:self.dev_set_start]]
        X['all'] = X_all[:]
        
        Y['test'] = Y_all[self.shuffeled_indices[self.test_set_start:]]
        Y['dev'] = Y_all[self.shuffeled_indices[self.dev_set_start:self.test_set_start]]
        Y['train'] = Y_all[self.shuffeled_indices[self.train_set_start:self.dev_set_start]]
        Y['all'] = Y_all[:]

        return X, Y

    # Return the unshuffled index in all data that corresponds to the given
    # dataset_tye and index.
    #
    def getUnshuffeledIndex(self, dataset_type, index):

        # Shuffled data
        if dataset_type == 'train':
            unshuffled_index = self.shuffeled_indices[index + self.train_set_start]
        elif dataset_type == 'dev':
            unshuffled_index = self.shuffeled_indices[index + self.dev_set_start]
        elif dataset_type == 'test':
            unshuffled_index = self.shuffeled_indices[index + self.test_set_start]
        else:
            assert False, "Unexpected 'dataset_type' parameter received."

        return unshuffled_index

    # Return the prediction date that corresponds to the given
    # dataset_tye and index.
    #
    def getStartDateFromIndex(self, dataset_type, index):        

        if dataset_type != 'all':
            index = self.getUnshuffeledIndex(dataset_type, index)

        return self.first_prediction_date + index * self.prediction_rate
    
    # Return the dataset-type (train, test, ...) from the given unshuffeled index
    #
    def getDatasetTypeFromIndex(self, unshuffeled_index):

        shuffled_index = np.where(self.shuffeled_indices == unshuffeled_index)[0][0]

        if shuffled_index >= self.total_set_size:
            dataset_type = 'unknown (error)'
        elif shuffled_index >= self.test_set_start:
            dataset_type = 'test'
        elif shuffled_index >= self.dev_set_start:
            dataset_type = 'dev'
        elif shuffled_index >= self.train_set_start:
            dataset_type = 'train'
        else:
            dataset_type = 'un-used'

        return dataset_type

if __name__ == '__main__':
    pass

