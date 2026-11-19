# Tests for core/simulator.py. Phase 1.
#
# Cases:
#   - fixed seed gives identical output on repeated runs
#   - simulated mean and selected quantiles agree with ProbabilityCalculator within a stated
#     tolerance for flat and soft pity curves (large trial count, fixed seed)
#   - the hard pity cap is never exceeded
#   - progress_callback is called a bounded number of times and ends at (trials, trials)
#   - non-positive trials raises the domain exception
