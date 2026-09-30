### B_memory + familiarity: % of long-context gain recovered (mean of 5 doc splits)

|                                                         |   R@2% |   R@5% |   R@10% |   R@20% |   R@30% |   R@50% | budget for 50% of gap   |
|:--------------------------------------------------------|-------:|-------:|--------:|--------:|--------:|--------:|:------------------------|
| ('code', 'entropy (FLARE-style)')                       |    7.4 |   17   |    30.7 |    51.8 |    66.8 |    86.6 | 19.0% ± 0.5             |
| ('code', 'familiarity + entropy only (7 scalars)')      |   12.2 |   24.4 |    37.9 |    57.1 |    69.6 |    85.6 | 15.7% ± 0.6             |
| ('code', 'learned: value (KL)')                         |   13.3 |   26.3 |    41.8 |    61.6 |    73.8 |    87.2 | 13.7% ± 0.6             |
| ('code', 'learned: value (KL) + familiarity')           |   14.8 |   29.1 |    45.4 |    65.3 |    76.7 |    89.1 | 11.9% ± 0.7             |
| ('code', 'oracle: KL (needs resource)')                 |   28.4 |   49.4 |    66.5 |    83.4 |    90.6 |    97.4 | 5.1% ± 0.2              |
| ('natural', 'entropy (FLARE-style)')                    |    5.4 |   13.2 |    24.8 |    43.8 |    59.1 |    80.6 | 23.7% ± 0.5             |
| ('natural', 'familiarity + entropy only (7 scalars)')   |    9.2 |   18.9 |    30.6 |    49.4 |    63.4 |    82.3 | 20.4% ± 0.5             |
| ('natural', 'learned: value (KL)')                      |   10   |   20.3 |    33.5 |    52.2 |    65.7 |    83.3 | 18.6% ± 0.4             |
| ('natural', 'learned: value (KL) + familiarity')        |   11.4 |   23.1 |    36.8 |    56   |    68.7 |    85.1 | 16.4% ± 0.4             |
| ('natural', 'oracle: KL (needs resource)')              |   22.4 |   40.1 |    56.6 |    75.4 |    85.1 |    95.4 | 7.7% ± 0.1              |
| ('prose', 'entropy (FLARE-style)')                      |    4.2 |   10.4 |    20.1 |    37.3 |    51.3 |    73.3 | 29.0% ± 0.8             |
| ('prose', 'familiarity + entropy only (7 scalars)')     |    6.9 |   14.9 |    25   |    41.9 |    55.8 |    76.6 | 25.4% ± 1.0             |
| ('prose', 'learned: value (KL)')                        |    7.6 |   16   |    27.1 |    44.1 |    57.2 |    76.4 | 24.3% ± 0.5             |
| ('prose', 'learned: value (KL) + familiarity')          |    8.9 |   18.4 |    30.2 |    47.8 |    60.7 |    78.8 | 21.4% ± 0.6             |
| ('prose', 'oracle: KL (needs resource)')                |   17.8 |   32.9 |    48.4 |    67.2 |    78.5 |    91.6 | 10.7% ± 0.4             |
| ('prose_ids', 'entropy (FLARE-style)')                  |    4.6 |   10.7 |    18.8 |    33.7 |    47.5 |    70.4 | 31.9% ± 0.7             |
| ('prose_ids', 'familiarity + entropy only (7 scalars)') |    7.6 |   16.3 |    26.7 |    43.7 |    56.4 |    75.9 | 24.8% ± 0.8             |
| ('prose_ids', 'learned: value (KL)')                    |    7.7 |   15.5 |    25.4 |    41.3 |    54.8 |    75.4 | 26.3% ± 0.8             |
| ('prose_ids', 'learned: value (KL) + familiarity')      |    9.3 |   18.2 |    29.7 |    47.9 |    60.9 |    78.7 | 21.5% ± 0.7             |
| ('prose_ids', 'oracle: KL (needs resource)')            |   16.8 |   32.8 |    49   |    68.4 |    80.2 |    92.5 | 10.4% ± 0.2             |


### Selection at 10% budget on id-injected prose (base rates: id_first 3.9%, id_repeat 1.0%)

| policy                                 |   share_id_first |   share_id_repeat |
|:---------------------------------------|-----------------:|------------------:|
| entropy (FLARE-style)                  |            0.033 |             0.007 |
| familiarity + entropy only (7 scalars) |            0.039 |             0.072 |
| learned: value (KL)                    |            0.02  |             0.005 |
| learned: value (KL) + familiarity      |            0.033 |             0.028 |
| oracle: KL (needs resource)            |            0.138 |             0.086 |


### Familiarity bits on natural text: firing rate and mean memory gain (nats) when on/off

|            |   rate |   gain_m_when_on |   gain_m_when_off |
|:-----------|-------:|-----------------:|------------------:|
| fam_bi     |  0.262 |            0.88  |             0.449 |
| fam_tri    |  0.144 |            0.99  |             0.49  |
| fam_quad   |  0.089 |            1.098 |             0.51  |
| fam_bi_det |  0.153 |            0.918 |             0.498 |


### Familiarity bits by token type on id-injected prose (fraction firing)

| label     |   fam_bi |   fam_tri |   fam_bi_det |
|:----------|---------:|----------:|-------------:|
| id_first  |    0.19  |     0.183 |        0.06  |
| id_repeat |    0.972 |     0.909 |        0.758 |
| natural   |    0.179 |     0.08  |        0.13  |


### Cross-domain transfer (train on the other natural domain)

|                                                               |   % gain recovered @10% |   budget for 50% (%) |
|:--------------------------------------------------------------|------------------------:|---------------------:|
| ('code', 'entropy')                                           |                    30.7 |                 19   |
| ('code', 'familiarity + entropy (7 scalars) (other domain)')  |                    35.1 |                 20.4 |
| ('code', 'learned + familiarity (other domain)')              |                    34.9 |                 18.1 |
| ('prose', 'entropy')                                          |                    20.1 |                 29   |
| ('prose', 'familiarity + entropy (7 scalars) (other domain)') |                    24.1 |                 25.9 |
| ('prose', 'learned + familiarity (other domain)')             |                    24.7 |                 27   |
