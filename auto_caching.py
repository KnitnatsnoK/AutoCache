import time
from collections import defaultdict
PRINT_AUTO_CACHE_TTIMES = True

def AutoCache(benchmark_inputs:int=5, runs_per_input:int=3, min_occurrences:int=2, max_benchmark_time:float=1.0):
    def decorator(func):
        class _AutoCacheWrapper:
            __slots__ = (
                "func", "cache", "use_cache", "benchmark_inputs",
                "runs_per_input", "min_occurrences", "max_benchmark_time", "benchmark_data",
                "valid_count", "total_benchmark_time", "disable"
            )

            def __init__(self):
                self.func = func
                self.cache = {}
                self.use_cache = None
                self.benchmark_inputs = benchmark_inputs
                self.runs_per_input = runs_per_input
                self.min_occurrences = min_occurrences
                self.max_benchmark_time = max_benchmark_time
                self.benchmark_data = defaultdict(lambda: [0.0, 0.0, 0])  # [no_cache, with_cache, count]
                self.valid_count = 0
                self.total_benchmark_time = 0.0
                self.disable = False

            def set_cache_enabled(self, enabled: bool):
                self.disable = not enabled

            def __call__(self, *args, **kwargs):
                if self.disable:
                    return self.func(*args, **kwargs)

                key = (args, frozenset(kwargs.items()))

                if self.use_cache is None:
                    self._benchmark(key, args, kwargs)
                    if self.valid_count >= self.benchmark_inputs or self.total_benchmark_time >= self.max_benchmark_time:
                        self._finalize_cache_decision()

                if self.use_cache and key in self.cache:
                    return self.cache[key]

                result = self.func(*args, **kwargs)
                if self.use_cache:
                    self.cache[key] = result
                return result

            def _benchmark(self, key, args, kwargs):
                data = self.benchmark_data[key]

                # No-cache time
                t0 = time.perf_counter()
                for _ in range(self.runs_per_input):
                    self.func(*args, **kwargs)
                no_cache_time = time.perf_counter() - t0
                data[0] += no_cache_time

                # With-cache time
                self.cache.clear()
                t0 = time.perf_counter()
                for _ in range(self.runs_per_input):
                    if key in self.cache:
                        self.cache[key]
                    else:
                        self.cache[key] = self.func(*args, **kwargs)
                with_cache_time = time.perf_counter() - t0
                data[1] += with_cache_time

                data[2] += 1
                if data[2] == self.min_occurrences:
                    self.valid_count += 1

                self.total_benchmark_time += no_cache_time + with_cache_time

            def _finalize_cache_decision(self):
                if self.use_cache is not None:
                    return
                total_no_cache = 0.0
                total_with_cache = 0.0

                for no_cache, with_cache, count in self.benchmark_data.values():
                    if count > self.min_occurrences:
                        total_no_cache += no_cache
                        total_with_cache += with_cache
                if PRINT_AUTO_CACHE_TTIMES:
                    print(self.func)
                    print(f"Total No Cache Time: {total_no_cache:.6f}s")
                    print(f"Total With Cache Time: {total_with_cache:.6f}s")
                self.use_cache = total_with_cache < total_no_cache

        return _AutoCacheWrapper()
    return decorator


# Example usage: Fibonacci sequence
if __name__ == "__main__":
    @AutoCache(benchmark_inputs=10)
    def fibonacci(x:int) -> int:
        if x <= 1:
            return x
        return fibonacci(x - 1) + fibonacci(x - 2)

    NUM = 10

    fibonacci.set_cache_enabled(True)
    st = time.perf_counter()
    print(fibonacci(NUM))
    print(f"With cache: {time.perf_counter()-st:.2f}s")
    print("Actually using cache:", fibonacci.use_cache) # None means it has still not decided (not received enough unique inputs)
    print()

    fibonacci.set_cache_enabled(False)
    st = time.perf_counter()
    print(fibonacci(NUM))
    print(f"Without cache: {time.perf_counter()-st:.2f}s")
