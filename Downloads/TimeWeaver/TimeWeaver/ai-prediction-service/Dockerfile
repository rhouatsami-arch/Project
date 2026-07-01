FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /workspace
COPY . .
RUN mvn -q -DskipTests -pl ai-prediction-service -am package

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /workspace/ai-prediction-service/target/ai-prediction-service-*.jar app.jar
EXPOSE 8082
ENTRYPOINT ["java","-jar","/app/app.jar"]
