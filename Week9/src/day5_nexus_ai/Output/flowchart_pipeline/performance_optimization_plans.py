class PerformanceOptimizationPlan:
    def __init__(self, plan_name):
        self.plan_name = plan_name
        self.optimizations = []

    def add_optimization(self, optimization):
        self.optimizations.append(optimization)

    def __str__(self):
        return f'Performance Optimization Plan: {self.plan_name}'

class Optimization:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

# Create performance optimization plan
aws_data_lake_optimization_plan = PerformanceOptimizationPlan('AWS Data Lake Optimization Plan')

# Create optimizations
data_compression = Optimization('Data Compression')
partitioning = Optimization('Partitioning')
spot_instances = Optimization('Spot Instances')

# Add optimizations to plan
aws_data_lake_optimization_plan.add_optimization(data_compression)
aws_data_lake_optimization_plan.add_optimization(partitioning)
aws_data_lake_optimization_plan.add_optimization(spot_instances)

# Print performance optimization plan
print('Performance Optimization Plan:')
print(aws_data_lake_optimization_plan)
for optimization in aws_data_lake_optimization_plan.optimizations:
    print(f'- {optimization}')