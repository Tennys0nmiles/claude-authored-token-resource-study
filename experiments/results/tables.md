
### A_compute: % of loss gap recovered at each budget (mean of 5 doc splits)

|                                                    |   R@2% |   R@5% |   R@10% |   R@20% |   R@30% |   R@50% | budget for 50% of gap   |
|:---------------------------------------------------|-------:|-------:|--------:|--------:|--------:|--------:|:------------------------|
| ('code', '1 - max prob (CALM-style)')              |    5   |   13.5 |    25.9 |    46.5 |    62.7 |    84.3 | 22.0% ± 0.7             |
| ('code', 'entropy (BLT-style)')                    |    6.3 |   13.5 |    25.6 |    46.9 |    64.1 |    86.5 | 21.6% ± 0.7             |
| ('code', 'layer-6 to layer-12 change')             |    3   |    7.9 |    16.3 |    32.9 |    47.7 |    70.6 | 31.8% ± 0.9             |
| ('code', 'learned: raw surprise')                  |    4.6 |   12.8 |    24.7 |    46.2 |    63.7 |    85.9 | 22.1% ± 0.5             |
| ('code', 'learned: value (KL)')                    |    8.2 |   17.6 |    30.9 |    51   |    66.7 |    86   | 19.5% ± 0.6             |
| ('code', 'learned: value (KL), scalars only')      |    6.3 |   14   |    26.4 |    47.8 |    64.4 |    86.6 | 21.2% ± 0.7             |
| ('code', 'learned: value (realized gain)')         |    8.1 |   17.4 |    30.3 |    50.6 |    65.3 |    84.8 | 19.7% ± 0.9             |
| ('code', 'oracle: KL (needs resource)')            |   13.4 |   26.6 |    42.6 |    64.7 |    79.2 |    94.6 | 13.1% ± 0.5             |
| ('code', 'oracle: realized gain')                  |   24   |   45.7 |    70.3 |    99.3 |   113.2 |   121.6 | 5.7% ± 0.1              |
| ('code', 'random')                                 |    1.9 |    5   |    10   |    19.9 |    29.8 |    50.5 | 49.5% ± 1.0             |
| ('natural', '1 - max prob (CALM-style)')           |    3.8 |   10.3 |    20.5 |    38.2 |    53.6 |    77.8 | 27.5% ± 0.3             |
| ('natural', 'entropy (BLT-style)')                 |    4.4 |   10.6 |    20.8 |    39.4 |    55   |    79.1 | 26.5% ± 0.4             |
| ('natural', 'layer-6 to layer-12 change')          |    2.3 |    6.4 |    13.7 |    27.5 |    39.3 |    62   | 39.5% ± 0.6             |
| ('natural', 'learned: raw surprise')               |    3.7 |    9.5 |    19.8 |    38   |    53.7 |    79   | 27.6% ± 0.3             |
| ('natural', 'learned: value (KL)')                 |    6.4 |   14.5 |    25.4 |    43.8 |    59   |    80.6 | 23.8% ± 0.4             |
| ('natural', 'learned: value (KL), scalars only')   |    4.8 |   10.9 |    21.5 |    40.4 |    55.9 |    79.5 | 26.0% ± 0.5             |
| ('natural', 'learned: value (realized gain)')      |    6.3 |   13.9 |    24.6 |    42.9 |    57.6 |    79.2 | 24.5% ± 0.9             |
| ('natural', 'oracle: KL (needs resource)')         |   11.7 |   22.7 |    36.5 |    56.2 |    70.9 |    89.6 | 16.8% ± 0.2             |
| ('natural', 'oracle: realized gain')               |   20.6 |   40.2 |    63.3 |    92.6 |   109   |   121.6 | 6.9% ± 0.1              |
| ('natural', 'random')                              |    2   |    5.1 |    10.1 |    20.1 |    30.1 |    50.4 | 49.6% ± 0.5             |
| ('prose', '1 - max prob (CALM-style)')             |    3   |    8.1 |    16.7 |    33   |    46.7 |    70   | 32.5% ± 0.4             |
| ('prose', 'entropy (BLT-style)')                   |    3.2 |    8.2 |    17   |    34.4 |    48.3 |    72   | 31.2% ± 0.4             |
| ('prose', 'layer-6 to layer-12 change')            |    1.6 |    4.5 |    10.3 |    21.6 |    32.8 |    54.7 | 45.4% ± 0.4             |
| ('prose', 'learned: raw surprise')                 |    3.1 |    8   |    16.3 |    33.1 |    47.2 |    71.3 | 32.1% ± 0.5             |
| ('prose', 'learned: value (KL)')                   |    4.8 |   11   |    20.4 |    37.5 |    52   |    73.7 | 28.5% ± 0.8             |
| ('prose', 'learned: value (KL), scalars only')     |    3.2 |    8.3 |    17.3 |    34.3 |    48.9 |    72.2 | 30.8% ± 0.4             |
| ('prose', 'learned: value (realized gain)')        |    4.3 |   10.5 |    19.5 |    36   |    50.4 |    72.4 | 29.7% ± 1.0             |
| ('prose', 'oracle: KL (needs resource)')           |    9.9 |   19.1 |    31.2 |    48.5 |    63   |    83.2 | 20.9% ± 0.6             |
| ('prose', 'oracle: realized gain')                 |   17.6 |   35.3 |    56.8 |    85.6 |   103.6 |   120.4 | 8.2% ± 0.1              |
| ('prose', 'random')                                |    2   |    5.1 |    10.2 |    20.3 |    30.2 |    50.2 | 49.8% ± 0.4             |
| ('prose_ids', '1 - max prob (CALM-style)')         |    3.1 |    6.9 |    15   |    30.9 |    44.6 |    68.8 | 34.0% ± 0.5             |
| ('prose_ids', 'entropy (BLT-style)')               |    3.4 |    8.4 |    17.2 |    33.3 |    46.9 |    71   | 32.2% ± 0.5             |
| ('prose_ids', 'layer-6 to layer-12 change')        |    1.8 |    4.9 |    10.3 |    20.8 |    31.5 |    53.7 | 46.7% ± 0.3             |
| ('prose_ids', 'learned: raw surprise')             |    3.2 |    8.4 |    17.1 |    32.6 |    46.3 |    70.3 | 32.9% ± 0.8             |
| ('prose_ids', 'learned: value (KL)')               |    5.1 |   11.5 |    20.9 |    37.2 |    50.8 |    72.5 | 29.3% ± 0.6             |
| ('prose_ids', 'learned: value (KL), scalars only') |    3.5 |    8.4 |    16.7 |    32.7 |    46.5 |    71.2 | 32.6% ± 0.6             |
| ('prose_ids', 'learned: value (realized gain)')    |    4.3 |   10.4 |    19.1 |    35.5 |    49.3 |    71.6 | 30.6% ± 1.9             |
| ('prose_ids', 'oracle: KL (needs resource)')       |   10.1 |   19.1 |    31.2 |    49.2 |    63.6 |    84   | 20.6% ± 0.9             |
| ('prose_ids', 'oracle: realized gain')             |   18.3 |   36.3 |    58.2 |    87.5 |   105.4 |   122.2 | 7.9% ± 0.1              |
| ('prose_ids', 'random')                            |    2.1 |    5.2 |    10.1 |    20   |    29.8 |    50.5 | 49.5% ± 0.3             |


### A_compute: what each policy selects at a 10% budget

|                                                    |   share_id_first |   share_id_repeat |   share_no_gain |   mean_gain |   mean_H_L |
|:---------------------------------------------------|-----------------:|------------------:|----------------:|------------:|-----------:|
| ('code', '1 - max prob (CALM-style)')              |            0     |             0     |           0.244 |       1.351 |      4.011 |
| ('code', 'entropy (BLT-style)')                    |            0     |             0     |           0.249 |       1.339 |      4.225 |
| ('code', 'layer-6 to layer-12 change')             |            0     |             0     |           0.381 |       0.85  |      2.073 |
| ('code', 'learned: raw surprise')                  |            0     |             0     |           0.261 |       1.289 |      4.245 |
| ('code', 'learned: value (KL)')                    |            0     |             0     |           0.211 |       1.613 |      3.267 |
| ('code', 'learned: value (KL), scalars only')      |            0     |             0     |           0.242 |       1.381 |      4.121 |
| ('code', 'learned: value (realized gain)')         |            0     |             0     |           0.204 |       1.582 |      3.049 |
| ('code', 'oracle: KL (needs resource)')            |            0     |             0     |           0.208 |       2.221 |      2.504 |
| ('code', 'oracle: realized gain')                  |            0     |             0     |           0     |       3.672 |      2.553 |
| ('code', 'random')                                 |            0     |             0     |           0.477 |       0.523 |      1.34  |
| ('natural', '1 - max prob (CALM-style)')           |            0     |             0     |           0.254 |       1.196 |      4.598 |
| ('natural', 'entropy (BLT-style)')                 |            0     |             0     |           0.259 |       1.215 |      4.809 |
| ('natural', 'layer-6 to layer-12 change')          |            0     |             0     |           0.377 |       0.803 |      2.05  |
| ('natural', 'learned: raw surprise')               |            0     |             0     |           0.266 |       1.16  |      4.78  |
| ('natural', 'learned: value (KL)')                 |            0     |             0     |           0.223 |       1.485 |      3.568 |
| ('natural', 'learned: value (KL), scalars only')   |            0     |             0     |           0.254 |       1.257 |      4.638 |
| ('natural', 'learned: value (realized gain)')      |            0     |             0     |           0.218 |       1.436 |      3.542 |
| ('natural', 'oracle: KL (needs resource)')         |            0     |             0     |           0.214 |       2.131 |      2.812 |
| ('natural', 'oracle: realized gain')               |            0     |             0     |           0     |       3.701 |      3.025 |
| ('natural', 'random')                              |            0     |             0     |           0.424 |       0.589 |      1.949 |
| ('prose', '1 - max prob (CALM-style)')             |            0     |             0     |           0.264 |       1.091 |      4.921 |
| ('prose', 'entropy (BLT-style)')                   |            0     |             0     |           0.267 |       1.112 |      5.15  |
| ('prose', 'layer-6 to layer-12 change')            |            0     |             0     |           0.382 |       0.673 |      2.05  |
| ('prose', 'learned: raw surprise')                 |            0     |             0     |           0.271 |       1.065 |      5.098 |
| ('prose', 'learned: value (KL)')                   |            0     |             0     |           0.236 |       1.334 |      4.078 |
| ('prose', 'learned: value (KL), scalars only')     |            0     |             0     |           0.266 |       1.133 |      5.068 |
| ('prose', 'learned: value (realized gain)')        |            0     |             0     |           0.236 |       1.275 |      4.131 |
| ('prose', 'oracle: KL (needs resource)')           |            0     |             0     |           0.219 |       2.042 |      3.2   |
| ('prose', 'oracle: realized gain')                 |            0     |             0     |           0     |       3.716 |      3.46  |
| ('prose', 'random')                                |            0     |             0     |           0.364 |       0.667 |      2.625 |
| ('prose_ids', '1 - max prob (CALM-style)')         |            0.149 |             0.006 |           0.302 |       0.92  |      4.987 |
| ('prose_ids', 'entropy (BLT-style)')               |            0.02  |             0.001 |           0.278 |       1.054 |      5.152 |
| ('prose_ids', 'layer-6 to layer-12 change')        |            0.019 |             0.009 |           0.383 |       0.633 |      2.034 |
| ('prose_ids', 'learned: raw surprise')             |            0.019 |             0     |           0.271 |       1.046 |      5.068 |
| ('prose_ids', 'learned: value (KL)')               |            0.034 |             0     |           0.246 |       1.278 |      4.115 |
| ('prose_ids', 'learned: value (KL), scalars only') |            0.072 |             0.004 |           0.289 |       1.023 |      5.09  |
| ('prose_ids', 'learned: value (realized gain)')    |            0.075 |             0.002 |           0.253 |       1.171 |      4.155 |
| ('prose_ids', 'oracle: KL (needs resource)')       |            0.006 |             0.002 |           0.231 |       1.908 |      3.264 |
| ('prose_ids', 'oracle: realized gain')             |            0.012 |             0.002 |           0     |       3.565 |      3.515 |
| ('prose_ids', 'random')                            |            0.039 |             0.01  |           0.365 |       0.62  |      2.713 |


### A_compute: Spearman rank correlation with realized gain / KL (test docs)

|                                           |   rho_gain |   rho_kl |
|:------------------------------------------|-----------:|---------:|
| ('code', '1 - max prob (CALM-style)')     |      0.44  |    0.845 |
| ('code', 'entropy (BLT-style)')           |      0.436 |    0.866 |
| ('code', 'layer-6 to layer-12 change')    |      0.221 |    0.455 |
| ('code', 'learned: raw surprise')         |      0.397 |    0.821 |
| ('code', 'learned: value (KL)')           |      0.406 |    0.803 |
| ('natural', '1 - max prob (CALM-style)')  |      0.365 |    0.772 |
| ('natural', 'entropy (BLT-style)')        |      0.365 |    0.803 |
| ('natural', 'layer-6 to layer-12 change') |      0.158 |    0.339 |
| ('natural', 'learned: raw surprise')      |      0.342 |    0.771 |
| ('natural', 'learned: value (KL)')        |      0.365 |    0.786 |
| ('prose', '1 - max prob (CALM-style)')    |      0.285 |    0.66  |
| ('prose', 'entropy (BLT-style)')          |      0.292 |    0.717 |
| ('prose', 'layer-6 to layer-12 change')   |      0.083 |    0.189 |
| ('prose', 'learned: raw surprise')        |      0.278 |    0.688 |
| ('prose', 'learned: value (KL)')          |      0.304 |    0.738 |


### A_compute: cross-domain transfer of the value head (train on one domain, test on the other)

|                                   |   % gap recovered @10% |   @20% |   budget for 50% of gap (%) |
|:----------------------------------|-----------------------:|-------:|----------------------------:|
| ('code', 'entropy')               |                   25.6 |   46.9 |                        21.6 |
| ('code', 'learned on prose only') |                   27   |   47.3 |                        21.5 |
| ('prose', 'entropy')              |                   17   |   34.4 |                        31.2 |
| ('prose', 'learned on code only') |                   17.9 |   33.8 |                        31.4 |

### B_memory: % of loss gap recovered at each budget (mean of 5 doc splits)

|                                                 |   R@2% |   R@5% |   R@10% |   R@20% |   R@30% |   R@50% | budget for 50% of gap   |
|:------------------------------------------------|-------:|-------:|--------:|--------:|--------:|--------:|:------------------------|
| ('code', 'entropy (FLARE-style)')               |    5.9 |   13.7 |    26.1 |    46.7 |    62.3 |    83.5 | 21.8% ± 0.8             |
| ('code', 'learned: raw surprise')               |    5   |   12.5 |    24.5 |    45.1 |    61.7 |    83.3 | 22.8% ± 0.7             |
| ('code', 'learned: value (KL)')                 |   11.3 |   23.1 |    37.3 |    57.3 |    70.9 |    86.6 | 15.8% ± 0.9             |
| ('code', 'learned: value (realized gain)')      |   10.9 |   22.5 |    36.3 |    56.4 |    69.8 |    85.9 | 16.3% ± 0.9             |
| ('code', 'oracle: KL (needs resource)')         |   25.8 |   47.1 |    65.4 |    81.9 |    90.1 |    96.9 | 5.6% ± 0.2              |
| ('code', 'oracle: realized gain')               |   31.9 |   60   |    85.6 |   109.4 |   119.7 |   125.9 | 3.8% ± 0.1              |
| ('code', 'random')                              |    2   |    4.8 |     9.8 |    19.9 |    29.7 |    50   | 50.1% ± 1.1             |
| ('natural', 'entropy (FLARE-style)')            |    4.6 |   11.1 |    21.5 |    39.8 |    55   |    76.1 | 26.5% ± 0.7             |
| ('natural', 'learned: raw surprise')            |    4.1 |   10   |    19.7 |    38   |    52.9 |    76.4 | 28.0% ± 0.6             |
| ('natural', 'learned: value (KL)')              |    9.8 |   19.5 |    32.2 |    50.2 |    63.3 |    81.2 | 19.9% ± 0.4             |
| ('natural', 'learned: value (realized gain)')   |    9.3 |   19.1 |    31.4 |    49.4 |    62.2 |    80.4 | 20.5% ± 0.5             |
| ('natural', 'oracle: KL (needs resource)')      |   23   |   41.7 |    58.9 |    76   |    85.2 |    94.8 | 7.0% ± 0.2              |
| ('natural', 'oracle: realized gain')            |   29.5 |   55.7 |    81   |   105.8 |   117.8 |   126.4 | 4.2% ± 0.1              |
| ('natural', 'random')                           |    2   |    4.9 |     9.9 |    20   |    30.1 |    50.3 | 49.7% ± 0.6             |
| ('prose', 'entropy (FLARE-style)')              |    3.7 |    9.1 |    18.2 |    35   |    48.8 |    69.8 | 31.0% ± 0.6             |
| ('prose', 'learned: raw surprise')              |    3.6 |    8.9 |    17.5 |    33.2 |    47.3 |    69.5 | 32.1% ± 0.5             |
| ('prose', 'learned: value (KL)')                |    8   |   15.9 |    27.2 |    43.5 |    56.2 |    74.9 | 24.9% ± 0.6             |
| ('prose', 'learned: value (realized gain)')     |    7.8 |   15.9 |    26.9 |    43   |    55.3 |    73.8 | 25.3% ± 0.7             |
| ('prose', 'oracle: KL (needs resource)')        |   20.1 |   36.7 |    52.6 |    69.9 |    80.1 |    91.7 | 9.0% ± 0.2              |
| ('prose', 'oracle: realized gain')              |   27.2 |   51.6 |    76.3 |   101.9 |   115.3 |   126.4 | 4.8% ± 0.1              |
| ('prose', 'random')                             |    1.9 |    5   |    10   |    20.1 |    30.4 |    50.5 | 49.5% ± 0.2             |
| ('prose_ids', 'entropy (FLARE-style)')          |    3.2 |    8   |    16.9 |    30.9 |    43.4 |    66.9 | 35.8% ± 0.9             |
| ('prose_ids', 'learned: raw surprise')          |    2.9 |    7.4 |    15.2 |    29.6 |    42.2 |    64.3 | 36.7% ± 1.2             |
| ('prose_ids', 'learned: value (KL)')            |    7.2 |   15   |    24.9 |    40   |    52.9 |    72.9 | 27.8% ± 0.6             |
| ('prose_ids', 'learned: value (realized gain)') |    6.6 |   14.5 |    25.1 |    40.4 |    52.1 |    70.9 | 28.1% ± 0.9             |
| ('prose_ids', 'oracle: KL (needs resource)')    |   17.5 |   34.5 |    52.6 |    71.7 |    81.7 |    92.8 | 9.1% ± 0.1              |
| ('prose_ids', 'oracle: realized gain')          |   22.6 |   45.4 |    70.1 |    95.8 |   108.5 |   119.1 | 5.7% ± 0.1              |
| ('prose_ids', 'random')                         |    2   |    4.9 |     9.9 |    20   |    29.9 |    50   | 50.1% ± 1.1             |


### B_memory: what each policy selects at a 10% budget

|                                                 |   share_id_first |   share_id_repeat |   share_no_gain |   mean_gain |   mean_H_L |
|:------------------------------------------------|-----------------:|------------------:|----------------:|------------:|-----------:|
| ('code', 'entropy (FLARE-style)')               |            0     |             0     |           0.344 |       1.322 |      3.591 |
| ('code', 'learned: raw surprise')               |            0     |             0     |           0.36  |       1.244 |      3.617 |
| ('code', 'learned: value (KL)')                 |            0     |             0     |           0.25  |       1.895 |      1.998 |
| ('code', 'learned: value (realized gain)')      |            0     |             0     |           0.254 |       1.842 |      1.955 |
| ('code', 'oracle: KL (needs resource)')         |            0     |             0     |           0.167 |       3.321 |      1.114 |
| ('code', 'oracle: realized gain')               |            0     |             0     |           0     |       4.347 |      1.301 |
| ('code', 'random')                              |            0     |             0     |           0.513 |       0.495 |      1.34  |
| ('natural', 'entropy (FLARE-style)')            |            0     |             0     |           0.344 |       1.181 |      4.207 |
| ('natural', 'learned: raw surprise')            |            0     |             0     |           0.354 |       1.083 |      4.268 |
| ('natural', 'learned: value (KL)')              |            0     |             0     |           0.265 |       1.769 |      2.358 |
| ('natural', 'learned: value (realized gain)')   |            0     |             0     |           0.27  |       1.72  |      2.395 |
| ('natural', 'oracle: KL (needs resource)')      |            0     |             0     |           0.181 |       3.23  |      1.552 |
| ('natural', 'oracle: realized gain')            |            0     |             0     |           0     |       4.441 |      1.843 |
| ('natural', 'random')                           |            0     |             0     |           0.474 |       0.541 |      1.949 |
| ('prose', 'entropy (FLARE-style)')              |            0     |             0     |           0.345 |       1.079 |      4.649 |
| ('prose', 'learned: raw surprise')              |            0     |             0     |           0.349 |       1.04  |      4.59  |
| ('prose', 'learned: value (KL)')                |            0     |             0     |           0.282 |       1.616 |      2.851 |
| ('prose', 'learned: value (realized gain)')     |            0     |             0     |           0.286 |       1.597 |      2.866 |
| ('prose', 'oracle: KL (needs resource)')        |            0     |             0     |           0.197 |       3.124 |      2.052 |
| ('prose', 'oracle: realized gain')              |            0     |             0     |           0     |       4.53  |      2.329 |
| ('prose', 'random')                             |            0     |             0     |           0.43  |       0.593 |      2.625 |
| ('prose_ids', 'entropy (FLARE-style)')          |            0.018 |             0.004 |           0.323 |       1.326 |      4.545 |
| ('prose_ids', 'learned: raw surprise')          |            0.003 |             0.001 |           0.338 |       1.194 |      4.502 |
| ('prose_ids', 'learned: value (KL)')            |            0.029 |             0.007 |           0.264 |       1.956 |      2.787 |
| ('prose_ids', 'learned: value (realized gain)') |            0.037 |             0.01  |           0.265 |       1.973 |      2.836 |
| ('prose_ids', 'oracle: KL (needs resource)')    |            0.145 |             0.086 |           0.145 |       4.136 |      2.253 |
| ('prose_ids', 'oracle: realized gain')          |            0.098 |             0.085 |           0     |       5.509 |      2.384 |
| ('prose_ids', 'random')                         |            0.039 |             0.01  |           0.409 |       0.775 |      2.713 |


### B_memory: Spearman rank correlation with realized gain / KL (test docs)

|                                      |   rho_gain |   rho_kl |
|:-------------------------------------|-----------:|---------:|
| ('code', 'entropy (FLARE-style)')    |      0.258 |    0.69  |
| ('code', 'learned: raw surprise')    |      0.23  |    0.648 |
| ('code', 'learned: value (KL)')      |      0.279 |    0.646 |
| ('natural', 'entropy (FLARE-style)') |      0.208 |    0.625 |
| ('natural', 'learned: raw surprise') |      0.191 |    0.595 |
| ('natural', 'learned: value (KL)')   |      0.241 |    0.591 |
| ('prose', 'entropy (FLARE-style)')   |      0.156 |    0.53  |
| ('prose', 'learned: raw surprise')   |      0.15  |    0.512 |
| ('prose', 'learned: value (KL)')     |      0.193 |    0.501 |


### B_memory: cross-domain transfer of the value head (train on one domain, test on the other)

|                                   |   % gap recovered @10% |   @20% |   budget for 50% of gap (%) |
|:----------------------------------|-----------------------:|-------:|----------------------------:|
| ('code', 'entropy')               |                   26.1 |   46.7 |                        21.8 |
| ('code', 'learned on prose only') |                   24.2 |   41.9 |                        26.2 |
| ('prose', 'entropy')              |                   18.2 |   35   |                        31   |
| ('prose', 'learned on code only') |                   20.4 |   36.2 |                        30.8 |


### Natural text, by decile of the small model's entropy H_S

|   H_S_decile |   H_S |   nll_S |   H_L |   gain_c |   KL_LS |   gain_m |     n |
|-------------:|------:|--------:|------:|---------:|--------:|---------:|------:|
|            1 | 0.034 |   0.07  | 0.036 |    0.025 |   0.023 |    0.41  | 10860 |
|            2 | 0.241 |   0.316 | 0.206 |    0.098 |   0.113 |    0.611 | 10859 |
|            3 | 0.658 |   0.752 | 0.491 |    0.23  |   0.253 |    0.546 | 10859 |
|            4 | 1.201 |   1.219 | 0.848 |    0.345 |   0.4   |    0.547 | 10859 |
|            5 | 1.902 |   1.975 | 1.362 |    0.542 |   0.594 |    0.562 | 10860 |
|            6 | 2.705 |   2.712 | 2     |    0.65  |   0.715 |    0.516 | 10859 |
|            7 | 3.503 |   3.481 | 2.619 |    0.77  |   0.853 |    0.539 | 10859 |
|            8 | 4.276 |   4.166 | 3.214 |    0.92  |   1     |    0.547 | 10859 |
|            9 | 5.093 |   5.037 | 3.864 |    1.086 |   1.165 |    0.529 | 10859 |
|           10 | 6.168 |   6.116 | 4.827 |    1.217 |   1.305 |    0.504 | 10860 |
