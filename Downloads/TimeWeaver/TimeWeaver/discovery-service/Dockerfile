FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /workspace
COPY . .
RUN mvn -q -DskipTests -pl discovery-service -am package

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /workspace/discovery-service/target/discovery-service-*.jar app.jar
EXPOSE 8761
ENTRYPOINT ["java","-jar","/app/app.jar"]
