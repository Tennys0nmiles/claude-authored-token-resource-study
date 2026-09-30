
### Qwen2.5-1.5B_W1024 — natural: % of local→full loss gap recovered (gap = 0.125 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |     13.2 |      23.3 |      41   |      55.8 |       15.7 |        27.7 |        46.9 |        61.3 |
| familiarity head (7 scalars)        |     18.8 |      29.8 |      47.2 |      61.3 |       21.5 |        33.5 |        52.1 |        65.8 |
| familiarity rule (no training)      |     16   |      23.3 |      39.8 |      54.2 |       18.3 |        25.6 |        42.2 |        56.9 |
| learned head (hidden + familiarity) |     29.5 |      43.7 |      60.5 |      72.7 |       32.1 |        46.9 |        63.9 |        75.1 |
| oracle KL (needs full pass)         |     56.5 |      70.5 |      83.1 |      89.6 |       62.4 |        76.8 |        88.4 |        93.6 |
| random                              |      4.9 |       9.7 |      19   |      28.8 |        5.7 |        11   |        21.4 |        31.4 |

### Qwen2.5-1.5B_W1024 — prose: % of local→full loss gap recovered (gap = 0.150 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |      9.6 |      17.5 |      32.8 |      47.1 |       12   |        21.6 |        38.3 |        52.3 |
| familiarity head (7 scalars)        |     16.6 |      27.8 |      43.6 |      57.3 |       19.8 |        31.9 |        48.8 |        61.9 |
| familiarity rule (no training)      |     15.1 |      23.3 |      39   |      52.1 |       17.5 |        25.5 |        41.6 |        55   |
| learned head (hidden + familiarity) |     23.1 |      36.2 |      53.9 |      67.3 |       25.1 |        39.2 |        57.6 |        70   |
| oracle KL (needs full pass)         |     49.5 |      65   |      79.7 |      87.6 |       54.7 |        70.9 |        84.7 |        91.1 |
| random                              |      5.4 |      10.3 |      19.3 |      28.3 |        6.1 |        11.5 |        21.3 |        30.6 |

### Qwen2.5-1.5B_W1024 — code: % of local→full loss gap recovered (gap = 0.095 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |     19.6 |      33.7 |      55.9 |      71.5 |       22.4 |        38.8 |        62.3 |        77.6 |
| familiarity head (7 scalars)        |     22.6 |      33.6 |      53.7 |      68.6 |       24.5 |        36.4 |        58.2 |        72.9 |
| familiarity rule (no training)      |     17.7 |      23.4 |      41.2 |      57.9 |       19.6 |        25.7 |        43.4 |        60.5 |
| learned head (hidden + familiarity) |     41.2 |      57.1 |      72.4 |      82.5 |       44.9 |        60.8 |        75.3 |        84.3 |
| oracle KL (needs full pass)         |     69   |      80.3 |      89.3 |      93.3 |       76.1 |        87.5 |        95.1 |        98.1 |
| random                              |      3.9 |       8.6 |      18.6 |      29.6 |        4.8 |        10.2 |        21.5 |        32.8 |

### Qwen2.5-1.5B_W1024 — prose_ids: % of local→full loss gap recovered (gap = 0.148 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |     10   |      17.9 |      33.2 |      47.3 |       12.6 |        22   |        38.6 |        52.6 |
| familiarity head (7 scalars)        |     17.8 |      29   |      44.7 |      58.4 |       21.2 |        33.4 |        50   |        63.3 |
| familiarity rule (no training)      |     16.1 |      24.6 |      40.2 |      53.7 |       18.5 |        27.2 |        42.8 |        56.7 |
| learned head (hidden + familiarity) |     24.2 |      36.8 |      55.2 |      68.5 |       26   |        39.5 |        58.6 |        71.4 |
| oracle KL (needs full pass)         |     50.9 |      66.6 |      80.7 |      88.2 |       56   |        72.1 |        85.2 |        91.6 |
| random                              |      4.1 |       8.6 |      18.3 |      28.1 |        4.5 |         9.1 |        19   |        29.5 |
