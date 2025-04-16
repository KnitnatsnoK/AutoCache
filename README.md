# AutoCache
#### A Python decotator that automatically decides if the function should use caching for a function or not.

### Usage:
The `AutoCache`-class should be used for functions that receive an input which returns a specific output in form of a `return` statement. 
It is used as a decorator, but must be called like this: `@AutoCache()` and not like this: `AutoCache`.  
After some usage of the function, the `AutoCache` will automatically decide if it's better to use caching or not.
After deciding, it will use either caching for all future computations or just call the function like it would be normally.

### The way it works:
The `AutoCache` has few inputs to control the decision:  
- `benchmark_inputs`: Controls how many function calls with unique inputs are needed to decide. (How many benchmarks are needed)
- `runs_per_input`: Controls how many test_calls are made for each input before deciding. (For more accurate performance measurement)
- `min_occurences`: Controls how many of the same input are needed for the input to be accounted for. (Caching needs to have had at least one occurence of the same input before caching can be used and therefore is worth it)
- `max_benchmark_time`: Controls how long the benchmarking before deciding can take at max (in seconds).
