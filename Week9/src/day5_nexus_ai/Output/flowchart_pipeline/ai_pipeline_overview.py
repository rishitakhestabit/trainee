class AIStage:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class AIStageSequence:
    def __init__(self):
        self.stages = []

    def add_stage(self, stage):
        self.stages.append(stage)

    def __str__(self):
        return ' -> '.join(str(stage) for stage in self.stages)

# Create AI pipeline stages
data_ingestion = AIStage('Data Ingestion')
data_preprocessing = AIStage('Data Preprocessing')
model_training = AIStage('Model Training')
model_deployment = AIStage('Model Deployment')
model_monitoring = AIStage('Model Monitoring')

# Create AI pipeline sequence
ai_pipeline = AIStageSequence()
ai_pipeline.add_stage(data_ingestion)
ai_pipeline.add_stage(data_preprocessing)
ai_pipeline.add_stage(model_training)
ai_pipeline.add_stage(model_deployment)
ai_pipeline.add_stage(model_monitoring)

# Print AI pipeline overview
print('AI Pipeline Overview:')
print(ai_pipeline)