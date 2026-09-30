
### pythia-1.4b-deduped_W256 — natural: % of local→full loss gap recovered (gap = 0.195 nats/token)

| policy                               |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:-------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                 |      9.7 |      19.6 |      36.3 |      51.1 |       12.6 |        25.3 |        45   |        60.6 |
| familiarity head (7 scalars)         |     19.3 |      31   |      47.7 |      59.7 |       22.5 |        34.8 |        52.1 |        65   |
| familiarity rule (no training)       |     17.1 |      29.8 |      45.5 |      57.6 |       20.5 |        32.8 |        49.1 |        62.2 |
| learned head (hidden + familiarity)  |     24.5 |      38.6 |      56.2 |      65.8 |       27.5 |        41.7 |        59.4 |        69.3 |
| learned head (hidden only, ablation) |     21.2 |      33   |      47.6 |      59   |       23.1 |        36.8 |        51.5 |        62.9 |
| oracle KL (needs full pass)          |     46.5 |      62.3 |      76.9 |      84.8 |       52.5 |        68.6 |        83.3 |        90.1 |
| random                               |      3.5 |       7.1 |      16   |      26.1 |        4.2 |         9   |        18.9 |        28.9 |

### pythia-1.4b-deduped_W256 — prose: % of local→full loss gap recovered (gap = 0.260 nats/token)

| policy                               |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:-------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                 |      6.3 |      14.5 |      29.2 |      44.8 |        9.3 |        20   |        38.1 |        54.1 |
| familiarity head (7 scalars)         |     18.3 |      31.1 |      46.9 |      57.6 |       22.1 |        35.3 |        52.1 |        63.4 |
| familiarity rule (no training)       |     17   |      30.2 |      45.9 |      57.5 |       20.1 |        33   |        49.5 |        62.9 |
| learned head (hidden + familiarity)  |     20   |      32.8 |      50.6 |      61.4 |       22.4 |        36   |        53.7 |        64.4 |
| learned head (hidden only, ablation) |     14.2 |      25.5 |      40.1 |      53.2 |       15.3 |        28.8 |        43.9 |        56.5 |
| oracle KL (needs full pass)          |     39.9 |      57   |      73.5 |      82.5 |       46   |        63.4 |        79.7 |        87.3 |
| random                               |      3.3 |       6.8 |      15.5 |      25.5 |        3.7 |         8.7 |        18.2 |        28   |

### pythia-1.4b-deduped_W256 — code: % of local→full loss gap recovered (gap = 0.136 nats/token)

| policy                               |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:-------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                 |     15.6 |      28.5 |      48.5 |      62   |       18.2 |        34.5 |        56.9 |        71.8 |
| familiarity head (7 scalars)         |     21   |      30.8 |      49   |      63.4 |       23.3 |        33.9 |        52.1 |        67.9 |
| familiarity rule (no training)       |     17.4 |      29.2 |      44.8 |      57.7 |       21.1 |        32.4 |        48.4 |        61   |
| learned head (hidden + familiarity)  |     32.3 |      48.6 |      65.8 |      73.3 |       36.2 |        51.6 |        69.2 |        77.7 |
| learned head (hidden only, ablation) |     33.3 |      45.8 |      60.4 |      68.9 |       36.7 |        50.4 |        64.7 |        73.8 |
| oracle KL (needs full pass)          |     57.9 |      71.4 |      82.8 |      88.7 |       63.7 |        77.6 |        89.4 |        94.8 |
| random                               |      3.7 |       7.7 |      16.9 |      27.1 |        5   |         9.5 |        20.1 |        30.6 |

### pythia-1.4b-deduped_W256 — prose_ids: % of local→full loss gap recovered (gap = 0.261 nats/token)

| policy                               |   e2e@5% |   e2e@10% |   e2e@20% |   e2e@30% |   indep@5% |   indep@10% |   indep@20% |   indep@30% |
|:-------------------------------------|---------:|----------:|----------:|----------:|-----------:|------------:|------------:|------------:|
| entropy (local pass)                 |      5.4 |      13.1 |      28   |      43.6 |        8.2 |        18.2 |        36.6 |        52.7 |
| familiarity head (7 scalars)         |     21.9 |      36.5 |      50.3 |      60.7 |       25.8 |        40   |        54.3 |        65   |
| familiarity rule (no training)       |     20.7 |      34.9 |      50   |      59.8 |       24   |        37.8 |        53.6 |        64.1 |
| learned head (hidden + familiarity)  |     19.3 |      32.8 |      50.9 |      63.5 |       23.2 |        37.2 |        53.6 |        65.3 |
| learned head (hidden only, ablation) |     12.7 |      22.7 |      38.8 |      50   |       14.6 |        26.4 |        42.5 |        52.7 |
| oracle KL (needs full pass)          |     42.6 |      58.4 |      74.7 |      82.8 |       48.3 |        63.3 |        79.5 |        86.7 |
| random                               |      4.1 |       7.7 |      15.9 |      26.9 |        5   |         9.6 |        19.3 |        30.1 |
