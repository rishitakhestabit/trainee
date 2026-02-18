import joblib

obj = joblib.load("src/features/preprocessor.joblib")

print("TYPE:", type(obj))
print(obj)
