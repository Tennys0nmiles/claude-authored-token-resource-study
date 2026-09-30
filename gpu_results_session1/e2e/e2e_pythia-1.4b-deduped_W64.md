
### pythia-1.4b-deduped_W64 — natural: % of local→full loss gap recovered (gap = 0.462 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |     11.1 |      20.1 |      36.4 |      50.3 |       13.3 |        24.3 |        43.2 |        58   |
| familiarity head (7 scalars)        |     16.1 |      26.6 |      42.8 |      56.4 |       19.3 |        30.9 |        48.5 |        61.9 |
| familiarity rule (no training)      |     13.4 |      22.6 |      37.5 |      50.8 |       16.7 |        26   |        40.7 |        54.4 |
| learned head (hidden + familiarity) |     20.1 |      32.3 |      50.9 |      63.4 |       22.2 |        36.3 |        55.8 |        67.9 |
| oracle KL (needs full pass)         |     36.7 |      52   |      69.1 |      78.3 |       42.3 |        59.6 |        76.9 |        85.7 |
| random                              |      4.5 |       9.1 |      18.8 |      28.9 |        5   |        10   |        20.6 |        30.8 |

### pythia-1.4b-deduped_W64 — prose: % of local→full loss gap recovered (gap = 0.538 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |      8   |      15.4 |      30.5 |      43.8 |        9.6 |        18.7 |        36.2 |        50.1 |
| familiarity head (7 scalars)        |     13.1 |      22.9 |      38.1 |      51.3 |       16.1 |        27.2 |        43.3 |        56.3 |
| familiarity rule (no training)      |     11.6 |      21.1 |      35.9 |      50.1 |       14.3 |        23.9 |        38.5 |        53.5 |
| learned head (hidden + familiarity) |     17.1 |      27.9 |      45.3 |      58.7 |       18.7 |        31.2 |        49   |        62   |
| oracle KL (needs full pass)         |     31.5 |      46   |      63.8 |      73.9 |       36.1 |        52.2 |        70.5 |        80.6 |
| random                              |      4.7 |       9   |      18.6 |      28.8 |        5.4 |        10   |        20.7 |        30.6 |

### pythia-1.4b-deduped_W64 — code: % of local→full loss gap recovered (gap = 0.393 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |     15   |      25.9 |      43.8 |      58.3 |       17.8 |        31.3 |        51.7 |        67.7 |
| familiarity head (7 scalars)        |     19.8 |      31.2 |      48.7 |      62.7 |       23.2 |        35.5 |        54.9 |        68.9 |
| familiarity rule (no training)      |     15.7 |      24.4 |      39.3 |      51.7 |       19.6 |        28.6 |        43.4 |        55.6 |
| learned head (hidden + familiarity) |     23.8 |      37.8 |      57.8 |      69.2 |       26.5 |        42.7 |        64.3 |        75   |
| oracle KL (needs full pass)         |     43   |      59.5 |      75.7 |      83.7 |       49.9 |        68.8 |        84.7 |        92.1 |
| random                              |      4.2 |       9.2 |      19   |      29   |        4.6 |        10   |        20.5 |        31.1 |

### pythia-1.4b-deduped_W64 — prose_ids: % of local→full loss gap recovered (gap = 0.675 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |      9   |      15.8 |      29.6 |      43.3 |        9.4 |        17.4 |        33.1 |        47.3 |
| familiarity head (7 scalars)        |     16.1 |      28.6 |      44.7 |      56.2 |       17.9 |        30.4 |        46.3 |        58   |
| familiarity rule (no training)      |     18.1 |      29.5 |      45.3 |      56   |       19.1 |        30.1 |        45.2 |        56.4 |
| learned head (hidden + familiarity) |     18.6 |      29.6 |      46.5 |      59.2 |       18.7 |        30.4 |        47.8 |        60.6 |
| oracle KL (needs full pass)         |     35.4 |      50.5 |      67.7 |      77.8 |       37.7 |        54   |        72.2 |        82.6 |
| random                              |      4.9 |       8.9 |      18.7 |      28.4 |        5.2 |         9.6 |        19.4 |        29.6 |
