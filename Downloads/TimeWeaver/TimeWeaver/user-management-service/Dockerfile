FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /workspace
COPY . .
RUN mvn -q -DskipTests -pl user-management-service -am package

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /workspace/user-management-service/target/user-management-service-*.jar app.jar
EXPOSE 8081
ENTRYPOINT ["java","-jar","/app/app.jar"]
