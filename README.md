# Guidelines of the project.

## Outline of the project.

## Notebooks.

We chose to use notebooks for a better presentation and understanding of both our workflow and our results. Besides, notebooks are very convenient for working remotely on a server, thanks to its web-browser development interface.

Notebooks provide a way to explore and experiment simultaneously different tracks or improvement on the project.

- `Low regime intervals.ipynb` - To visualize the cycles of the pump.

- `Exploring the metrics to detect anomalies.ipynb` - in particular fourier analysis for oscillation detection.

- `Predicting the steps transitions(1 and 2).ipynb` - two separate analysis that follow the work on early signals for predicting abrupt changes in the data. There was no result concurring to this study, which can be explained, as it has been discussed, by the fact that the steps anomalies cannot be associated to regime changes.

- `Neural Network ... .ipynb` - a experimental work on neural networks. See [dedicated paragraph.](#neural-network-experiments)

- `Supervised anomaly detection.ipynb` - our current pipeline for extracting anomalies.

## Implementation.

The `constants.py` file is  to group logically the name of physical variables. This nomenclature makes it easier to work both horizontally and vertically: 

    -  Horizontally, with the sensors of the same type (flow leakage, temperature,...). 
    
    -  Vertically, with the sensors of the same loop in the pump - there are 4 loops.

The `Observation` class responsibility is to:

- Import all the data from sensors corresponding to a single pump on one site.

- Deal with missing values (aka. 32760)

- Identify the cycles of the pump.

The `Interval` class responsibility is to:

- Deal with array of time intervals.

The `Scale` class responsibility is to:

- Resample the dataframe, in case we want to compute features at different scales.

The `Feature` class responsibility is to:

- Score a certain feature given a dataframe. These features can be used afterwards to determine the type of anomalies we are delaing with (a step, a trend, a spike, oscillation, ...)

The `ScoreAnalysis` class responsibility is to:

- Analyse a time series which correspond to the score (likelihood) of an anomaly: We extract features to deduce anomalies - for instance, we extract the slope to deduce a critical increasing trend. 
        
    
### Dealing with missing values

The process:

- Identify all the missing values.

- Group them if there are consecutive. Two cases arise:

    - The group is small (less than 1 hour), we can impute missing values, considering the values before and after.
    
    - The group is large. For some sensors, we sometimes have weeks or even months of missing values. Imputation is impossible or absurd. We have therefore two solutions:
    
        1. Remove the data for all sensors on the same interval.
        
        2. Keep the data. We ignore the missing values.

- Identify the cycles of the pump with a threshold. To that aim, we:

    - Set a threshold to sensor DEB1- (<200 L.h<sup>-1</sup>)
    
    - Group the consecutive timestamps to get the exact intervals. Yields around ~1 interval per year.
    
**NB:** The accurate cycle identification is actually a little more complicated. [Explication below.](#cycle-identification)


### Cycle identification

The pipeline for extracting the cycles is as follows:

- Set a threshold to sensor DEB1- (<200 L.h<sup>-1</sup>) and we group timestamps to get intervals according to a maximum time lapse. We chose to take a large time lapse of 15 days, meaning that, any <200 L.h<sup>-1</sup> timestamps closer than 15 days will be merged and be considered as part of the same interval (cycle).

- These intervals supposedly represent a "low regime" where the power is almost always very close to 0, and the flow sensors (DEB-1/../4) are under 200 L.h<sup>-1</sup>. However, there are sometimes **split because of missing values**. 

- To bridge these undesired gaps, we merge this low regime intervals, with the missing value intervals **on the condition that they overlap**, because we don't want to merge missing value intervals that are outside of this range. 

- There might still remain **isolated timestamps** where the DEB1- value goes under 200 L.h<sup>-1</sup>, but these don't correspond to any low regime intervals. They are just **spikes that need to be filtered out** of our interval extraction.

- Finally, if some "low regime intervals" are close enough but not yet merge, (by a length of 1 month), we merge them.


### Analysing the score anomalies

The process:

- We first filter the values according to a threshold of interest.
    
- We then only consider the local extrema.

- We finally remove extrema that are too close in time, by selecting the best score.

### Combining results at different scales

To that effect, the function `combine` (see `tools.py`) is used, and its inner workings are detailed as comments in the implementation.

In broad strokes, the function takes as input dataframes that represent anomaly scores. Each score has a certain "scope of influence" on the other scores. If an anomaly score is high, and **other anomaly scores in its scope are lower**, they are **discarded**. Conversely, if this score **is in the scope of an anomaly that is higher**, it is discarded itself.
 
This way we prevent overlapping of the same anomaly type at different scales.

*Note:* The function can also artificially be used **to disambiguate the steps from the trend**, and discard the "false positive" trend anomalies.

### Neural network experiments

So far, we tried a supervised method, where we extract features, create score, and then identify extrema as anomalies.

Unfortunately, this strategy might not successfully isolate some other unseen-before anomalies. We therefore focus here on an unsupervised method for detecting them: in particular, we try to "encode" the multivariate time series to a lower dimension by reducing its dimensionality. Afterwards, we "decode" the series and try to reconstruct it from that lower dimensional space. 

The reconstruction error, between the original and the "encoded-decoded" data,  part is **a good indicator for anomalies**. Indeed, the underlying features of the encoded data are best learnt for data points that belong to a cluster, or at least that are not isolated.

Among the many dimensionality reduction algorithms, the most common is PCA. However, Neural Network Autoencoders have also proven to be very efficient.

- To analyse the quality of a given network, we provide our dimensionality reduction as an input for the classification task on a widely used benchmark for time series - the UCR benchmark.

- After finding a convenient network for encoding time series, we experiment it on our data, and **rank the anomalies according to the reconstruction error**.