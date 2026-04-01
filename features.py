from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression

# 1. Create Spark session
spark = SparkSession.builder.appName("BigData-ML").getOrCreate()

# 2. Load CSV data
data = spark.read.csv("bigdata.csv", header=True, inferSchema=True)

# 3. Convert columns to features vector
assembler = VectorAssembler(
    inputCols=["area", "bedrooms", "age"],
    outputCol="features"
)

final_data = assembler.transform(data).select("features", "price")

# 4. Train Linear Regression model
lr = LinearRegression(featuresCol="features", labelCol="price")
model = lr.fit(final_data)

# 5. Predict
predictions = model.transform(final_data)

# 6. Show predictions
predictions.show(689)

# 7. Stop Spark session
spark.stop()