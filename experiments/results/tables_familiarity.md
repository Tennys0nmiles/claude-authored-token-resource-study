### B_memory + familiarity: % of long-context gain recovered (mean of 5 doc splits)

|                                                         |   R@2% |   R@5% |   R@10% |   R@20% |   R@30% |   R@50% | budget for 50% of gap   |
|:--------------------------------------------------------|-------:|-------:|--------:|--------:|--------:|--------:|:------------------------|
| ('code', 'entropy (FLARE-style)')                       |    5.9 |   13.7 |    26.1 |    46.7 |    62.3 |    83.5 | 21.8% ± 0.8             |
| ('code', 'familiarity + entropy only (7 scalars)')      |   13.3 |   27.1 |    39.3 |    53.7 |    66.7 |    84.2 | 17.2% ± 0.8             |
| ('code', 'learned: value (KL)')                         |   11.3 |   23.1 |    37.3 |    57.3 |    70.9 |    86.6 | 15.8% ± 0.9             |
| ('code', 'learned: value (KL) + familiarity')           |   14.8 |   29.5 |    44.8 |    64   |    76.4 |    89.8 | 12.2% ± 0.4             |
| ('code', 'oracle: KL (needs resource)')                 |   25.8 |   47.1 |    65.4 |    81.9 |    90.1 |    96.9 | 5.6% ± 0.2              |
| ('natural', 'entropy (FLARE-style)')                    |    4.6 |   11.1 |    21.5 |    39.8 |    55   |    76.1 | 26.5% ± 0.7             |
| ('natural', 'familiarity + entropy only (7 scalars)')   |   11.3 |   22.4 |    33.6 |    48.2 |    61.7 |    80.5 | 21.3% ± 0.3             |
| ('natural', 'learned: value (KL)')                      |    9.8 |   19.5 |    32.2 |    50.2 |    63.3 |    81.2 | 19.9% ± 0.4             |
| ('natural', 'learned: value (KL) + familiarity')        |   13.4 |   25.7 |    39.3 |    57.3 |    69.5 |    85   | 15.4% ± 0.5             |
| ('natural', 'oracle: KL (needs resource)')              |   23   |   41.7 |    58.9 |    76   |    85.2 |    94.8 | 7.0% ± 0.2              |
| ('prose', 'entropy (FLARE-style)')                      |    3.7 |    9.1 |    18.2 |    35   |    48.8 |    69.8 | 31.0% ± 0.6             |
| ('prose', 'familiarity + entropy only (7 scalars)')     |    9.2 |   17.9 |    28.1 |    43.1 |    56.8 |    76.2 | 24.6% ± 0.5             |
| ('prose', 'learned: value (KL)')                        |    8   |   15.9 |    27.2 |    43.5 |    56.2 |    74.9 | 24.9% ± 0.6             |
| ('prose', 'learned: value (KL) + familiarity')          |   11.5 |   21.9 |    34.1 |    50.9 |    62.9 |    80   | 19.3% ± 1.1             |
| ('prose', 'oracle: KL (needs resource)')                |   20.1 |   36.7 |    52.6 |    69.9 |    80.1 |    91.7 | 9.0% ± 0.2              |
| ('prose_ids', 'entropy (FLARE-style)')                  |    3.2 |    8   |    16.9 |    30.9 |    43.4 |    66.9 | 35.8% ± 0.9             |
| ('prose_ids', 'familiarity + entropy only (7 scalars)') |    8.5 |   19   |    32.1 |    46.7 |    57.6 |    75   | 22.7% ± 0.5             |
| ('prose_ids', 'learned: value (KL)')                    |    7.2 |   15   |    24.9 |    40   |    52.9 |    72.9 | 27.8% ± 0.6             |
| ('prose_ids', 'learned: value (KL) + familiarity')      |   11.2 |   21.9 |    34.5 |    51.4 |    62.7 |    79.1 | 19.0% ± 0.9             |
| ('prose_ids', 'oracle: KL (needs resource)')            |   17.5 |   34.5 |    52.6 |    71.7 |    81.7 |    92.8 | 9.1% ± 0.1              |


### Selection at 10% budget on id-injected prose (base rates: id_first 3.9%, id_repeat 1.0%)

| policy                                 |   share_id_first |   share_id_repeat |
|:---------------------------------------|-----------------:|------------------:|
| entropy (FLARE-style)                  |            0.018 |             0.004 |
| familiarity + entropy only (7 scalars) |            0.052 |             0.086 |
| learned: value (KL)                    |            0.029 |             0.007 |
| learned: value (KL) + familiarity      |            0.057 |             0.067 |
| oracle: KL (needs resource)            |            0.145 |             0.086 |


### Familiarity bits on natural text: firing rate and mean memory gain (nats) when on/off

|            |   rate |   gain_m_when_on |   gain_m_when_off |
|:-----------|-------:|-----------------:|------------------:|
| fam_bi     |  0.262 |            0.986 |             0.369 |
| fam_tri    |  0.144 |            1.159 |             0.426 |
| fam_quad   |  0.089 |            1.333 |             0.453 |
| fam_bi_det |  0.153 |            1.077 |             0.433 |


### Familiarity bits by token type on id-injected prose (fraction firing)

| label     |   fam_bi |   fam_tri |   fam_bi_det |
|:----------|---------:|----------:|-------------:|
| id_first  |    0.19  |     0.183 |        0.06  |
| id_repeat |    0.972 |     0.909 |        0.758 |
| natural   |    0.179 |     0.08  |        0.13  |


### Cross-domain transfer (train on the other natural domain)

|                                                               |   % gain recovered @10% |   budget for 50% (%) |
|:--------------------------------------------------------------|------------------------:|---------------------:|
| ('code', 'entropy')                                           |                    26.1 |                 21.8 |
| ('code', 'familiarity + entropy (7 scalars) (other domain)')  |                    34.4 |                 19.4 |
| ('code', 'learned + familiarity (other domain)')              |                    37.1 |                 17   |
| ('prose', 'entropy')                                          |                    18.2 |                 31   |
| ('prose', 'familiarity + entropy (7 scalars) (other domain)') |                    27.9 |                 24.4 |
| ('prose', 'learned + familiarity (other domain)')             |                    27.6 |                 24.6 |
