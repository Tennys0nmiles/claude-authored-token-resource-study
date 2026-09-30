
### pythia-160m-deduped_W64 — natural: % of local→full loss gap recovered (gap = 0.534 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |      9.1 |      17.6 |      32.3 |      46.2 |       10.9 |        20.9 |        37.2 |        52.1 |
| familiarity head (7 scalars)        |     16.2 |      27.1 |      41.7 |      53.9 |       18.6 |        29.8 |        45.3 |        57.6 |
| familiarity rule (no training)      |     14.5 |      23.9 |      39.3 |      51.2 |       17.4 |        26.9 |        42.1 |        54.3 |
| learned head (hidden + familiarity) |     21.2 |      33.5 |      51.3 |      63.2 |       22.4 |        35.8 |        53.9 |        66.2 |
| oracle KL (needs full pass)         |     33.7 |      49.5 |      66   |      76   |       37.8 |        54.9 |        72.7 |        82.3 |
| random                              |      4.4 |       9.1 |      19   |      28.9 |        4.7 |        10   |        20.4 |        30.7 |

### pythia-160m-deduped_W64 — prose: % of local→full loss gap recovered (gap = 0.542 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |      6.6 |      13.7 |      27   |      40.5 |        8.2 |        16.4 |        31.4 |        45.5 |
| familiarity head (7 scalars)        |     13.9 |      25   |      38.9 |      51.2 |       16.8 |        28.1 |        42.9 |        55.5 |
| familiarity rule (no training)      |     13.1 |      23.3 |      38.7 |      50   |       15.6 |        26.1 |        41.3 |        53.6 |
| learned head (hidden + familiarity) |     20.1 |      31.8 |      49   |      60   |       21.7 |        34   |        51.5 |        63.1 |
| oracle KL (needs full pass)         |     32.6 |      47.2 |      63   |      73.4 |       36.3 |        52.1 |        68.4 |        78.5 |
| random                              |      4.5 |       8.8 |      18.3 |      28.2 |        5   |        10.1 |        20.5 |        30.6 |

### pythia-160m-deduped_W64 — code: % of local→full loss gap recovered (gap = 0.528 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |     11.3 |      21.3 |      37.1 |      51.5 |       13.4 |        25.1 |        42.6 |        58.2 |
| familiarity head (7 scalars)        |     18.4 |      29.1 |      44.4 |      56.4 |       20.3 |        31.4 |        47.4 |        59.5 |
| familiarity rule (no training)      |     15.8 |      24.5 |      40   |      52.4 |       19   |        27.5 |        42.9 |        55   |
| learned head (hidden + familiarity) |     22.2 |      35.1 |      53.3 |      66.2 |       23   |        37.4 |        56.1 |        69.2 |
| oracle KL (needs full pass)         |     34.8 |      51.5 |      68.7 |      78.4 |       39.2 |        57.6 |        76.6 |        85.8 |
| random                              |      4.3 |       9.4 |      19.6 |      29.6 |        4.4 |         9.9 |        20.3 |        30.8 |

### pythia-160m-deduped_W64 — prose_ids: % of local→full loss gap recovered (gap = 0.670 nats/token)

| policy                              |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                |      6.3 |      13   |      25.5 |      38.6 |        7   |        14.7 |        28.4 |        41.7 |
| familiarity head (7 scalars)        |     17.1 |      29.8 |      44.2 |      54.6 |       19.1 |        31.9 |        46.4 |        56.9 |
| familiarity rule (no training)      |     18.2 |      29.5 |      44.9 |      54.3 |       19.7 |        31.1 |        46.3 |        56.2 |
| learned head (hidden + familiarity) |     21.1 |      32.6 |      49.1 |      60.5 |       21.4 |        33.6 |        50.5 |        61.8 |
| oracle KL (needs full pass)         |     34   |      49.5 |      65.7 |      76   |       36.6 |        53.4 |        70   |        80.4 |
| random                              |      4.5 |       9   |      18.5 |      28   |        5   |        10   |        19.4 |        29.2 |
