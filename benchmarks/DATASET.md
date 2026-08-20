# Benchmark dataset policy

The built-in benchmark is a small deterministic smoke-test corpus. It verifies that metric generation is reproducible; it does **not** establish production detection accuracy.

Before publishing a TPR, FPR, precision, recall, or accuracy claim, add a versioned external corpus with documented source permissions, ground-truth labels, class balance, preprocessing, detector configurations, and an independent test split. Keep the corpus hash and full command line with every result.
