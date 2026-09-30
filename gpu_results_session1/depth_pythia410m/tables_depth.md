
### Exit at layer 12 of 24: % of the (exit → full depth) loss gap recovered by running the remaining layers on a budget of tokens

Mean gap = 1.605 nats/token (nll exit 3.847 vs full 2.242).

|                                                        |   R@2% |   R@5% |   R@10% |   R@20% |   R@30% |   R@50% | budget for 50% of gap   |
|:-------------------------------------------------------|-------:|-------:|--------:|--------:|--------:|--------:|:------------------------|
| ('code', '1 - max prob at exit 12 (CALM-style)')       |    4.5 |   11.5 |    22.4 |    42.7 |    60.2 |    84.1 | 23.9% ± 0.3             |
| ('code', 'entropy at exit 12 (early-exit style)')      |    4.8 |   11.8 |    22.4 |    42.7 |    61.2 |    85.7 | 23.7% ± 0.2             |
| ('code', 'learned: raw surprise')                      |    4.7 |   11.7 |    23.2 |    44.2 |    61.9 |    85.8 | 23.0% ± 0.4             |
| ('code', 'learned: value (KL)')                        |    7.4 |   16.6 |    29.8 |    51   |    66.8 |    86.5 | 19.5% ± 0.2             |
| ('code', 'learned: value (KL), scalars only')          |    5.1 |   12.2 |    23.2 |    42.9 |    61.1 |    84.9 | 23.8% ± 0.3             |
| ('code', 'learned: value (realized gain)')             |    7.3 |   16.5 |    29.6 |    50.7 |    66.8 |    86.3 | 19.6% ± 0.2             |
| ('code', 'lens change 8->12 (saturation)')             |    0.9 |    3.6 |    10.8 |    28.2 |    45.8 |    75.1 | 32.6% ± 0.7             |
| ('code', 'oracle: KL (needs resource)')                |   10.9 |   22.5 |    37.6 |    59   |    74.5 |    92.2 | 15.3% ± 0.1             |
| ('code', 'oracle: realized gain')                      |   13.3 |   28.1 |    47.1 |    73.3 |    89.4 |   103.2 | 10.9% ± 0.1             |
| ('code', 'random')                                     |    2   |    4.9 |     9.8 |    19.9 |    29.8 |    49.8 | 50.1% ± 0.5             |
| ('natural', '1 - max prob at exit 12 (CALM-style)')    |    3.7 |    9.4 |    18.6 |    35.7 |    51.5 |    75.7 | 29.0% ± 0.1             |
| ('natural', 'entropy at exit 12 (early-exit style)')   |    4   |    9.9 |    19.1 |    37   |    52.9 |    77.6 | 28.1% ± 0.2             |
| ('natural', 'learned: raw surprise')                   |    4   |    9.9 |    19.5 |    37.5 |    53.4 |    77.3 | 27.7% ± 0.4             |
| ('natural', 'learned: value (KL)')                     |    7   |   15.5 |    27.5 |    46.5 |    61   |    81   | 22.2% ± 0.2             |
| ('natural', 'learned: value (KL), scalars only')       |    4.7 |   10.6 |    20.3 |    37.8 |    53.6 |    77.8 | 27.6% ± 0.3             |
| ('natural', 'learned: value (realized gain)')          |    6.9 |   15.4 |    27.3 |    46.2 |    60.8 |    80.8 | 22.4% ± 0.3             |
| ('natural', 'lens change 8->12 (saturation)')          |    1   |    4.4 |    11.7 |    28.2 |    44.1 |    70.3 | 34.1% ± 0.5             |
| ('natural', 'oracle: KL (needs resource)')             |   10.2 |   20.7 |    34.5 |    54.3 |    68.6 |    87.5 | 17.5% ± 0.1             |
| ('natural', 'oracle: realized gain')                   |   12.9 |   27.1 |    45.4 |    70.9 |    87.3 |   103.6 | 11.5% ± 0.1             |
| ('natural', 'random')                                  |    2   |    5   |     9.9 |    20   |    29.9 |    49.9 | 50.0% ± 0.4             |
| ('prose', '1 - max prob at exit 12 (CALM-style)')      |    3.3 |    8.1 |    16   |    31.3 |    45   |    68   | 33.9% ± 0.2             |
| ('prose', 'entropy at exit 12 (early-exit style)')     |    3.7 |    8.8 |    17.2 |    33   |    47.3 |    70.3 | 32.1% ± 0.4             |
| ('prose', 'learned: raw surprise')                     |    3.3 |    8.3 |    16.3 |    31.9 |    46.3 |    69   | 32.8% ± 0.7             |
| ('prose', 'learned: value (KL)')                       |    5.9 |   13.2 |    23.5 |    40.6 |    54.1 |    74.5 | 26.7% ± 0.4             |
| ('prose', 'learned: value (KL), scalars only')         |    4.2 |    9.5 |    18.2 |    33.8 |    48.1 |    70.9 | 31.4% ± 0.4             |
| ('prose', 'learned: value (realized gain)')            |    5.8 |   12.9 |    23.1 |    40.2 |    53.6 |    74.3 | 27.1% ± 0.3             |
| ('prose', 'lens change 8->12 (saturation)')            |    1.5 |    4.9 |    12   |    26.9 |    40.7 |    64.7 | 37.3% ± 0.3             |
| ('prose', 'oracle: KL (needs resource)')               |    8.7 |   18.2 |    30.5 |    48.4 |    61.9 |    81.5 | 21.1% ± 0.5             |
| ('prose', 'oracle: realized gain')                     |   12.2 |   25.7 |    43.2 |    68.1 |    84.8 |   103.4 | 12.3% ± 0.1             |
| ('prose', 'random')                                    |    2   |    5.1 |    10   |    20.1 |    30.1 |    50.1 | 49.9% ± 0.4             |
| ('prose_ids', '1 - max prob at exit 12 (CALM-style)')  |    3.3 |    8.1 |    15.8 |    31   |    44.8 |    68.1 | 34.0% ± 0.3             |
| ('prose_ids', 'entropy at exit 12 (early-exit style)') |    3.7 |    8.7 |    16.9 |    32.4 |    46.6 |    70.2 | 32.6% ± 0.4             |
| ('prose_ids', 'learned: raw surprise')                 |    3.3 |    8.2 |    16.1 |    31.4 |    45.7 |    69   | 33.3% ± 0.6             |
| ('prose_ids', 'learned: value (KL)')                   |    6   |   13.2 |    23.2 |    39.8 |    53.2 |    73.6 | 27.5% ± 0.5             |
| ('prose_ids', 'learned: value (KL), scalars only')     |    4.1 |    9.2 |    17.3 |    32.6 |    46.7 |    70.3 | 32.5% ± 0.4             |
| ('prose_ids', 'learned: value (realized gain)')        |    5.8 |   12.8 |    22.7 |    39.4 |    52.7 |    73.3 | 27.8% ± 0.4             |
| ('prose_ids', 'lens change 8->12 (saturation)')        |    1.2 |    4.1 |    10.1 |    23.7 |    37.5 |    62.3 | 39.8% ± 0.3             |
| ('prose_ids', 'oracle: KL (needs resource)')           |    8.7 |   18.1 |    29.9 |    47.2 |    60.6 |    80.4 | 21.9% ± 0.5             |
| ('prose_ids', 'oracle: realized gain')                 |   12.3 |   25.6 |    43   |    67.9 |    84.8 |   103.8 | 12.4% ± 0.1             |
| ('prose_ids', 'random')                                |    2.1 |    5.1 |    10.1 |    20.1 |    29.9 |    50.3 | 49.6% ± 0.3             |


Cross-domain (train on the other domain):

|                                   |   R10 |   R20 |   b50 |
|:----------------------------------|------:|------:|------:|
| ('code', 'entropy')               |  22.4 |  42.7 |  23.7 |
| ('code', 'learned on prose only') |  26.8 |  46.6 |  22   |
| ('prose', 'entropy')              |  17.2 |  33   |  32.1 |
| ('prose', 'learned on code only') |  20.8 |  37.2 |  29.5 |


Selection at 10%:

|                                                      |   share_id_first |   share_id_repeat |   share_no_gain |   mean_gain |   mean_H_L |
|:-----------------------------------------------------|-----------------:|------------------:|----------------:|------------:|-----------:|
| ('natural', '1 - max prob at exit 12 (CALM-style)')  |                0 |                 0 |           0.145 |       3.001 |      4.285 |
| ('natural', 'entropy at exit 12 (early-exit style)') |                0 |                 0 |           0.142 |       3.086 |      4.385 |
| ('natural', 'learned: raw surprise')                 |                0 |                 0 |           0.148 |       3.145 |      4.63  |
| ('natural', 'learned: value (KL)')                   |                0 |                 0 |           0.063 |       4.44  |      2.255 |
| ('natural', 'learned: value (KL), scalars only')     |                0 |                 0 |           0.124 |       3.273 |      3.909 |
| ('natural', 'learned: value (realized gain)')        |                0 |                 0 |           0.063 |       4.398 |      2.291 |
| ('natural', 'lens change 8->12 (saturation)')        |                0 |                 0 |           0.192 |       1.88  |      1.015 |
| ('natural', 'oracle: KL (needs resource)')           |                0 |                 0 |           0.076 |       5.576 |      1.909 |
| ('natural', 'oracle: realized gain')                 |                0 |                 0 |           0     |       7.319 |      2.634 |
| ('natural', 'random')                                |                0 |                 0 |           0.3   |       1.598 |      2.18  |


Rank correlations:

|                                                      |   rho_gain |   rho_kl |
|:-----------------------------------------------------|-----------:|---------:|
| ('natural', '1 - max prob at exit 12 (CALM-style)')  |      0.466 |    0.738 |
| ('natural', 'entropy at exit 12 (early-exit style)') |      0.48  |    0.769 |
| ('natural', 'learned: raw surprise')                 |      0.455 |    0.762 |
| ('natural', 'learned: value (KL)')                   |      0.524 |    0.799 |
| ('natural', 'lens change 8->12 (saturation)')        |      0.34  |    0.496 |

### Exit at layer 16 of 24: % of the (exit → full depth) loss gap recovered by running the remaining layers on a budget of tokens

Mean gap = 1.126 nats/token (nll exit 3.368 vs full 2.242).

|                                                        |   R@2% |   R@5% |   R@10% |   R@20% |   R@30% |   R@50% | budget for 50% of gap   |
|:-------------------------------------------------------|-------:|-------:|--------:|--------:|--------:|--------:|:------------------------|
| ('code', '1 - max prob at exit 16 (CALM-style)')       |    5.3 |   13.4 |    25.7 |    48.2 |    66.3 |    87.4 | 20.9% ± 0.3             |
| ('code', 'entropy at exit 16 (early-exit style)')      |    5.4 |   13.1 |    25.5 |    48.3 |    67.2 |    88.6 | 20.8% ± 0.3             |
| ('code', 'learned: raw surprise')                      |    4.5 |   11.5 |    23.4 |    46   |    65.6 |    88.6 | 21.8% ± 0.3             |
| ('code', 'learned: value (KL)')                        |    8.5 |   18.7 |    33.3 |    55.6 |    71.5 |    88.7 | 17.1% ± 0.2             |
| ('code', 'learned: value (KL), scalars only')          |    6.5 |   14.6 |    26.7 |    48.8 |    66.8 |    88.1 | 20.6% ± 0.2             |
| ('code', 'learned: value (realized gain)')             |    8.3 |   18.4 |    32.8 |    55.3 |    71.4 |    88.6 | 17.4% ± 0.1             |
| ('code', 'lens change 8->12 (saturation)')             |    1.3 |    4.7 |    12.3 |    29.4 |    46.3 |    75.7 | 32.4% ± 0.6             |
| ('code', 'oracle: KL (needs resource)')                |   12.5 |   25.5 |    41.3 |    63.5 |    77.9 |    93.4 | 13.5% ± 0.2             |
| ('code', 'oracle: realized gain')                      |   16.1 |   33.2 |    54.4 |    81.7 |    96.9 |   107.6 | 8.8% ± 0.1              |
| ('code', 'random')                                     |    2   |    4.9 |     9.8 |    19.9 |    29.8 |    49.8 | 50.2% ± 0.7             |
| ('natural', '1 - max prob at exit 16 (CALM-style)')    |    4.4 |   10.7 |    20.9 |    39.1 |    55.1 |    79.7 | 26.7% ± 0.3             |
| ('natural', 'entropy at exit 16 (early-exit style)')   |    4.6 |   11   |    21.1 |    39.5 |    56   |    81   | 26.2% ± 0.4             |
| ('natural', 'learned: raw surprise')                   |    3.9 |    9.6 |    19.5 |    38.3 |    54.9 |    80.3 | 26.8% ± 0.5             |
| ('natural', 'learned: value (KL)')                     |    7.8 |   17.2 |    30.6 |    50.6 |    65.4 |    83.7 | 19.7% ± 0.2             |
| ('natural', 'learned: value (KL), scalars only')       |    5.6 |   12.7 |    23   |    41.6 |    57.9 |    81.7 | 24.9% ± 0.3             |
| ('natural', 'learned: value (realized gain)')          |    7.7 |   16.9 |    30.2 |    50.3 |    65   |    83.5 | 19.8% ± 0.2             |
| ('natural', 'lens change 8->12 (saturation)')          |    1.5 |    5.3 |    12.8 |    29.1 |    44.8 |    71.1 | 33.5% ± 0.4             |
| ('natural', 'oracle: KL (needs resource)')             |   11.4 |   23.2 |    37.6 |    57.7 |    71.5 |    88.8 | 15.7% ± 0.2             |
| ('natural', 'oracle: realized gain')                   |   15.3 |   31.5 |    51.6 |    78   |    93.9 |   108.3 | 9.6% ± 0.2              |
| ('natural', 'random')                                  |    2   |    5   |     9.9 |    20   |    29.9 |    49.9 | 50.1% ± 0.5             |
| ('prose', '1 - max prob at exit 16 (CALM-style)')      |    4   |    9.6 |    18.2 |    33.8 |    47.5 |    70.5 | 32.0% ± 0.4             |
| ('prose', 'entropy at exit 16 (early-exit style)')     |    4.3 |   10.1 |    19.3 |    34.9 |    49.1 |    72.4 | 30.7% ± 0.6             |
| ('prose', 'learned: raw surprise')                     |    3.5 |    8.7 |    17.1 |    33.7 |    48.4 |    71.7 | 31.2% ± 0.8             |
| ('prose', 'learned: value (KL)')                       |    6.8 |   15.4 |    27.3 |    45   |    58.9 |    77.6 | 23.4% ± 0.3             |
| ('prose', 'learned: value (KL), scalars only')         |    5   |   11.4 |    20.5 |    36.6 |    51   |    74.1 | 29.2% ± 0.5             |
| ('prose', 'learned: value (realized gain)')            |    6.7 |   15.1 |    26.8 |    44.8 |    58.3 |    77.5 | 23.5% ± 0.4             |
| ('prose', 'lens change 8->12 (saturation)')            |    2   |    5.8 |    13.2 |    28.4 |    42.5 |    66.2 | 36.0% ± 0.2             |
| ('prose', 'oracle: KL (needs resource)')               |   10.1 |   20.5 |    33.3 |    51.4 |    64.8 |    83   | 19.1% ± 0.5             |
| ('prose', 'oracle: realized gain')                     |   14.4 |   29.5 |    48.5 |    74.1 |    90.4 |   107.8 | 10.5% ± 0.2             |
| ('prose', 'random')                                    |    2   |    5.1 |    10   |    20.1 |    30   |    50   | 50.0% ± 0.5             |
| ('prose_ids', '1 - max prob at exit 16 (CALM-style)')  |    4   |    9.3 |    17.6 |    33.2 |    47.1 |    70.3 | 32.2% ± 0.7             |
| ('prose_ids', 'entropy at exit 16 (early-exit style)') |    4   |    9.9 |    18.9 |    34.2 |    48.1 |    72.1 | 31.5% ± 0.9             |
| ('prose_ids', 'learned: raw surprise')                 |    3.5 |    8.6 |    16.9 |    32.9 |    47.3 |    71.4 | 32.1% ± 0.9             |
| ('prose_ids', 'learned: value (KL)')                   |    6.9 |   15.3 |    26.7 |    44.1 |    57.3 |    76.3 | 24.2% ± 0.5             |
| ('prose_ids', 'learned: value (KL), scalars only')     |    4.6 |   10.8 |    19.9 |    35.4 |    49.8 |    73.3 | 30.1% ± 0.6             |
| ('prose_ids', 'learned: value (realized gain)')        |    6.6 |   15   |    26.2 |    43.6 |    56.8 |    76.3 | 24.6% ± 0.5             |
| ('prose_ids', 'lens change 8->12 (saturation)')        |    1.5 |    4.7 |    10.9 |    24.8 |    38.9 |    63.7 | 38.6% ± 0.3             |
| ('prose_ids', 'oracle: KL (needs resource)')           |   10   |   20.1 |    32.4 |    50.1 |    63.7 |    82.5 | 19.9% ± 0.6             |
| ('prose_ids', 'oracle: realized gain')                 |   14.3 |   29.3 |    48.3 |    74.1 |    90.7 |   108.3 | 10.5% ± 0.2             |
| ('prose_ids', 'random')                                |    2   |    5.1 |    10.3 |    20.3 |    30.1 |    50.4 | 49.6% ± 0.3             |


Cross-domain (train on the other domain):

|                                   |   R10 |   R20 |   b50 |
|:----------------------------------|------:|------:|------:|
| ('code', 'entropy')               |  25.5 |  48.3 |  20.8 |
| ('code', 'learned on prose only') |  30.1 |  51.5 |  19.2 |
| ('prose', 'entropy')              |  19.3 |  34.9 |  30.7 |
| ('prose', 'learned on code only') |  24.3 |  41.5 |  25.9 |


Selection at 10%:

|                                                      |   share_id_first |   share_id_repeat |   share_no_gain |   mean_gain |   mean_H_L |
|:-----------------------------------------------------|-----------------:|------------------:|----------------:|------------:|-----------:|
| ('natural', '1 - max prob at exit 16 (CALM-style)')  |                0 |                 0 |           0.171 |       2.373 |      4.504 |
| ('natural', 'entropy at exit 16 (early-exit style)') |                0 |                 0 |           0.166 |       2.397 |      4.583 |
| ('natural', 'learned: raw surprise')                 |                0 |                 0 |           0.181 |       2.216 |      4.948 |
| ('natural', 'learned: value (KL)')                   |                0 |                 0 |           0.082 |       3.478 |      2.36  |
| ('natural', 'learned: value (KL), scalars only')     |                0 |                 0 |           0.146 |       2.613 |      4.046 |
| ('natural', 'learned: value (realized gain)')        |                0 |                 0 |           0.084 |       3.43  |      2.399 |
| ('natural', 'lens change 8->12 (saturation)')        |                0 |                 0 |           0.273 |       1.45  |      1.015 |
| ('natural', 'oracle: KL (needs resource)')           |                0 |                 0 |           0.093 |       4.265 |      2.12  |
| ('natural', 'oracle: realized gain')                 |                0 |                 0 |           0     |       5.853 |      2.751 |
| ('natural', 'random')                                |                0 |                 0 |           0.364 |       1.121 |      2.18  |


Rank correlations:

|                                                      |   rho_gain |   rho_kl |
|:-----------------------------------------------------|-----------:|---------:|
| ('natural', '1 - max prob at exit 16 (CALM-style)')  |      0.454 |    0.777 |
| ('natural', 'entropy at exit 16 (early-exit style)') |      0.46  |    0.797 |
| ('natural', 'learned: raw surprise')                 |      0.43  |    0.786 |
| ('natural', 'learned: value (KL)')                   |      0.502 |    0.813 |
| ('natural', 'lens change 8->12 (saturation)')        |      0.297 |    0.472 |
