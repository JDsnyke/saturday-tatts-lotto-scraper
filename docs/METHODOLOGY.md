# Methodology

## 1. What can and cannot be improved

Saturday Lotto draws six winning numbers from 45. A standard six-number entry therefore represents one of `C(45,6) = 8,145,060` possible winning combinations. In a fair draw, every one of those combinations has the same Division 1 probability.

Historical results are useful for data-quality auditing and for describing realised variation. They are not a defensible basis for assigning higher next-draw probability to a number because it is hot, cold, overdue, recently drawn or historically paired with another number.

The v2 project therefore removes the previous weighted-frequency recommendation score.

## 2. Descriptive diagnostics

For a particular number, the probability of appearing among the six winning numbers in one draw is `6/45`.

Across `n` independent draws, the count for that number can be modelled marginally as a binomial random variable with:

- expected count: `n × 6/45`
- variance: `n × (6/45) × (39/45)`
- z-score: `(observed - expected) / sqrt(variance)`

The dashboard also reports:

- normalized entropy of the 45 observed main-number counts;
- a Pearson-style χ² distance from equal counts as a descriptive diagnostic;
- historical pair counts and their lift versus the expected pair co-occurrence count.

These are diagnostics, not forecasts. The within-draw counts are dependent because exactly six numbers are selected, so the project deliberately avoids turning the displayed χ² statistic into a simplistic p-value.

## 3. Multi-ticket coverage

If you buy `n` **distinct** standard entries, exactly `n` of the `8,145,060` possible Division 1 combinations are covered. The Division 1 probability is therefore `n / 8,145,060`.

Coverage mode does not alter this probability. Instead, it makes a multi-ticket set less internally redundant by greedily prioritising:

1. numbers used least often in the current ticket set;
2. candidate numbers that repeat the fewest previously used number pairs;
3. lower overlap with previously selected tickets as a tie-break consideration.

The result is a more even portfolio of combinations, not a more likely individual ticket.

## 4. Data validation

Before analysis, the loader checks that:

- every row contains the expected number of columns;
- dates are ISO-formatted and unique;
- all numbers are integers from 1 to 45;
- numbers within each main/supplementary set are unique;
- main and supplementary numbers do not overlap for a draw;
- winning and supplementary files contain exactly the same set of draw dates.

The canonical writer sorts draws newest-first, eliminating the old date-range bug caused by assuming an append order.
