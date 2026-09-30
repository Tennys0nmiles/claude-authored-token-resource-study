### B_memory + familiarity: % of long-context gain recovered (mean of 5 doc splits)

|                                                         |   R@2% |   R@5% |   R@10% |   R@20% |   R@30% |   R@50% | budget for 50% of gap   |
|:--------------------------------------------------------|-------:|-------:|--------:|--------:|--------:|--------:|:------------------------|
| ('code', 'entropy (FLARE-style)')                       |    7   |   15.7 |    29.4 |    49.8 |    64.7 |    84.8 | 20.1% ± 0.6             |
| ('code', 'familiarity + entropy only (7 scalars)')      |   12.5 |   25.3 |    38.2 |    55.2 |    67.6 |    85.1 | 16.4% ± 0.8             |
| ('code', 'learned: value (KL)')                         |   12.2 |   24.7 |    40   |    60.7 |    73.3 |    87.9 | 14.1% ± 0.4             |
| ('code', 'learned: value (KL) + familiarity')           |   14.4 |   28.5 |    44.7 |    65.2 |    77   |    90.1 | 12.2% ± 0.5             |
| ('code', 'oracle: KL (needs resource)')                 |   27.7 |   48.6 |    66.6 |    82.7 |    90.5 |    97.2 | 5.3% ± 0.2              |
| ('natural', 'entropy (FLARE-style)')                    |    4.9 |   12.2 |    23.3 |    42.2 |    56.9 |    78.6 | 24.8% ± 0.4             |
| ('natural', 'familiarity + entropy only (7 scalars)')   |    9.9 |   20   |    31.5 |    48.6 |    61.7 |    81.4 | 21.0% ± 0.4             |
| ('natural', 'learned: value (KL)')                      |    9.7 |   20   |    33.1 |    52.1 |    65.7 |    83.1 | 18.7% ± 0.4             |
| ('natural', 'learned: value (KL) + familiarity')        |   12.1 |   23.6 |    37.7 |    57   |    69.7 |    85.4 | 16.0% ± 0.6             |
| ('natural', 'oracle: KL (needs resource)')              |   22.7 |   40.7 |    57.7 |    75.6 |    85.2 |    95.1 | 7.4% ± 0.1              |
| ('prose', 'entropy (FLARE-style)')                      |    3.9 |    9.4 |    19   |    35.9 |    50.1 |    71.7 | 29.9% ± 0.5             |
| ('prose', 'familiarity + entropy only (7 scalars)')     |    7.4 |   15.7 |    26   |    42   |    55.3 |    76.1 | 25.8% ± 0.4             |
| ('prose', 'learned: value (KL)')                        |    7.8 |   16.2 |    27.4 |    44.6 |    57.8 |    76.9 | 23.9% ± 0.5             |
| ('prose', 'learned: value (KL) + familiarity')          |   10.1 |   19.5 |    31.8 |    49.8 |    62.5 |    79.7 | 20.1% ± 0.7             |
| ('prose', 'oracle: KL (needs resource)')                |   18.5 |   34   |    49.9 |    68.1 |    78.8 |    91.7 | 10.0% ± 0.2             |
| ('prose_ids', 'entropy (FLARE-style)')                  |    4.3 |    9.9 |    18.2 |    32.6 |    45.9 |    68.5 | 33.2% ± 0.7             |
| ('prose_ids', 'familiarity + entropy only (7 scalars)') |    8   |   17.5 |    28.7 |    44.3 |    56.2 |    75.1 | 24.4% ± 0.5             |
| ('prose_ids', 'learned: value (KL)')                    |    8.1 |   15.9 |    25.8 |    41.3 |    53.5 |    73.7 | 27.0% ± 0.9             |
| ('prose_ids', 'learned: value (KL) + familiarity')      |   10.7 |   20.4 |    32.1 |    48.9 |    61   |    78.5 | 20.8% ± 0.6             |
| ('prose_ids', 'oracle: KL (needs resource)')            |   17.3 |   33.7 |    50.7 |    69.7 |    81.2 |    92.9 | 9.7% ± 0.1              |


### Selection at 10% budget on id-injected prose (base rates: id_first 3.9%, id_repeat 1.0%)

| policy                                 |   share_id_first |   share_id_repeat |
|:---------------------------------------|-----------------:|------------------:|
| entropy (FLARE-style)                  |            0.016 |             0.003 |
| familiarity + entropy only (7 scalars) |            0.052 |             0.078 |
| learned: value (KL)                    |            0.036 |             0.011 |
| learned: value (KL) + familiarity      |            0.063 |             0.045 |
| oracle: KL (needs resource)            |            0.152 |             0.085 |


### Familiarity bits on natural text: firing rate and mean memory gain (nats) when on/off

|            |   rate |   gain_m_when_on |   gain_m_when_off |
|:-----------|-------:|-----------------:|------------------:|
| fam_bi     |  0.262 |            0.931 |             0.424 |
| fam_tri    |  0.144 |            1.065 |             0.471 |
| fam_quad   |  0.089 |            1.189 |             0.495 |
| fam_bi_det |  0.153 |            0.994 |             0.478 |


### Familiarity bits by token type on id-injected prose (fraction firing)

| label     |   fam_bi |   fam_tri |   fam_bi_det |
|:----------|---------:|----------:|-------------:|
| id_first  |    0.19  |     0.183 |        0.06  |
| id_repeat |    0.972 |     0.909 |        0.758 |
| natural   |    0.179 |     0.08  |        0.13  |


### Cross-domain transfer (train on the other natural domain)

|                                                               |   % gain recovered @10% |   budget for 50% (%) |
|:--------------------------------------------------------------|------------------------:|---------------------:|
| ('code', 'entropy')                                           |                    29.4 |                 20.1 |
| ('code', 'familiarity + entropy (7 scalars) (other domain)')  |                    33.9 |                 20.7 |
| ('code', 'learned + familiarity (other domain)')              |                    36.8 |                 17   |
| ('prose', 'entropy')                                          |                    19   |                 29.9 |
| ('prose', 'familiarity + entropy (7 scalars) (other domain)') |                    24.8 |                 25.6 |
| ('prose', 'learned + familiarity (other domain)')             |                    25.3 |                 26.2 |
