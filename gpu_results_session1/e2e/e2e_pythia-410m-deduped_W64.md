
### pythia-410m-deduped_W64 — natural: % of local→full loss gap recovered (gap = 0.467 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |     10.9 |      19.6 |      36.3 |      49.8 |       13.1 |        24.1 |        42.8 |        56.9 |
| familiarity head (7 scalars)        |     16.7 |      28   |      43.5 |      56.5 |       19.8 |        31.8 |        48.5 |        62   |
| familiarity rule (no training)      |     14.5 |      24.3 |      39.2 |      52.3 |       17.6 |        27.6 |        42.6 |        56.4 |
| learned head (hidden + familiarity) |     21.1 |      34   |      52.3 |      64.9 |       23.5 |        37.5 |        57.1 |        69.9 |
| oracle KL (needs full pass)         |     36.4 |      52.1 |      69.5 |      79.9 |       42.5 |        59.8 |        77.4 |        86.6 |
| random                              |      4.3 |       8.8 |      18.2 |      28.3 |        4.9 |         9.8 |        19.9 |        30.3 |

### pythia-410m-deduped_W64 — prose: % of local→full loss gap recovered (gap = 0.525 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |      7.6 |      15.3 |      31   |      43.8 |        9.4 |        18.8 |        36.4 |        50.1 |
| familiarity head (7 scalars)        |     14.1 |      24.6 |      39.5 |      52.5 |       16.8 |        28   |        44.3 |        57.7 |
| familiarity rule (no training)      |     12.7 |      22.8 |      37.8 |      51.3 |       14.9 |        25.5 |        40.4 |        55.2 |
| learned head (hidden + familiarity) |     18.7 |      30.4 |      47.4 |      58.9 |       20.4 |        33   |        51.2 |        63.6 |
| oracle KL (needs full pass)         |     32.2 |      47.3 |      64.8 |      76.3 |       36.9 |        53.2 |        71.4 |        81.9 |
| random                              |      4.6 |       8.7 |      18.4 |      28.2 |        5.3 |         9.9 |        20.3 |        30.4 |

### pythia-410m-deduped_W64 — code: % of local→full loss gap recovered (gap = 0.414 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |     14.6 |      24.5 |      42.5 |      56.7 |       17.3 |        30   |        50.1 |        64.7 |
| familiarity head (7 scalars)        |     19.8 |      31.8 |      48   |      61   |       23.3 |        36.2 |        53.3 |        66.8 |
| familiarity rule (no training)      |     16.5 |      25.9 |      40.9 |      53.4 |       20.7 |        30.1 |        45.2 |        57.7 |
| learned head (hidden + familiarity) |     23.8 |      38.1 |      58   |      71.8 |       27   |        42.6 |        63.8 |        77   |
| oracle KL (needs full pass)         |     41.3 |      57.7 |      74.8 |      84   |       48.8 |        67.2 |        84.2 |        92.1 |
| random                              |      3.9 |       8.9 |      18   |      28.4 |        4.5 |         9.6 |        19.5 |        30.2 |

### pythia-410m-deduped_W64 — prose_ids: % of local→full loss gap recovered (gap = 0.662 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |      8.6 |      15.3 |      29.1 |      42.6 |        9   |        17   |        32.2 |        46.2 |
| familiarity head (7 scalars)        |     17.1 |      29.7 |      44.5 |      56.2 |       18.5 |        31.2 |        46.6 |        58.4 |
| familiarity rule (no training)      |     18.3 |      29.7 |      45.7 |      56   |       19.5 |        30.7 |        46   |        57.2 |
| learned head (hidden + familiarity) |     21.4 |      31.6 |      47.4 |      58.2 |       21.1 |        32.2 |        48.7 |        59.5 |
| oracle KL (needs full pass)         |     35.9 |      51.6 |      68.8 |      79.1 |       38.5 |        55.4 |        73.3 |        83.7 |
| random                              |      4.7 |       9.2 |      18.8 |      28.3 |        5.2 |        10.1 |        19.6 |        29.7 |
