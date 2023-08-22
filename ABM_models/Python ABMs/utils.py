import numpy as np
from xrspatial  import focal
from xrspatial.utils import ngjit
import seaborn as sns
import matplotlib.pyplot as plt
import utils

def create_meteo_weightmatrix(params, windspeed, winddirection, temperature, rain, temp_diff):         
    # order params: windsp_disp_coeff, dispar_intercept, prate ,temp_coeff, rain_coeff, localV_mod, dispar2_coeff, temp_diff_coeff, windsp_coeff
    prop_rate = params[2] + (params[3] * temperature) + (params[4] * rain) + (params[7] * temp_diff) + (params[8] * windspeed)
    disparity_factor = params[1] + (params[0] * windspeed)
    disparity_factor2 = params[6] * disparity_factor
    weight_matrix = np.full((5, 5), prop_rate)
    
    if winddirection <= 191.25:
        if 11.25 <= winddirection <= 348.75:
            weight_matrix[0:3, 1:4] = prop_rate * disparity_factor2
            weight_matrix[0:2, 2:3] = prop_rate * disparity_factor
            weight_matrix[3, 1:4] = prop_rate / disparity_factor2
            weight_matrix[4, :] = prop_rate / disparity_factor2
            weight_matrix[3:5, 2:3] = prop_rate / disparity_factor
        elif 33.75 <= winddirection <= 11.25:
            weight_matrix[0, 2:5] = prop_rate * disparity_factor2
            weight_matrix[1, 1:5] = prop_rate * disparity_factor2
            weight_matrix[2, 3] = prop_rate * disparity_factor2
            weight_matrix[0, 3] = prop_rate * disparity_factor
            weight_matrix[1, 2:3] = prop_rate * disparity_factor
            weight_matrix[4, 0:3] = prop_rate / disparity_factor2
            weight_matrix[3, 0:4] = prop_rate / disparity_factor2
            weight_matrix[2, 1] = prop_rate / disparity_factor2
            weight_matrix[3, 1:2] = prop_rate / disparity_factor
            weight_matrix[4, 1] = prop_rate / disparity_factor
        # ... Similarly handle other cases of winddirection ranges
        
    else:
        if 213.75 <= winddirection <= 191.25:
            weight_matrix[4, 0:3] = prop_rate * disparity_factor2
            weight_matrix[3, 0:4] = prop_rate * disparity_factor2
            weight_matrix[2, 1] = prop_rate * disparity_factor2
            weight_matrix[3, 1:2] = prop_rate * disparity_factor
            weight_matrix[4, 1] = prop_rate * disparity_factor
            weight_matrix[0, 2:5] = prop_rate / disparity_factor2
            weight_matrix[1, 1:5] = prop_rate / disparity_factor2
            weight_matrix[2, 3] = prop_rate / disparity_factor2
            weight_matrix[0, 3] = prop_rate / disparity_factor
            weight_matrix[1, 2:3] = prop_rate / disparity_factor
        # ... Similarly handle other cases of winddirection ranges
    
    weight_matrix[2, 2] = params[5] / disparity_factor
    return weight_matrix


def monthly_mean_matrix(month, params, dailyWeather):
    monthly_matrices = []
    indices = np.where(dailyWeather["month"] == month)[0]
    for x in indices:
        matrix = create_meteo_weightmatrix(params,dailyWeather["Windspeed"][x], dailyWeather["Winddirection"][x],
                                           dailyWeather["Temperature"][x], dailyWeather["Rain"][x],
                                           dailyWeather["TempDifference"][x])
        monthly_matrices.append(matrix)
    return(np.asarray(np.mean(monthly_matrices, axis=0)))



def adjust_diff_moderators(rasterset, params, moderator_df):
    values = np.asarray(rasterset[:]).flatten()
    GreenCover = moderator_df["GreenCover"].fillna(0)
    openspace_fraction = moderator_df["openspace_fraction"].fillna(0)
    NrTrees = moderator_df["NrTrees"].fillna(0)
    building_height = moderator_df["building_height"].fillna(0)
    neigh_height_diff = moderator_df["neigh_height_diff"].fillna(0)
    result = values *  (params[0] + (params[1] * GreenCover) + (params[2] * openspace_fraction) +
                       (params[3] * NrTrees) + (params[4] * building_height) + 
                       (params[5] * neigh_height_diff))
    return result

def provide_adjuster( params, moderator_df):
    GreenCover = moderator_df["GreenCover"].fillna(0)
    openspace_fraction = moderator_df["openspace_fraction"].fillna(0)
    NrTrees = moderator_df["NrTrees"].fillna(0)
    building_height = moderator_df["building_height"].fillna(0)
    neigh_height_diff = moderator_df["neigh_height_diff"].fillna(0)
    return (params[0] + (params[1] * GreenCover) + (params[2] * openspace_fraction) +
                       (params[3] * NrTrees) + (params[4] * building_height) + 
                       (params[5] * neigh_height_diff))



def cellautom_dispersion(weightmatrix, airpollraster, monthlyweather, moderator_df, include_baseline_in_dispersion,baseline_NO2, params):
    @ngjit    
    def weightedaverage(kernel_data):
        # print(np.multiply(kernel_data, weightmatrix),round((np.nansum(np.multiply(kernel_data, weightmatrix))/np.nansum(weightmatrix)),10), round(np.nanmean(np.multiply(kernel_data, weightmatrix)),10))
        return round((np.nansum(np.multiply(kernel_data, weightmatrix))/np.nansum(weightmatrix)),10)
        # return round(np.nanmean(np.multiply(kernel_data, weightmatrix)),10)
    nr_repeats = params[13] + (params[17] * monthlyweather["Windspeed"]) + \
                (params[18] * monthlyweather["Temperature"]) + \
                (params[19] * monthlyweather["TempDifference"])
    print(nr_repeats)
    for i in range(int(nr_repeats.iloc[0])):
            airpollraster[:] =  focal.apply(raster = airpollraster, kernel= np.full((5, 5), 1), func= weightedaverage)
    airpollraster[:] = np.array(adjust_diff_moderators(airpollraster, params[6:12], moderator_df).fillna(0)).reshape(airpollraster.shape)
    if include_baseline_in_dispersion == False:
        airpollraster[:] = np.array(np.asarray(airpollraster[:]).flatten() + (params[12] * baseline_NO2)).reshape(airpollraster.shape)
    return(airpollraster)



def cellautom_dispersion_adjuster(weightmatrix, airpollraster, nr_repeats, adjuster, include_baseline_in_dispersion,baseline_NO2, params):
    @ngjit    
    def weightedaverage(kernel_data):
        # print(np.multiply(kernel_data, weightmatrix), round((np.nansum(np.multiply(kernel_data, weightmatrix))/np.nansum(weightmatrix)),10), round(np.nanmean(np.multiply(kernel_data, weightmatrix)),10))
        return round((np.nansum(np.multiply(kernel_data, weightmatrix))/np.nansum(weightmatrix)),10)
        # return round(np.nanmean(np.multiply(kernel_data, weightmatrix)),10)
    for i in range(int(nr_repeats)):
            airpollraster[:] =  focal.apply(raster = airpollraster, kernel= np.full((5, 5), 1), func= weightedaverage)
    airpollraster[:] = np.array((np.asarray(airpollraster[:]).flatten() * adjuster).fillna(0)).reshape(airpollraster.shape)
    if include_baseline_in_dispersion == False:
        airpollraster[:] = np.array(np.asarray(airpollraster[:]).flatten() + (params[12] * baseline_NO2)).reshape(airpollraster.shape)
    return(airpollraster)

def cellautom_dispersion_noadjuster(weightmatrix, airpollraster, monthlyweather,  include_baseline_in_dispersion,baseline_NO2, params):
    @ngjit    
    def weightedaverage(kernel_data):
        return round(np.nanmean(np.multiply(kernel_data, weightmatrix)),10)
    nr_repeats = params[13] + (params[17] * monthlyweather["Windspeed"]) + \
                (params[18] * monthlyweather["Temperature"]) + \
                (params[19] * monthlyweather["TempDifference"])
    for i in range(int(nr_repeats)):
            airpollraster[:] =  focal.apply(raster = airpollraster, kernel= np.full((5, 5), 1), func= weightedaverage)
    if include_baseline_in_dispersion == False:
        airpollraster[:] = np.array(np.asarray(airpollraster[:]).flatten() + (params[12] * baseline_NO2)).reshape(airpollraster.shape)
    return(airpollraster)

