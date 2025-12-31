package com.timeweaver.timetracking;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@SpringBootApplication
@EnableFeignClients
public class TimeTrackingServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(TimeTrackingServiceApplication.class, args);
    }
}
