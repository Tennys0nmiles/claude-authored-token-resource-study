
### Exit at layer 12 of 24: % of the (exit → full depth) loss gap recovered by running the remaining layers on a budget of tokens

Mean gap = 1.786 nats/token (nll exit 3.782 vs full 1.996).

|                                                        |   R@2% |   R@5% |   R@10% |   R@20% |   R@30% |   R@50% | budget for 50% of gap   |
|:-------------------------------------------------------|-------:|-------:|--------:|--------:|--------:|--------:|:------------------------|
| ('code', '1 - max prob at exit 12 (CALM-style)')       |    4.8 |   11.6 |    22.9 |    42.7 |    59.7 |    81.4 | 24.0% ± 0.4             |
| ('code', 'entropy at exit 12 (early-exit style)')      |    4.8 |   11.7 |    23.2 |    44.3 |    61.6 |    84.5 | 23.1% ± 0.3             |
| ('code', 'learned: raw surprise')                      |    4.8 |   11.6 |    23.3 |    44.6 |    62.7 |    86.6 | 22.7% ± 0.3             |
| ('code', 'learned: value (KL)')                        |    7.1 |   16.2 |    29.5 |    51.6 |    68.2 |    86.9 | 19.2% ± 0.3             |
| ('code', 'learned: value (KL), scalars only')          |    5.3 |   12.3 |    23.7 |    44.7 |    61.9 |    83.8 | 22.9% ± 0.2             |
| ('code', 'learned: value (realized gain)')             |    7   |   16.1 |    29.5 |    51.6 |    68.2 |    86.8 | 19.2% ± 0.3             |
| ('code', 'lens change 8->12 (saturation)')             |    1.9 |    5.8 |    13.5 |    30.9 |    47.8 |    76.3 | 31.4% ± 0.3             |
| ('code', 'oracle: KL (needs resource)')                |   10.7 |   22.8 |    38.7 |    61.3 |    76.7 |    93.5 | 14.5% ± 0.1             |
| ('code', 'oracle: realized gain')                      |   12.4 |   26.9 |    46.1 |    73.1 |    89.9 |   103.6 | 11.2% ± 0.1             |
| ('code', 'random')                                     |    2   |    5   |     9.9 |    20   |    30   |    49.9 | 50.0% ± 0.5             |
| ('natural', '1 - max prob at exit 12 (CALM-style)')    |    3.6 |    9.2 |    18.4 |    35.2 |    49.9 |    74.5 | 30.0% ± 0.2             |
| ('natural', 'entropy at exit 12 (early-exit style)')   |    4.2 |    9.8 |    19.2 |    37.2 |    53   |    76.7 | 27.9% ± 0.4             |
| ('natural', 'learned: raw surprise')                   |    4.2 |   10.2 |    20.3 |    38.6 |    54.3 |    78.1 | 27.1% ± 0.5             |
| ('natural', 'learned: value (KL)')                     |    6.9 |   15.5 |    27.9 |    47.5 |    62.2 |    81.4 | 21.5% ± 0.3             |
| ('natural', 'learned: value (KL), scalars only')       |    4.7 |   10.9 |    20.6 |    38.8 |    54.5 |    77.4 | 26.9% ± 0.4             |
| ('natural', 'learned: value (realized gain)')          |    6.9 |   15.5 |    27.7 |    47.4 |    62.1 |    81.2 | 21.6% ± 0.3             |
| ('natural', 'lens change 8->12 (saturation)')          |    2.1 |    6.1 |    13.6 |    29.9 |    44.8 |    71   | 33.7% ± 0.3             |
| ('natural', 'oracle: KL (needs resource)')             |   10.2 |   21.5 |    35.8 |    56.6 |    71.1 |    89   | 16.4% ± 0.2             |
| ('natural', 'oracle: realized gain')                   |   12.3 |   26.3 |    44.7 |    70.7 |    87.5 |   103.6 | 11.7% ± 0.1             |
| ('natural', 'random')                                  |    2   |    5   |    10   |    20   |    30   |    50   | 50.0% ± 0.3             |
| ('prose', '1 - max prob at exit 12 (CALM-style)')      |    3.2 |    7.9 |    16   |    30.6 |    43.6 |    66.5 | 35.4% ± 0.4             |
| ('prose', 'entropy at exit 12 (early-exit style)')     |    3.7 |    9   |    17.2 |    32.9 |    47.3 |    69.1 | 32.1% ± 0.5             |
| ('prose', 'learned: raw surprise')                     |    3.5 |    8.6 |    17   |    33   |    47   |    69.5 | 32.4% ± 0.7             |
| ('prose', 'learned: value (KL)')                       |    5.9 |   13.1 |    23.7 |    40.8 |    54.7 |    74.6 | 26.3% ± 0.2             |
| ('prose', 'learned: value (KL), scalars only')         |    4.1 |    9.6 |    18.3 |    34.4 |    48.8 |    70.7 | 31.0% ± 0.4             |
| ('prose', 'learned: value (realized gain)')            |    5.8 |   13   |    23.5 |    40.8 |    54.5 |    74.4 | 26.5% ± 0.3             |
| ('prose', 'lens change 8->12 (saturation)')            |    2.1 |    5.8 |    12.5 |    26.9 |    39.9 |    64.8 | 37.7% ± 0.3             |
| ('prose', 'oracle: KL (needs resource)')               |    8.9 |   18.6 |    31.5 |    50.1 |    63.9 |    83.2 | 19.9% ± 0.4             |
| ('prose', 'oracle: realized gain')                     |   11.7 |   25.1 |    42.5 |    67.7 |    84.7 |   103.1 | 12.6% ± 0.2             |
| ('prose', 'random')                                    |    2   |    5.1 |    10.1 |    20.1 |    30.1 |    50.2 | 49.8% ± 0.1             |
| ('prose_ids', '1 - max prob at exit 12 (CALM-style)')  |    3.2 |    7.9 |    15.7 |    30.7 |    43.7 |    66.8 | 35.1% ± 0.4             |
| ('prose_ids', 'entropy at exit 12 (early-exit style)') |    3.8 |    8.9 |    17.1 |    32.4 |    46.5 |    69   | 32.8% ± 0.5             |
| ('prose_ids', 'learned: raw surprise')                 |    3.4 |    8.5 |    16.9 |    32.7 |    46.6 |    69.5 | 32.6% ± 0.5             |
| ('prose_ids', 'learned: value (KL)')                   |    5.8 |   12.9 |    23.2 |    40   |    53.8 |    74.1 | 27.1% ± 0.3             |
| ('prose_ids', 'learned: value (KL), scalars only')     |    4.1 |    9.3 |    17.5 |    32.8 |    47   |    69.7 | 32.4% ± 0.5             |
| ('prose_ids', 'learned: value (realized gain)')        |    5.8 |   12.7 |    22.9 |    39.9 |    53.8 |    74   | 27.2% ± 0.3             |
| ('prose_ids', 'lens change 8->12 (saturation)')        |    1.5 |    4.6 |    11   |    24.7 |    37.7 |    63   | 39.7% ± 0.3             |
| ('prose_ids', 'oracle: KL (needs resource)')           |    8.9 |   18.5 |    30.9 |    49.2 |    62.9 |    82.3 | 20.5% ± 0.4             |
| ('prose_ids', 'oracle: realized gain')                 |   11.7 |   24.9 |    42.2 |    67.3 |    84.4 |   103.1 | 12.7% ± 0.1             |
| ('prose_ids', 'random')                                |    2   |    5   |    10.1 |    20   |    29.8 |    50.2 | 49.8% ± 0.3             |


Cross-domain (train on the other domain):

|                                   |   R10 |   R20 |   b50 |
|:----------------------------------|------:|------:|------:|
| ('code', 'entropy')               |  23.2 |  44.3 |  23.1 |
| ('code', 'learned on prose only') |  26.8 |  47.1 |  21.7 |
| ('prose', 'entropy')              |  17.2 |  32.9 |  32.1 |
| ('prose', 'learned on code only') |  22   |  38   |  28.8 |


Selection at 10%:

|                                                      |   share_id_first |   share_id_repeat |   share_no_gain |   mean_gain |   mean_H_L |
|:-----------------------------------------------------|-----------------:|------------------:|----------------:|------------:|-----------:|
| ('natural', '1 - max prob at exit 12 (CALM-style)')  |                0 |                 0 |           0.13  |       3.308 |      3.797 |
| ('natural', 'entropy at exit 12 (early-exit style)') |                0 |                 0 |           0.125 |       3.453 |      3.813 |
| ('natural', 'learned: raw surprise')                 |                0 |                 0 |           0.13  |       3.641 |      3.996 |
| ('natural', 'learned: value (KL)')                   |                0 |                 0 |           0.05  |       5.005 |      1.584 |
| ('natural', 'learned: value (KL), scalars only')     |                0 |                 0 |           0.114 |       3.696 |      3.38  |
| ('natural', 'learned: value (realized gain)')        |                0 |                 0 |           0.05  |       4.978 |      1.613 |
| ('natural', 'lens change 8->12 (saturation)')        |                0 |                 0 |           0.2   |       2.442 |      1.472 |
| ('natural', 'oracle: KL (needs resource)')           |                0 |                 0 |           0.061 |       6.431 |      1.377 |
| ('natural', 'oracle: realized gain')                 |                0 |                 0 |           0     |       8.025 |      2.06  |
| ('natural', 'random')                                |                0 |                 0 |           0.324 |       1.79  |      1.949 |


Rank correlations:

|                                                      |   rho_gain |   rho_kl |
|:-----------------------------------------------------|-----------:|---------:|
| ('natural', '1 - max prob at exit 12 (CALM-style)')  |      0.455 |    0.691 |
| ('natural', 'entropy at exit 12 (early-exit style)') |      0.48  |    0.735 |
| ('natural', 'learned: raw surprise')                 |      0.468 |    0.748 |
| ('natural', 'learned: value (KL)')                   |      0.526 |    0.761 |
| ('natural', 'lens change 8->12 (saturation)')        |      0.362 |    0.532 |

### Exit at layer 16 of 24: % of the (exit → full depth) loss gap recovered by running the remaining layers on a budget of tokens

Mean gap = 1.066 nats/token (nll exit 3.062 vs full 1.996).

|                                                        |   R@2% |   R@5% |   R@10% |   R@20% |   R@30% |   R@50% | budget for 50% of gap   |
|:-------------------------------------------------------|-------:|-------:|--------:|--------:|--------:|--------:|:------------------------|
| ('code', '1 - max prob at exit 16 (CALM-style)')       |    6.7 |   14.8 |    27.1 |    48.5 |    65   |    85   | 20.8% ± 0.3             |
| ('code', 'entropy at exit 16 (early-exit style)')      |    6.9 |   15.3 |    27.7 |    49.3 |    66.1 |    86.7 | 20.4% ± 0.3             |
| ('code', 'learned: raw surprise')                      |    5.1 |   11.9 |    23.4 |    45.3 |    63.9 |    86.6 | 22.3% ± 0.3             |
| ('code', 'learned: value (KL)')                        |    7.6 |   17.6 |    31.5 |    53.4 |    69.3 |    87.1 | 18.2% ± 0.3             |
| ('code', 'learned: value (KL), scalars only')          |    7   |   15.5 |    27.9 |    49.4 |    65.9 |    86.2 | 20.3% ± 0.2             |
| ('code', 'learned: value (realized gain)')             |    7.5 |   17.3 |    31.2 |    53.3 |    69.4 |    87   | 18.3% ± 0.3             |
| ('code', 'lens change 8->12 (saturation)')             |    1.6 |    5.3 |    12.7 |    29.4 |    45.9 |    74.6 | 32.8% ± 0.3             |
| ('code', 'oracle: KL (needs resource)')                |   11.8 |   24.2 |    40.1 |    62.6 |    77.6 |    93.1 | 13.8% ± 0.1             |
| ('code', 'oracle: realized gain')                      |   15.2 |   31.8 |    53   |    80.9 |    96.5 |   107.2 | 9.2% ± 0.1              |
| ('code', 'random')                                     |    2   |    5   |    10   |    20.1 |    30   |    50.1 | 49.9% ± 0.6             |
| ('natural', '1 - max prob at exit 16 (CALM-style)')    |    5.3 |   11.8 |    21.9 |    39.4 |    54.9 |    77.9 | 26.7% ± 0.3             |
| ('natural', 'entropy at exit 16 (early-exit style)')   |    6.1 |   13.2 |    23.6 |    41.6 |    56.7 |    79.3 | 25.4% ± 0.4             |
| ('natural', 'learned: raw surprise')                   |    4.1 |    9.8 |    19   |    36.9 |    52.8 |    78.2 | 28.2% ± 0.4             |
| ('natural', 'learned: value (KL)')                     |    7.4 |   16.8 |    29.4 |    48.4 |    62.3 |    81.4 | 21.0% ± 0.3             |
| ('natural', 'learned: value (KL), scalars only')       |    6.3 |   13.7 |    24.2 |    42.2 |    57.2 |    79.7 | 24.9% ± 0.4             |
| ('natural', 'learned: value (realized gain)')          |    7.3 |   16.4 |    29   |    48.2 |    62.3 |    81.2 | 21.1% ± 0.4             |
| ('natural', 'lens change 8->12 (saturation)')          |    1.8 |    5.7 |    12.7 |    28.3 |    42.8 |    69.4 | 35.2% ± 0.3             |
| ('natural', 'oracle: KL (needs resource)')             |   11.3 |   22.7 |    36.9 |    57.1 |    70.9 |    88.6 | 16.0% ± 0.2             |
| ('natural', 'oracle: realized gain')                   |   14.9 |   31   |    51.5 |    78.9 |    95.2 |   109.1 | 9.6% ± 0.1              |
| ('natural', 'random')                                  |    2   |    5.1 |    10   |    20.1 |    30.1 |    50.2 | 49.8% ± 0.4             |
| ('prose', '1 - max prob at exit 16 (CALM-style)')      |    3.7 |    9.1 |    17.3 |    32.7 |    46.1 |    68.9 | 33.1% ± 0.5             |
| ('prose', 'entropy at exit 16 (early-exit style)')     |    4.5 |   10.1 |    19.1 |    34.7 |    48.6 |    70.6 | 31.1% ± 0.5             |
| ('prose', 'learned: raw surprise')                     |    3   |    7.8 |    15.8 |    31.4 |    45.7 |    68.7 | 33.5% ± 0.6             |
| ('prose', 'learned: value (KL)')                       |    6.7 |   14.5 |    24.8 |    41.1 |    54.4 |    74.4 | 26.5% ± 0.5             |
| ('prose', 'learned: value (KL), scalars only')         |    4.8 |   10.6 |    19.7 |    35.2 |    49.3 |    71.3 | 30.6% ± 0.5             |
| ('prose', 'learned: value (realized gain)')            |    6.5 |   14.2 |    24.4 |    40.8 |    54.3 |    74.1 | 26.7% ± 0.4             |
| ('prose', 'lens change 8->12 (saturation)')            |    2   |    5.5 |    11.9 |    25.7 |    38.3 |    63.5 | 39.1% ± 0.4             |
| ('prose', 'oracle: KL (needs resource)')               |   10.1 |   19.8 |    32.3 |    50.1 |    63.1 |    82.7 | 19.9% ± 0.7             |
| ('prose', 'oracle: realized gain')                     |   14.3 |   29.9 |    49.5 |    76.5 |    93.7 |   110.7 | 10.1% ± 0.1             |
| ('prose', 'random')                                    |    2   |    5.1 |    10.1 |    20.1 |    30.2 |    50.4 | 49.6% ± 0.5             |
| ('prose_ids', '1 - max prob at exit 16 (CALM-style)')  |    3.5 |    8.9 |    17.1 |    32.2 |    45.7 |    68.1 | 33.3% ± 0.6             |
| ('prose_ids', 'entropy at exit 16 (early-exit style)') |    4.4 |   10.3 |    18.8 |    33.8 |    47.4 |    69.8 | 32.2% ± 0.6             |
| ('prose_ids', 'learned: raw surprise')                 |    2.9 |    7.8 |    15.8 |    31   |    45.1 |    68.7 | 33.7% ± 0.7             |
| ('prose_ids', 'learned: value (KL)')                   |    6.7 |   14.2 |    24.2 |    40   |    53.3 |    73.7 | 27.3% ± 0.5             |
| ('prose_ids', 'learned: value (KL), scalars only')     |    4.8 |   10.5 |    19.3 |    34.2 |    47.9 |    70.1 | 31.7% ± 0.6             |
| ('prose_ids', 'learned: value (realized gain)')        |    6.5 |   14   |    23.8 |    39.9 |    53.3 |    73.5 | 27.4% ± 0.5             |
| ('prose_ids', 'lens change 8->12 (saturation)')        |    1.2 |    4.1 |    10   |    23.3 |    35.9 |    61.6 | 41.1% ± 0.3             |
| ('prose_ids', 'oracle: KL (needs resource)')           |    9.9 |   19.6 |    31.7 |    49.5 |    62.5 |    81.8 | 20.3% ± 0.7             |
| ('prose_ids', 'oracle: realized gain')                 |   14.3 |   30   |    49.7 |    76.8 |    94.1 |   111.2 | 10.1% ± 0.1             |
| ('prose_ids', 'random')                                |    2.1 |    5   |    10.3 |    20.2 |    29.9 |    50.3 | 49.6% ± 0.2             |


Cross-domain (train on the other domain):

|                                   |   R10 |   R20 |   b50 |
|:----------------------------------|------:|------:|------:|
| ('code', 'entropy')               |  27.7 |  49.3 |  20.4 |
| ('code', 'learned on prose only') |  29.1 |  50.1 |  19.9 |
| ('prose', 'entropy')              |  19.1 |  34.7 |  31.1 |
| ('prose', 'learned on code only') |  22.8 |  38.6 |  28.4 |


Selection at 10%:

|                                                      |   share_id_first |   share_id_repeat |   share_no_gain |   mean_gain |   mean_H_L |
|:-----------------------------------------------------|-----------------:|------------------:|----------------:|------------:|-----------:|
| ('natural', '1 - max prob at exit 16 (CALM-style)')  |                0 |                 0 |           0.157 |       2.351 |      4.021 |
| ('natural', 'entropy at exit 16 (early-exit style)') |                0 |                 0 |           0.136 |       2.525 |      3.804 |
| ('natural', 'learned: raw surprise')                 |                0 |                 0 |           0.179 |       2.042 |      4.646 |
| ('natural', 'learned: value (KL)')                   |                0 |                 0 |           0.078 |       3.146 |      2.157 |
| ('natural', 'learned: value (KL), scalars only')     |                0 |                 0 |           0.126 |       2.591 |      3.573 |
| ('natural', 'learned: value (realized gain)')        |                0 |                 0 |           0.078 |       3.106 |      2.189 |
| ('natural', 'lens change 8->12 (saturation)')        |                0 |                 0 |           0.29  |       1.362 |      1.472 |
| ('natural', 'oracle: KL (needs resource)')           |                0 |                 0 |           0.103 |       3.96  |      1.868 |
| ('natural', 'oracle: realized gain')                 |                0 |                 0 |           0     |       5.518 |      2.447 |
| ('natural', 'random')                                |                0 |                 0 |           0.38  |       1.073 |      1.949 |


Rank correlations:

|                                                      |   rho_gain |   rho_kl |
|:-----------------------------------------------------|-----------:|---------:|
| ('natural', '1 - max prob at exit 16 (CALM-style)')  |      0.444 |    0.747 |
| ('natural', 'entropy at exit 16 (early-exit style)') |      0.461 |    0.78  |
| ('natural', 'learned: raw surprise')                 |      0.397 |    0.745 |
| ('natural', 'learned: value (KL)')                   |      0.475 |    0.77  |
| ('natural', 'lens change 8->12 (saturation)')        |      0.28  |    0.475 |
