FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /workspace
COPY . .
RUN mvn -q -DskipTests -pl notification-service -am package

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /workspace/notification-service/target/notification-service-*.jar app.jar
EXPOSE 8083
ENTRYPOINT ["java","-jar","/app/app.jar"]
