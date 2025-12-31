FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /workspace
COPY . .
RUN mvn -q -DskipTests -pl time-tracking-service -am package

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /workspace/time-tracking-service/target/time-tracking-service-*.jar app.jar
EXPOSE 8084
ENTRYPOINT ["java","-jar","/app/app.jar"]
